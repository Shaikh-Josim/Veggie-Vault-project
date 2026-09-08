from pathlib import Path
import logging
from typing import Iterable
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

        indexes = [[0, 108], [110, 109], [221, 107], [330, 114], [446, 109], [557, 88], [647, 110], [759, 107]]

        attr_name_val: dict[str,dict[str, list[list[int]]]] = {'request_id': 
                            {'req-001': [[0, 108], [221, 107], [759, 107]], 'req-002': [[110, 109], [446, 109]], 'req-003': [[330, 114]], 'req-004': [[557, 88]], 'req-005': [[647, 110]]},

                         'user_id':{'user-101': [[0, 108], [221, 107], [557, 88], [759, 107]], 'user-102': [[110, 109],
                         [446, 109]], 'user-103': [[330, 114]], 'user-104': [[647, 110]]}
                        }
        
        self.log_file  = LogFile.objects.get(path = r"try_programs/django_errors.log.jsonl")

        self.reader.create_index_in_db(log_file= self.log_file, indexing_attributes=['request_id', 'user_id'])

        self.log_location = LogLocation.objects.get(start_position = indexes[0][0], length = indexes[0][1])
        self.log_index = LogIndex.objects.get(location = self.log_location, attribute_name = list(attr_name_val.keys())[0],attribute_value = list(attr_name_val.get(list(attr_name_val.keys())[0]).keys())[0]) #type:ignore

            
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
        locations =self.reader.search_log_using_db(attr_name_val)

        self.assertEqual(len(locations), 3)
        print(' TEST PASSED SUCCESSFULLY!!')        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_read_log_using_db --debug-mode    
    def test_read_log_using_db(self):
        logger.info("\n---------- READ LOG USING DB TEST----------")
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

        self.test_read_log_using_db_single_condition()
        self.test_read_log_using_db_non_exists_condition()
        self.test_read_log_using_db_unmatched_multiple_conditions()
        self.test_search_log_using_db_multiple_conditions()

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_read_log_using_db_single_condition --debug-mode    
    def test_read_log_using_db_single_condition(self):
        logger.info("\n---------- READ LOG USING DB WITH SINGLE CONDITION TEST----------")
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
            log_file= self.log_file,
            indexing_attributes=["request_id", "user_id"],
        )

        self.assertEqual(LogLocation.objects.count(), 8)
        self.assertEqual(LogIndex.objects.count(), 16)

        print("TEST PASSED SUCCESSFULLY!!")

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_create_index_in_db --debug-mode    
    def test_create_index_in_db(self):
        logger.info("\n---------- CREATE INDEX IN DB TEST----------")
        self.assertEqual(LogLocation.objects.count(), 8)
        self.assertEqual(LogIndex.objects.count(), 16)

        print(' TEST PASSED SUCCESSFULLY!!')        

    # run this func test with
    # $env:PYTHONUNBUFFERED=1; python .\manage.py test base.tests.test_models.LogModelTest.test_create_index_in_db_adds_new_attribute --debug-mode    
    def test_create_index_in_db_adds_new_attribute(self):
        logger.info("\n---------- CREATE INDEX IN DB NEW ATTRIBUTE TEST ----------")

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
            log_file= self.log_file,
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

        indexes = LogIndex.objects.filter(
            attribute_name="request_id",
            attribute_value="req-001",
        ).order_by("location__start_position")

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