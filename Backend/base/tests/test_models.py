from pathlib import Path
import logging
from typing import Iterable
from unittest.mock import patch

from django.test import TestCase

from base.models import LogFile, LogIndex, LogLocation
from base.log_reader import LogReader

logger = logging.getLogger("base")

# run test with
# python .\manage.py test <app-name>.<test-folder>.<test-file-name>
# $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest --debug-mode

class LogModelTest(TestCase):
    

    def setUp(self) -> None:
        """Initializes testing records across required database tables."""

        log_dir = Path("try_programs")
        files = list(log_dir.glob("*.jsonl"))
        self.reader = LogReader()

        for file in files:
            LogFile.objects.create(path = file.as_posix())

        self.indexes = [[0, 108], [110, 109], [221, 107], [330, 114], [446, 109], [557, 88], [647, 110], [759, 107]]

        self.attr_name_val: dict[str,dict[str, list[list[int]]]] = {'request_id': 
                            {'req-001': [[0, 108], [221, 107], [759, 107]], 'req-002': [[110, 109], [446, 109]], 'req-003': [[330, 114]], 'req-004': [[557, 88]], 'req-005': [[647, 110]]},

                         'user_id':{'user-101': [[0, 108], [221, 107], [557, 88], [759, 107]], 'user-102': [[110, 109],
                         [446, 109]], 'user-103': [[330, 114]], 'user-104': [[647, 110]]}
                        }
        
        self.log_file  = LogFile.objects.get(path = r"try_programs/django_errors.log.jsonl")

        #self.reader.create_index_in_db(log_file_id= self.log_file.uid, indexing_attributes=['request_id', 'user_id'])

        #self.log_location = LogLocation.objects.get(start_position = indexes[0][0], length = indexes[0][1])
        #self.log_index = LogIndex.objects.get(location = self.log_location, attribute_name = list(attr_name_val.keys())[0],attribute_value = list(attr_name_val.get(list(attr_name_val.keys())[0]).keys())[0]) #type:ignore

            
    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_str_representation --debug-mode    
    def test_str_representation(self):
        logger.info("\n---------- STR REPRESENTATION LOGFILE, LOGLOCATION, LOGINDEX MODEL TEST----------")

        self.reader.create_index_in_db(log_file_id=self.log_file.uid, indexing_attributes=["request_id", "user_id"])
        self.log_location = LogLocation.objects.get(start_position = self.indexes[0][0], length = self.indexes[0][1])
        self.log_index = LogIndex.objects.get(location = self.log_location, attribute_name = list(self.attr_name_val.keys())[0],attribute_value = list(self.attr_name_val.get(list(self.attr_name_val.keys())[0]).keys())[0]) #type:ignore

        self.assertEqual(str(self.log_file), "logfile-path try_programs/django_errors.log.jsonl")
        self.assertEqual(str(self.log_index), "attribute_name: request_id, attribute_value: req-001")
        self.assertEqual(str(self.log_location), "start-position: 0, length: 108")
        print(' TEST PASSED SUCCESSFULLY!!')        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_search_log_using_db --debug-mode    
    def test_search_log_using_db(self):
        logger.info("\n---------- SEARCH LOG USING DB TEST----------")

        self.reader.create_index_in_db(log_file_id=self.log_file.uid, indexing_attributes=["request_id", "user_id"])
        attr_name_val = {'request_id': 'req-001', 'user_id': 'user-101'}
        locations =self.reader.search_log_using_db(attr_name_val)

        self.assertEqual(len(locations), 3)
        print(' TEST PASSED SUCCESSFULLY!!')        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_read_log_using_db --debug-mode    
    def test_read_log_using_db(self):
        logger.info("\n---------- READ LOG USING DB TEST----------")

        self.reader.create_index_in_db(log_file_id=self.log_file.uid, indexing_attributes=["request_id", "user_id"])
        attr_name_val = {"request_id": "req-001", "user_id": "user-101"}
        attr_name_val = {"request_id": "req-001"}

        locations = self.reader.search_log_using_db(attr_name_val)
        logs = self.reader.read_log_using_db(locations)

        self.assertEqual(len(logs), 3)

        for log in logs:
            self.assertEqual(log["request_id"], "req-001")
            self.assertEqual(log["user_id"], "user-101")

        attr_name_val = {"request_id": "req-999"}
        attr_name_val = {"request_id": "req-002", "user_id": "user-101"}
        
        locations = self.reader.search_log_using_db(attr_name_val)
        logs = self.reader.read_log_using_db(locations)
        self.assertEqual(len(logs), 0)
        print(' TEST PASSED SUCCESSFULLY!!')        

        
        self.test_read_log_using_db_non_exists_condition()
        self.test_read_log_using_db_unmatched_multiple_conditions()
        self.test_search_log_using_db_multiple_conditions()

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_read_log_using_db_single_condition --debug-mode    
    def test_read_log_using_db_single_condition(self):
        logger.info("\n---------- READ LOG USING DB WITH SINGLE CONDITION TEST----------")

        self.reader.create_index_in_db(log_file_id=self.log_file.uid, indexing_attributes=["request_id", "user_id"])
        attr_name_val = {"request_id": "req-001"}

        locations = self.reader.search_log_using_db(attr_name_val)
        logs = self.reader.read_log_using_db(locations)

        self.assertEqual(len(logs), 3)

        for log in logs:
            self.assertEqual(log["request_id"], "req-001")
        print(' TEST PASSED SUCCESSFULLY!!')        


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_read_log_using_db_non_exists_condition --debug-mode    
    def test_read_log_using_db_non_exists_condition(self):
        logger.info("\n---------- READ LOG USING DB WITH NON EXIST CONDITION TEST----------")
        attr_name_val = {"request_id": "req-999"}

        locations = self.reader.search_log_using_db(attr_name_val)
        logs = self.reader.read_log_using_db(locations)

        self.assertEqual(len(logs), 0)
        print(' TEST PASSED SUCCESSFULLY!!')        
        
    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_read_log_using_db_unmatched_multiple_conditions --debug-mode    
    def test_read_log_using_db_unmatched_multiple_conditions(self):
        logger.info("\n---------- READ LOG USING DB WITH UNMATCHED MULTIPLE CONDITION TEST----------")
        attr_name_val = {"request_id": "req-002", "user_id": "user-101"}
        
        locations = self.reader.search_log_using_db(attr_name_val)
        logs = self.reader.read_log_using_db(locations)
        self.assertEqual(len(logs), 0)
        print(' TEST PASSED SUCCESSFULLY!!')        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_search_log_using_db_multiple_conditions --debug-mode    
    def test_search_log_using_db_multiple_conditions(self):
        logger.info("\n---------- READ LOG USING DB WITH MULTIPLE CONDITION TEST----------")

        self.reader.create_index_in_db(log_file_id=self.log_file.uid, indexing_attributes=["request_id", "user_id"])
        attr_name_val = {
            "request_id": "req-001",
            "user_id": "user-101",
        }

        locations = self.reader.search_log_using_db(attr_name_val)
        logs = self.reader.read_log_using_db(locations)

        self.assertEqual(len(logs), 3)

        for log in logs:
            self.assertEqual(log["request_id"], "req-001")
            self.assertEqual(log["user_id"], "user-101")
        print(' TEST PASSED SUCCESSFULLY!!')        


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_create_index_in_db_does_not_create_duplicates --debug-mode    
    def test_create_index_in_db_does_not_create_duplicates(self):
        logger.info("\n---------- CREATE INDEX IN DB DUPLICATE TEST ----------")

        self.reader.create_index_in_db(
            log_file_id= self.log_file.uid,
            indexing_attributes=["request_id", "user_id"],
        )

        self.assertEqual(LogLocation.objects.count(), 8)
        self.assertEqual(LogIndex.objects.count(), 16)

        print("TEST PASSED SUCCESSFULLY!!")

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_create_index_in_db --debug-mode    
    def test_create_index_in_db(self):
        logger.info("\n---------- CREATE INDEX IN DB TEST----------")
        self.reader.create_index_in_db(log_file_id=self.log_file.uid, indexing_attributes=["request_id", "user_id"])
        self.assertEqual(LogLocation.objects.count(), 8)
        self.assertEqual(LogIndex.objects.count(), 16)

        print(' TEST PASSED SUCCESSFULLY!!')        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_create_index_in_db_adds_new_attribute --debug-mode    
    def test_create_index_in_db_adds_new_attribute(self):
        logger.info("\n---------- CREATE INDEX IN DB NEW ATTRIBUTE TEST ----------")

        self.reader.create_index_in_db(log_file_id=self.log_file.uid, indexing_attributes=["request_id", "user_id"])
        LogIndex.objects.filter(attribute_name="user_id").delete()  

        self.assertEqual(LogLocation.objects.count(), 8)
        self.assertEqual(
            LogIndex.objects.filter(attribute_name="request_id").count(),
            8
        )
        self.assertEqual(
            LogIndex.objects.filter(attribute_name="user_id").count(),
            0
        )

        self.reader.create_index_in_db(
            log_file_id = self.log_file.uid,
            indexing_attributes=["user_id"],
        )

        self.assertEqual(
            LogIndex.objects.filter(attribute_name="request_id").count(),
            8
        )
        self.assertEqual(
            LogIndex.objects.filter(attribute_name="user_id").count(),
            8
        )

        print("TEST PASSED SUCCESSFULLY!!")

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_create_index_in_db_correct_mapping --debug-mode    
    def test_create_index_in_db_correct_mapping(self):
        logger.info("\n---------- CREATE INDEX IN DB MAPPING TEST ----------")

        self.reader.create_index_in_db(log_file_id=self.log_file.uid, indexing_attributes=["request_id", "user_id"])
        indexes = LogIndex.objects.filter( attribute_name="request_id", attribute_value="req-001").order_by("location__start_position")

        actual_positions = [
            [index.location.start_position, index.location.length]
            for index in indexes
        ]

        expected_positions = [
            [0, 108],
            [221, 107],
            [759, 107],
        ]

        self.assertEqual(actual_positions, expected_positions)

        print("TEST PASSED SUCCESSFULLY!!")

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_sync_log_file_unchanged --debug-mode    
    def test_sync_log_file_unchanged(self):
        logger.info("\n---------- SYNC LOG FILE TEST ----------")

        # First sync — initialize metadata and index the file
        self.reader.sync_log_file(log_file_id=self.log_file.uid, indexing_attributes=["request_id", "user_id"])

        # Second sync — file hasn't changed
        with patch.object(self.reader, "_read_json_logs") as mock_reader:
            self.reader.sync_log_file(log_file_id=self.log_file.uid, indexing_attributes=["request_id", "user_id"])

        mock_reader.assert_not_called()

        self.assertEqual(LogLocation.objects.count(), 8)
        self.assertEqual(LogIndex.objects.count(), 16)

        print("TEST PASSED SUCCESSFULLY!!")


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_sync_log_file_initializes_file_metadata --debug-mode    
    def test_sync_log_file_initializes_file_metadata(self):
        logger.info("\n---------- SYNC LOG FILE INITIALIZES FILE METADATA TEST ----------")
        self.reader.sync_log_file(self.log_file.uid, ["request_id", "user_id"])

        self.log_file.refresh_from_db() #type:ignore

        self.assertGreater(self.log_file.file_size, 0)
        self.assertIsNotNone(self.log_file.file_modified_at)
        self.assertIsNotNone(self.log_file.file_fingerprint)

        self.assertEqual(LogLocation.objects.count(), 8)
        self.assertEqual(LogIndex.objects.count(), 16)
        print("TEST PASSED SUCCESSFULLY!!")


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_sync_log_file_same_size_replacement --debug-mode        
    def test_sync_log_file_same_size_replacement(self):
        logger.info("\n---------- SYNC LOG FILE SAME SIZE REPLACEMENT TEST ----------")
        original_content = Path(self.log_file.path).read_bytes()

        try:
            # Initial indexing
            self.reader.sync_log_file(log_file_id=self.log_file.uid, indexing_attributes=["request_id"])

            self.assertEqual(LogLocation.objects.filter(log_file=self.log_file ).count(), 8 )

            # Replace one request_id while keeping file size unchanged
            with open(self.log_file.path, "r+", encoding="utf-8", newline="") as file:
                content = file.read()

                updated_content = content.replace('"req-001"', '"req-009"', 1)
                self.assertEqual(len(content), len(updated_content))

                file.seek(0)
                file.write(updated_content)
                file.truncate()

            # Synchronize the modified file
            self.reader.sync_log_file(log_file_id=self.log_file.uid, indexing_attributes=["request_id"])

            # Verify locations remain unchanged
            self.assertEqual(LogLocation.objects.filter(log_file=self.log_file).count(), 8)

            # Verify updated indexes
            self.assertEqual(self.reader.search_log_using_db({"request_id": "req-001"}).count(), 2)
            self.assertEqual(self.reader.search_log_using_db({"request_id": "req-009"}).count(), 1)

        finally:
            # Restore the original file
            Path(self.log_file.path).write_bytes(original_content)
            print("TEST PASSED SUCCESSFULLY!!")


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_sync_log_file_larger_replacement --debug-mode
    def test_sync_log_file_larger_replacement(self):
        logger.info("\n---------- SYNC LOG FILE LARGER REPLACEMENT TEST ----------")
        original_content = Path(self.log_file.path).read_bytes()

        try:
            # Initial indexing
            self.reader.sync_log_file(log_file_id=self.log_file.uid, indexing_attributes=["request_id"])

            self.assertEqual(LogLocation.objects.filter(log_file=self.log_file).count(), 8)

            # Replace content with a longer value
            with open(self.log_file.path, "r+", encoding="utf-8", newline="") as file:
                content = file.read()
                updated_content = content.replace('"req-001"', '"req-009-longer-value"', 1,)

                self.assertGreater(len(updated_content), len(content))

                file.seek(0)
                file.write(updated_content)
                file.truncate()

            # Synchronize the modified file
            self.reader.sync_log_file(log_file_id=self.log_file.uid, indexing_attributes=["request_id"],)

            # Verify locations remain unchanged in count
            self.assertEqual(LogLocation.objects.filter(log_file=self.log_file).count(), 8)

            # Verify updated indexes
            self.assertEqual(self.reader.search_log_using_db({"request_id": "req-001"}).count(), 2)

            self.assertEqual(self.reader.search_log_using_db({"request_id": "req-009-longer-value"}).count(), 1)

            print("TEST PASSED SUCCESSFULLY!!")

        finally:
            Path(self.log_file.path).write_bytes(original_content)    


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_sync_log_file_appended --debug-mode
    def test_sync_log_file_appended(self):
        logger.info("\n---------- SYNC LOG FILE APPENDED TEST ----------")

        original_content = Path(self.log_file.path).read_bytes()

        try:
            # Initial indexing
            self.reader.sync_log_file(log_file_id=self.log_file.uid, indexing_attributes=["request_id"],)

            self.assertEqual(LogLocation.objects.filter(log_file=self.log_file).count(), 8)

            # Append a new log record
            appended_log = (
                '\n{"request_id":"req-006",'
                '"user_id":"user-105",'
                '"order_id":"ord-508",'
                '"level":"INFO",'
                '"message":"New order"}'
            )

            with open(self.log_file.path,"a",encoding="utf-8",newline="") as file:
                file.write(appended_log)

            # Synchronize the appended file
            self.reader.sync_log_file(log_file_id=self.log_file.uid, indexing_attributes=["request_id"])

            # Verify 9 total locations
            self.assertEqual(LogLocation.objects.filter(log_file=self.log_file).count(),9)

            # Verify the appended record was indexed
            self.assertEqual(self.reader.search_log_using_db({"request_id": "req-006"}).count(), 1)

            # Verify existing records remain unchanged
            self.assertEqual(self.reader.search_log_using_db({"request_id": "req-001"}).count(), 3)

            print("TEST PASSED SUCCESSFULLY!!")

        finally:
            Path(self.log_file.path).write_bytes(original_content)


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_sync_log_file_smaller_replacement --debug-mode


    def test_sync_log_file_smaller_replacement(self):
        logger.info("\n---------- SYNC LOG FILE SMALLER REPLACEMENT TEST ----------")

        original_content = Path(self.log_file.path).read_bytes()

        try:
            # Initial indexing
            self.reader.sync_log_file(log_file_id=self.log_file.uid, indexing_attributes=["request_id"])

            self.assertEqual(LogLocation.objects.filter(log_file=self.log_file).count(), 8)

            # Remove the first log record
            with open(self.log_file.path, "r", encoding="utf-8", newline="") as file:
                content = file.read()

            first_record_end = content.index("\n") + 1
            updated_content = content[first_record_end:]

            self.assertLess(len(updated_content), len(content))

            Path(self.log_file.path).write_text(updated_content, encoding="utf-8", newline="")

            # Synchronize the modified file
            self.reader.sync_log_file(log_file_id=self.log_file.uid, indexing_attributes=["request_id"],)

            # Verify 7 remaining locations
            self.assertEqual(LogLocation.objects.filter(log_file=self.log_file).count(), 7)

            # Verify removed record is no longer indexed
            self.assertEqual(self.reader.search_log_using_db({"request_id": "req-001"}).count(), 2)

            # Verify other records remain indexed
            self.assertEqual(self.reader.search_log_using_db({"request_id": "req-002"}).count(), 2)

            print("TEST PASSED SUCCESSFULLY!!")

        finally:
            Path(self.log_file.path).write_bytes(original_content)


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_sync_log_file_empty --debug-mode
    def test_sync_log_file_empty(self):
        logger.info("\n---------- SYNC LOG FILE EMPTY TEST ----------")

        original_content = Path(self.log_file.path).read_bytes()

        try:
            # Initial indexing
            self.reader.sync_log_file(log_file_id=self.log_file.uid, indexing_attributes=["request_id"])

            self.assertEqual(LogLocation.objects.filter(log_file=self.log_file).count(), 8)

            # Empty the physical log file
            Path(self.log_file.path).write_bytes(b"")

            # Synchronize the empty file
            self.reader.sync_log_file(log_file_id=self.log_file.uid, indexing_attributes=["request_id"])

            # Verify all locations were deleted
            self.assertEqual(LogLocation.objects.filter(log_file=self.log_file).count(), 0)

            # Verify file metadata
            self.log_file.refresh_from_db()

            self.assertEqual(self.log_file.file_size, 0)

            self.assertIsNone(self.log_file.file_fingerprint)

            print("TEST PASSED SUCCESSFULLY!!")

        finally:
            Path(self.log_file.path).write_bytes(original_content)


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_sync_log_file_whitespace_only --debug-mode


    def test_sync_log_file_whitespace_only(self):
        logger.info("\n---------- SYNC LOG FILE WHITESPACE ONLY TEST ----------")

        original_content = Path(self.log_file.path).read_bytes()

        try:
            # Initial indexing
            self.reader.sync_log_file(log_file_id=self.log_file.uid, indexing_attributes=["request_id"])

            self.assertEqual(LogLocation.objects.filter(log_file=self.log_file).count(), 8)

            # Replace the file content with whitespace
            Path(self.log_file.path).write_text("\n\n   \n\t  \n", encoding="utf-8",)

            # Synchronize the whitespace-only file
            self.reader.sync_log_file(log_file_id=self.log_file.uid, indexing_attributes=["request_id"])

            # Verify all locations were deleted
            self.assertEqual(LogLocation.objects.filter(log_file=self.log_file).count(), 0)

            # Verify physical file size is retained
            self.log_file.refresh_from_db()

            self.assertEqual(self.log_file.file_size, Path(self.log_file.path).stat().st_size)

            self.assertIsNone(self.log_file.file_fingerprint,)

            print("TEST PASSED SUCCESSFULLY!!")

        finally:
            Path(self.log_file.path).write_bytes(original_content)


    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_sync_log_file_indexing_failure --debug-mode
    def test_sync_log_file_indexing_failure(self):
        logger.info("\n---------- SYNC LOG FILE INDEXING FAILURE TEST ----------")

        original_content = Path(self.log_file.path).read_bytes()

        try:
            # Initial indexing
            self.reader.sync_log_file(log_file_id=self.log_file.uid, indexing_attributes=["request_id"],)

            self.log_file.refresh_from_db()

            original_file_size = self.log_file.file_size
            original_fingerprint = self.log_file.file_fingerprint
            original_location_count = LogLocation.objects.filter(log_file=self.log_file).count()

            # Append a valid record followed by malformed JSON
            appended_content = (
                '\n{"request_id":"req-006",'
                '"user_id":"user-105",'
                '"level":"INFO",'
                '"message":"Valid record"}'
                '\n{"request_id":'
            )

            with open(self.log_file.path, "a", encoding="utf-8", newline="") as file:
                file.write(appended_content)

            # Indexing should fail
            with self.assertRaises(ValueError):
                self.reader.sync_log_file(log_file_id=self.log_file.uid, indexing_attributes=["request_id"],)

            # Metadata should remain unchanged
            self.log_file.refresh_from_db()

            self.assertEqual(self.log_file.file_size, original_file_size)

            self.assertEqual(self.log_file.file_fingerprint, original_fingerprint)

            # Existing locations should remain unchanged
            self.assertEqual(LogLocation.objects.filter(log_file=self.log_file).count(), original_location_count)

            # The partially indexed record should not exist
            self.assertEqual(self.reader.search_log_using_db({"request_id": "req-006"}).count(), 0)

            print("TEST PASSED SUCCESSFULLY!!")

        finally:
            Path(self.log_file.path).write_bytes(original_content)