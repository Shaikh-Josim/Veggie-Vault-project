import time, timeit
from uuid import UUID
from typing import Iterable
import json
import os, sys
import hashlib
from collections.abc import Iterator
from typing import Any


from django.utils import timezone
from django.db import transaction

from base.models import LogLocation, LogIndex, LogFile
from base.helpers import get_file_prefix_fingerprint


class LogReader:

    json_obj_indices = []
    indexes:dict[str, list[list[int]]] = {}

    def lstrip_and_position(self, s: str):
        return len(s)- len(s.lstrip()), s.lstrip()

    def _read_json_logs(self, log_file_path: str, chunk_size: int = 10, start_read_position: int = 0) -> Iterator[tuple[dict[str, Any], int, int, list[list[int]] ]]:
        byte_read = start_read_position
        decoder = json.JSONDecoder()
        buffer = ""
        total_file_size_byte = os.path.getsize(log_file_path)
        start_position = start_read_position; length = 0; pending_whitespaces = 0; 
        json_obj_indices = []
        
        with open(log_file_path, "r", encoding="utf-8", newline='') as file:
            file.seek(start_read_position)
            while  chunk := file.read(chunk_size):
                byte_read += len(chunk.encode("utf-8"))
                if not chunk:
                    break

                buffer += chunk

                while buffer:
                    # Remove whitespace before the next JSON object.
                    spaces, buffer = self.lstrip_and_position(buffer)
                    if spaces != 0:
                        pending_whitespaces += spaces

                    if not buffer:
                        break

                    try:
                        log, end = decoder.raw_decode(buffer)
                        start_position = start_position + length + pending_whitespaces
                        length = end
                        json_obj_indices.append([start_position, end]) if not [start_position, end] in json_obj_indices else json_obj_indices
                        pending_whitespaces = 0

                        print(log, start_position, length)

                    except json.JSONDecodeError as e:
                        
                        if byte_read < total_file_size_byte:
                            break #continue reading next chunk until whole file is read

                        elif byte_read == total_file_size_byte:
                            print("Reached End Of File....")
                            break
                        else:
                            raise 

                    if not isinstance(log, dict):
                        raise ValueError("Log record is not a JSON object")

                    yield log, start_position, length, json_obj_indices
                    

                    # Remove the JSON object we just processed.
                    buffer = buffer[end:]
        print("file-size:", total_file_size_byte)
        print("byte-read:", byte_read)

        # if buffer has some data in it, but whole file has already been read..
        buffer = buffer.strip()
        if buffer:
            # log "there still some data in buffer unprocessed still waiting to be decoded"
            raise ValueError(
                "Incomplete JSON found at the end of the log file"
            )


    def linear_search_log(self, log_file_path:str, attribute:str, target_value:str) -> list[dict[str, Any]]:
        logs_containing_target = []

        for log, _, _, j in self._read_json_logs(log_file_path):
            if log.get(attribute) == target_value:
                logs_containing_target.append(log)
        print(j)
        return logs_containing_target

    def read_specific_log_in_file(self, log_file_path:str, start_position:int, length:int) -> dict[str, Any]:
        with open(log_file_path, "r", encoding="utf-8", newline='') as file:
            file.seek(start_position)
            jsonl_log = file.read(length)

            #print("start:", start_position)
            #print("length:", length)
            #print("repr:", repr(jsonl_log))
            
            try:
                log, end = json.JSONDecoder().raw_decode(jsonl_log)
                return log

            except Exception as e:
                print(e)
                return {}
            
    def get_json_obj_indeces(self, log_file_path:str):
        for _, _, _, json_obj_indices in self._read_json_logs(log_file_path):
            continue
        return json_obj_indices

    def read_all_logs(self, log_file_path:str)-> list[dict[str, Any]]:
        logs = []
        for log, _, _, _ in self._read_json_logs(log_file_path):
            logs.append(log)
        return logs
        
    def create_index(self, log_file_path:str, indexing_attribute: str = 'request_id'):
        indexes = {}

        for log, start_position, length, _ in self._read_json_logs(log_file_path):
            if indexing_attribute in log.keys():
                attribute_val = log.get(indexing_attribute)
                if attribute_val not in indexes.keys():
                    indexes[attribute_val] = [] 

                if [start_position, length] not in indexes[attribute_val]:
                    indexes[attribute_val].append([start_position, length])
        print('index: ',indexes)
        self.indexes = indexes #use file later instead of memory

    def search_log_using_indexing(self, log_file_path:str, target_value:str = ''):
        logs_containing_target = []

        indices = self.indexes.get(target_value)
        for start_position, length in indices: #type:ignore
            log = self.read_specific_log_in_file(log_file_path, start_position, length)
            logs_containing_target.append(log)
        
        return logs_containing_target

    def read_log_using_db(self, locations:Iterable[LogLocation]):
        reader = LogReader()
        logs = []
        for location in list(locations):
            logs.append(reader.read_specific_log_in_file(location.log_file.path, location.start_position, location.length))

        return logs    


    def create_index_in_db(self, log_file_id:UUID, indexing_attributes: list[str] = ['request_id'], start_read_position: int = 0,):
        log_file = LogFile.objects.get(uid = log_file_id)
        log_file_path = log_file.path

        for log, start_position, length, _ in self._read_json_logs(log_file_path, start_read_position= start_read_position):

            if not LogLocation.objects.filter(log_file = log_file, start_position = start_position, length = length).exists():
                location = LogLocation.objects.create(log_file = log_file, start_position = start_position, length = length)
            else:
                location = LogLocation.objects.get(log_file = log_file, start_position = start_position, length = length)

            for attribute_name in indexing_attributes:
                if attribute_name in log.keys() and not LogIndex.objects.filter(location = location, attribute_name = attribute_name, attribute_value = log.get(attribute_name)).exists():
                    LogIndex.objects.create(location = location, attribute_name = attribute_name, attribute_value= log.get(attribute_name))

    def search_log_using_db(self, attr_name_val:dict):
        location = LogLocation.objects.all()
        for attr_name, attr_val in attr_name_val.items():
            location = location.filter(indexes__attribute_name = attr_name, indexes__attribute_value = attr_val)

        return location.distinct()

    def sync_log_file(self, log_file_id: UUID, indexing_attributes: list[str]):

        log_file = LogFile.objects.get(uid=log_file_id)

        file_size = os.path.getsize(log_file.path)
        file_modified_at = timezone.datetime.fromtimestamp(os.path.getmtime(log_file.path),tz=timezone.get_current_timezone())

        print("file-size", file_size, "file_modified_at", file_modified_at)
        print("log_file_file-size", log_file.file_size, "log_file_file_modified_at", log_file.file_modified_at, "finger-print", log_file.file_fingerprint)

        if (log_file.file_size == file_size and log_file.file_modified_at == file_modified_at ):
            return

        elif not log_file.file_size and not log_file.file_modified_at and not log_file.file_fingerprint:
            self.create_index_in_db(log_file_id= log_file_id, indexing_attributes= indexing_attributes)

        elif (file_size > log_file.file_size):
            file_fingerprint = get_file_prefix_fingerprint(log_file_path= log_file.path, size= log_file.file_size)
            print("File Content Same:", file_fingerprint==log_file.file_fingerprint)

            if file_fingerprint == log_file.file_fingerprint:
                self.create_index_in_db(log_file_id= log_file_id, indexing_attributes= indexing_attributes, start_read_position= log_file.file_size)        

            else:
                self.rebuild_log_index(log_file_id, indexing_attributes)
                    #raise ValueError("File content changed. Rebuild required.")
        
        elif (file_size < log_file.file_size):
            self.rebuild_log_index(log_file_id, indexing_attributes)

        elif file_size == log_file.file_size:
            file_fingerprint = get_file_prefix_fingerprint(log_file_path= log_file.path, size= log_file.file_size)
            if file_fingerprint != log_file.file_fingerprint:
                self.rebuild_log_index(log_file_id, indexing_attributes)

        log_file.file_size = file_size
        log_file.file_modified_at = file_modified_at

        hasher = hashlib.sha256()

        with open(log_file.path, "rb") as file:
            while chunk := file.read(8192):
                hasher.update(chunk)

        file_fingerprint = hasher.hexdigest()

        print(file_fingerprint)
        log_file.file_fingerprint = file_fingerprint
        log_file.save()

    def rebuild_log_index(self, log_file_id: UUID, indexing_attributes: list[str]):
        log_file = LogFile.objects.get(uid=log_file_id)
        with transaction.atomic():
            print(len(log_file.locations.all())) #type:ignore
            log_file.locations.all().delete() #type:ignore
            print(len(log_file.locations.all())) #type:ignore
            self.create_index_in_db(log_file_id= log_file_id, indexing_attributes= indexing_attributes)


        

        

if __name__ == '__main__':

    reader = LogReader()
