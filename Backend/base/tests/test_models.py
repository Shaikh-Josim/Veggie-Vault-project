from pathlib import Path
import logging
from typing import Iterable
from django.test import TestCase

from base.models import LogFile, LogIndex, LogLocation
from try_programs.p1 import LogReader

logger = logging.getLogger("base")

# run test with
# python .\manage.py test <app-name>.<test-folder>.<test-file-name>
# $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest --debug-mode

class LogModelTest(TestCase):
    

    def setUp(self) -> None:
        """Initializes testing records across required database tables."""

        log_dir = Path("try_programs")
        files = list(log_dir.glob("*.jsonl"))

        for file in files:
            LogFile.objects.create(path = file.as_posix())

        indexes = [[0, 108], [110, 109], [221, 107], [330, 114], [446, 109], [557, 88], [647, 110], [759, 107]]

        self.log_file  = LogFile.objects.get(path = r"try_programs/django_errors.log.jsonl")

        for start_position, length in indexes:
            ...
            #LogLocation.objects.create(log_file = self.log_file, start_position = start_position, length = length)

        attr_name_val: dict[str,dict[str, list[list[int]]]] = {'request_id': 
                            {'req-001': [[0, 108], [221, 107], [759, 107]], 'req-002': [[110, 109], [446, 109]], 'req-003': [[330, 114]], 'req-004': [[557, 88]], 'req-005': [[647, 110]]},

                         'user_id':{'user-101': [[0, 108], [221, 107], [557, 88], [759, 107]], 'user-102': [[110, 109],
                         [446, 109]], 'user-103': [[330, 114]], 'user-104': [[647, 110]]}
                        }

        self.create_index_in_db(log_file_path= self.log_file.path, indexing_attributes=['request_id', 'user_id'])
        
        """
        for attrname in attr_name_val.keys():
            print(attrname)
            for attrval in attr_name_val.get(attrname).keys(): #type:ignore
                for start_position, length in attr_name_val.get(attrname).get(attrval): #type:ignore
                    location = LogLocation.objects.get(start_position = start_position, length = length)
                    LogIndex.objects.create(location = location, attribute_name = attrname, attribute_value= attrval)"""

        logs_indexes = LogIndex.objects.all()
        for index in logs_indexes:
            print(index, ' ', index.location)
        print(len(logs_indexes))

        self.log_location = LogLocation.objects.get(start_position = indexes[0][0], length = indexes[0][1])
        self.log_index = LogIndex.objects.get(location = self.log_location, attribute_name = list(attr_name_val.keys())[0],attribute_value = list(attr_name_val.get(list(attr_name_val.keys())[0]).keys())[0]) #type:ignore

        
    def create_index_in_db(self, log_file_path:str, indexing_attributes: list[str] = ['request_id']):
        reader = LogReader()

        for log, start_position, length, _ in reader._read_json_logs(log_file_path):

            if not LogLocation.objects.filter(log_file = self.log_file, start_position = start_position, length = length).exists():
                location = LogLocation.objects.create(log_file = self.log_file, start_position = start_position, length = length)
            else:
                location = LogLocation.objects.get(log_file = self.log_file, start_position = start_position, length = length)

            for attribute_name in indexing_attributes:
                if attribute_name in log.keys() and not LogIndex.objects.filter(location = location, attribute_name = attribute_name, attribute_value = log.get(attribute_name)).exists():
                    LogIndex.objects.create(location = location, attribute_name = attribute_name, attribute_value= log.get(attribute_name))

        
    
    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_str_representation --debug-mode    
    def test_str_representation(self):
        logger.info("\n---------- STR REPRESENTATION LOGFILE, LOGLOCATION, LOGINDEX MODEL TEST----------")
        self.assertEqual(str(self.log_file), "logfile-path try_programs/django_errors.log.jsonl")
        self.assertEqual(str(self.log_index), "attribute_name: request_id, attribute_value: req-001")
        self.assertEqual(str(self.log_location), "start-position: 0, length: 108")
        print(' TEST PASSED SUCCESSFULLY!!')        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_search_log_using_db --debug-mode    
    def test_search_log_using_db(self):
        logger.info("\n---------- SEARCH LOG USING DB TEST----------")
        attr_name_val = {'request_id': 'req-001', 'user_id': 'user-101'}
        locations =self.search_log_using_db(attr_name_val)

        self.assertEqual(len(locations), 3)
        print(' TEST PASSED SUCCESSFULLY!!')        



    def search_log_using_db(self, attr_name_val:dict):
        location = LogLocation.objects.all()
        for attr_name, attr_val in attr_name_val.items():
            location = location.filter(indexes__attribute_name = attr_name, indexes__attribute_value = attr_val)

        return location.distinct()

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_read_log_using_db --debug-mode    
    def test_read_log_using_db(self):
        logger.info("\n---------- READ LOG USING DB TEST----------")
        attr_name_val = {"request_id": "req-001", "user_id": "user-101"}
        attr_name_val = {"request_id": "req-001"}

        locations = self.search_log_using_db(attr_name_val)
        logs = self.read_log_using_db(locations)

        self.assertEqual(len(logs), 3)

        for log in logs:
            self.assertEqual(log["request_id"], "req-001")
            self.assertEqual(log["user_id"], "user-101")

        attr_name_val = {"request_id": "req-999"}
        attr_name_val = {"request_id": "req-002", "user_id": "user-101"}
        
        locations = self.search_log_using_db(attr_name_val)
        logs = self.read_log_using_db(locations)
        self.assertEqual(len(logs), 0)
        print(' TEST PASSED SUCCESSFULLY!!')        

        self.test_read_log_using_db_single_condition()
        self.test_read_log_using_db_non_exists_condition()
        self.test_read_log_using_db_unmatched_multiple_conditions()
        self.test_search_log_using_db_multiple_conditions()


    def test_read_log_using_db_single_condition(self):
        logger.info("\n---------- READ LOG USING DB WITH SINGLE CONDITION TEST----------")
        attr_name_val = {"request_id": "req-001"}

        locations = self.search_log_using_db(attr_name_val)
        logs = self.read_log_using_db(locations)

        self.assertEqual(len(logs), 3)

        for log in logs:
            self.assertEqual(log["request_id"], "req-001")
        print(' TEST PASSED SUCCESSFULLY!!')        


    def test_read_log_using_db_non_exists_condition(self):
        logger.info("\n---------- READ LOG USING DB WITH NON EXIST CONDITION TEST----------")
        attr_name_val = {"request_id": "req-999"}

        locations = self.search_log_using_db(attr_name_val)
        logs = self.read_log_using_db(locations)

        self.assertEqual(len(logs), 0)
        print(' TEST PASSED SUCCESSFULLY!!')        
        

    def test_read_log_using_db_unmatched_multiple_conditions(self):
        logger.info("\n---------- READ LOG USING DB WITH UNMATCHED MULTIPLE CONDITION TEST----------")
        attr_name_val = {"request_id": "req-002", "user_id": "user-101"}
        
        locations = self.search_log_using_db(attr_name_val)
        logs = self.read_log_using_db(locations)
        self.assertEqual(len(logs), 0)
        print(' TEST PASSED SUCCESSFULLY!!')        


    def test_search_log_using_db_multiple_conditions(self):
        logger.info("\n---------- READ LOG USING DB WITH MULTIPLE CONDITION TEST----------")
        attr_name_val = {
            "request_id": "req-001",
            "user_id": "user-101",
        }

        locations = self.search_log_using_db(attr_name_val)
        logs = self.read_log_using_db(locations)

        self.assertEqual(len(logs), 3)

        for log in logs:
            self.assertEqual(log["request_id"], "req-001")
            self.assertEqual(log["user_id"], "user-101")
        print(' TEST PASSED SUCCESSFULLY!!')        

    def read_log_using_db(self, locations:Iterable[LogLocation]):
        reader = LogReader()
        logs = []
        for location in list(locations):
            logs.append(reader.read_specific_log_in_file(location.log_file.path, location.start_position, location.length))

        return logs
            
            

    

            
                
            

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_log_obj_values --debug-mode    
    def test_log_obj_values(self):
        logger.info("\n---------- Order OBJ VALUES MODEL TEST----------")

        """self.assertEqual(self.order.amount, 500)
        self.assertEqual(self.order.razorpay_order_id, 'order_1')
        self.assertEqual(self.order.order_status, 'paid')
        self.assertEqual(self.order.payment_mode, 'offline')"""
        
        print(' TEST PASSED SUCCESSFULLY!!')        
    
