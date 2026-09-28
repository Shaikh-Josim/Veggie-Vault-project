from io import StringIO
import os
import logging
import json
import tempfile

from django.core.management import call_command, CommandError
from django.test import TestCase
from django.utils import timezone

from base.models import LogFile
from base.management.commands.logsearch import parse_filters
from base.log_reader import LogReader

logger = logging.getLogger("base")


class LogSearchCommandTest(TestCase):

    #helper function
    def create_test_log_file(self):
        records = [
            {"request_id": "req-001", "user_id": "user-101", "order_id": "ord-501", "level": "INFO", "message": "User logged in"},
            {"request_id": "req-002", "user_id": "user-102", "order_id": "ord-502", "level": "ERROR", "message": "Payment failed"},
            {"request_id": "req-001", "user_id": "user-101", "order_id": "ord-503", "level": "INFO", "message": "Order created"},
            {"request_id": "req-003", "user_id": "user-103", "order_id": "ord-504", "level": "WARNING", "message": "Stock running low"},
            {"request_id": "req-002", "user_id": "user-102", "order_id": "ord-505", "level": "INFO", "message": "Payment retried"},
            {"request_id": "req-004", "user_id": "user-101", "level": "INFO", "message": "Profile updated"},
            {"request_id": "req-005", "user_id": "user-104", "order_id": "ord-506", "level": "ERROR", "message": "Order cancelled"},
            {"request_id": "req-001", "user_id": "user-101", "order_id": "ord-507", "level": "INFO", "message": "Order shipped"},
        ]

        file = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
        self.file_path = file.name

        try:
            for record in records:
                file.write(json.dumps(record) + "\n")
        finally:
            file.close()

        return self.file_path

    def tearDown(self):
        if hasattr(self, "file_path") and os.path.exists(self.file_path):
            os.remove(self.file_path)
        super().tearDown()

    
    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_unregistered_file
    def test_unregistered_file(self):
        logger.info("\n--------- UNREGISTERED FILE TEST ----------")

        out = StringIO()
        err = StringIO()

        call_command(
            "logsearch",
            file="nonexistent.log.jsonl",
            stdout=out,
            stderr=err,
        )

        self.assertIn(
            "Log file is not registered.",
            err.getvalue(),
        )

        print("Unregistered file Test Passed Successfully!!")

    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_registered_file
    def test_registered_file(self):
        print("\n--------- REGISTERED FILE TEST ----------")

        file_path = self.create_test_log_file()

        LogFile.objects.create(
            path=file_path,
            file_modified_at=timezone.now(),
        )

        out = StringIO()
        err = StringIO()

        call_command(
            "logsearch",
            file=file_path,
            stdout=out,
            stderr=err,
        )

        self.assertIn(
            f"Found log file: {file_path}",
            out.getvalue(),
        )

        print("Registered file Test Passed Successfully!!")

    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_missing_file_argument
    def test_missing_file_argument(self):
        print("\n--------- MISSING FILE ARGUMENT TEST ----------")

        with self.assertRaises(CommandError):
            call_command("logsearch")

        print("Missing file argument Test Passed Successfully!!")


    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_parse_filters
    def test_parse_filters(self):
        print("\n--------- PARSE FILTERS TEST ----------")

        filters = ["level=ERROR", "user_id=user-102"]

        expected = {
            "level": "ERROR",
            "user_id": "user-102",
        }

        result = parse_filters(filters)

        self.assertEqual(result, expected)

        print("Parse filters Test Passed Successfully!!")


    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_invalid_filter_format
    def test_invalid_filter_format(self):
        print("\n--------- INVALID FILTER FORMAT TEST ----------")

        filters = ["level"]

        with self.assertRaisesRegex(ValueError, "Invalid filter format"):
            parse_filters(filters)

        print("Invalid filter format Test Passed Successfully!!")


    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_empty_filter_key_or_value
    def test_empty_filter_key_or_value(self):
        print("\n--------- EMPTY FILTER KEY OR VALUE TEST ----------")

        for filter_value in ["=ERROR", "level="]:
            with self.subTest(filter_value=filter_value):
                with self.assertRaisesRegex(
                    ValueError,
                    "Filter key and value cannot be empty.",
                ):
                    parse_filters([filter_value])

        print("Empty filter key or value Test Passed Successfully!!")


    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_duplicate_filter_key
    def test_duplicate_filter_key(self):
        print("\n--------- DUPLICATE FILTER KEY TEST ----------")

        filters = ["level=ERROR", "level=INFO"]

        with self.assertRaisesRegex(
            ValueError,
            "Duplicate filter key: level",
        ):
            parse_filters(filters)

        print("Duplicate filter key Test Passed Successfully!!")


    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_invalid_filter_command
    def test_invalid_filter_command(self):
        print("\n--------- INVALID FILTER COMMAND TEST ----------")

        with self.assertRaises(CommandError):
            call_command(
                "logsearch",
                file="nonexistent.log.jsonl",
                filter=["invalid-filter"],
            )

        print("Invalid filter command Test Passed Successfully!!")


    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_valid_filters_command
    def test_valid_filters_command(self):
        print("\n--------- VALID FILTER COMMAND TEST ----------")

        file_path = self.create_test_log_file()

        log_file = LogFile.objects.create(path=file_path, file_modified_at=timezone.now())
        LogReader().create_index_in_db(log_file.uid, indexing_attributes=["level", "user_id"])
        logger.debug("Index count: %s", log_file.locations.filter(indexes__attribute_name="level", indexes__attribute_value="ERROR").count())#type: ignore

        out = StringIO()
        err = StringIO()

        call_command(
            "logsearch",
            file=file_path,
            filter=["level=ERROR", "user_id=user-102"],
            stdout=out,
            stderr=err,
        )

        output = out.getvalue()

        self.assertIn("Found log file:", output)
        self.assertIn('"level": "ERROR"', output)
        self.assertIn('"user_id": "user-102"', output)

        print("Valid filter command Test Passed Successfully!!")


    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_no_matching_logs
    def test_no_matching_logs(self):
        print("\n--------- NO MATCHING LOGS TEST ----------")

        file_path = self.create_test_log_file()

        log_file = LogFile.objects.create(path=file_path, file_modified_at=timezone.now())

        LogReader().create_index_in_db(log_file.uid, indexing_attributes=["level", "user_id"],)

        out = StringIO()
        err = StringIO()

        call_command("logsearch", file=file_path, filter=["level=DEBUG"], stdout=out, stderr=err)

        output = out.getvalue()

        self.assertIn("No matching logs found.", output)

        print("No matching logs Test Passed Successfully!!")


    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_multiple_matching_logs
    def test_multiple_matching_logs(self):
        print("\n--------- MULTIPLE MATCHING LOGS TEST ----------")

        file_path = self.create_test_log_file()

        log_file = LogFile.objects.create(path=file_path, file_modified_at=timezone.now())

        LogReader().create_index_in_db(log_file.uid, indexing_attributes=["user_id"])

        out = StringIO()
        err = StringIO()

        call_command("logsearch", file=file_path, filter=["user_id=user-101"], stdout=out, stderr=err)

        output = out.getvalue()

        self.assertEqual(output.count('"user_id": "user-101"'), 4)

        print("Multiple matching logs Test Passed Successfully!!")


    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_json_output_validity
    def test_json_output_validity(self):
        print("\n--------- JSON OUTPUT VALIDITY TEST ----------")

        file_path = self.create_test_log_file()

        log_file = LogFile.objects.create(path=file_path, file_modified_at=timezone.now())

        LogReader().create_index_in_db(log_file.uid, indexing_attributes=["user_id"])

        out = StringIO()
        err = StringIO()

        call_command("logsearch", file=file_path, filter=["user_id=user-101"], stdout=out, stderr=err)

        output_lines = out.getvalue().splitlines()

        log_lines = [line for line in output_lines if line.startswith("{")]

        for line in log_lines:
            parsed_log = json.loads(line)

            self.assertIsInstance(parsed_log, dict)

        self.assertEqual(len(log_lines), 4)

        print("JSON output validity Test Passed Successfully!!")

     # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_whitespace_filter
    def test_whitespace_filter(self):
        print("\n--------- WHITESPACE FILTER TEST ----------")

        with self.assertRaisesRegex(ValueError,"Filter key and value cannot be empty."):
            parse_filters(["level=   "])

        print("Whitespace filter Test Passed Successfully!!")

    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_non_indexed_filter
    def test_non_indexed_filter(self):
        print("\n--------- NON-INDEXED FILTER TEST ----------")

        file_path = self.create_test_log_file()

        log_file = LogFile.objects.create(path=file_path, file_modified_at=timezone.now())

        LogReader().create_index_in_db(log_file.uid, indexing_attributes=["user_id"])

        out = StringIO()
        err = StringIO()

        call_command("logsearch",file=file_path, filter=["level=ERROR"], stdout=out, stderr=err)
        self.assertIn("Filter attribute 'level' is not indexed for this log file.", err.getvalue())

        print("Non-indexed filter Test Passed Successfully!!")


    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_whitespace_around_valid_filter
    def test_whitespace_around_valid_filter(self):
        print("\n--------- WHITESPACE VALID FILTER TEST ----------")

        parsed = parse_filters(["  level = ERROR  "])

        self.assertEqual(parsed, {"level": "ERROR"})

        print("Whitespace valid filter Test Passed Successfully!!")

    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_equals_in_filter_value
    def test_equals_in_filter_value(self):
        print("\n--------- EQUALS IN FILTER VALUE TEST ----------")

        parsed = parse_filters(["message=a=b"])

        self.assertEqual(parsed, {"message": "a=b"})

        print("Equals in filter value Test Passed Successfully!!")


    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_multiple_filters_with_non_indexed_attribute
    def test_multiple_filters_with_non_indexed_attribute(self):
        print("\n--------- MULTIPLE FILTERS NON-INDEXED TEST ----------")

        file_path = self.create_test_log_file()

        log_file = LogFile.objects.create(path=file_path, file_modified_at=timezone.now())

        LogReader().create_index_in_db(log_file.uid, indexing_attributes=["user_id"])

        out = StringIO()
        err = StringIO()

        call_command("logsearch", file=file_path, filter=["user_id=user-102", "level=ERROR"], stdout=out, stderr=err)

        self.assertIn("Filter attribute 'level' is not indexed for this log file.", err.getvalue())

        self.assertEqual(out.getvalue(), f"Found log file: {file_path}\n")

        print("Multiple filters non-indexed Test Passed Successfully!!")


    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_no_filters
    def test_no_filters(self):
        print("\n--------- NO FILTERS TEST ----------")

        file_path = self.create_test_log_file()

        log_file = LogFile.objects.create(path=file_path, file_modified_at=timezone.now())

        LogReader().create_index_in_db(log_file.uid, indexing_attributes=["user_id"])

        out = StringIO()
        err = StringIO()

        call_command("logsearch", file=file_path, stdout=out, stderr=err)

        output = out.getvalue()

        self.assertEqual(err.getvalue(), "")
        self.assertEqual(output.count('"user_id":'), 8)

        print("No filters Test Passed Successfully!!")


    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_result_order
    def test_result_order(self):
        print("\n--------- RESULT ORDER TEST ----------")

        file_path = self.create_test_log_file()

        log_file = LogFile.objects.create(path=file_path, file_modified_at=timezone.now())

        LogReader().create_index_in_db(log_file.uid, indexing_attributes=["user_id"])

        out = StringIO()
        err = StringIO()

        call_command("logsearch", file=file_path, filter=["user_id=user-101"], stdout=out, stderr=err)

        logs = [json.loads(line) for line in out.getvalue().splitlines() if line.startswith("{")]


        self.assertEqual([log["message"] for log in logs], ["User logged in", "Order created", "Profile updated", "Order shipped"])

        print("Result order Test Passed Successfully!!")


    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_registered_file_missing_from_disk
    def test_registered_file_missing_from_disk(self):
        print("\n--------- REGISTERED FILE MISSING TEST ----------")

        file_path = "try_programs/missing.log.jsonl"

        log_file = LogFile.objects.create(path=file_path, file_modified_at=timezone.now())

        location = log_file.locations.create(start_position=0, length=10) #type:ignore
        location.indexes.create(attribute_name="user_id", attribute_value="user-101")

        out = StringIO()
        err = StringIO()

        call_command("logsearch", file=file_path, filter=["user_id=user-101"], stdout=out, stderr=err)

        self.assertIn(f"Log file is missing from disk: {file_path}", err.getvalue())
        self.assertEqual(out.getvalue(), f"Found log file: {file_path}\n")

        print("Registered file missing Test Passed Successfully!!")

    # Run this test function with:
    # python manage.py test base.tests.test_logsearch_command.LogSearchCommandTest.test_stale_index
    def test_stale_index(self):
        print("\n--------- STALE INDEX TEST ----------")

        file = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
        self.file_path = file.name

        try:
            file.write('{"user_id":"user-101","message":"Original"}\n')
        finally:
            file.close()

        file_path = self.file_path

        log_file = LogFile.objects.create(path=file_path, file_modified_at=timezone.now())
        LogReader().create_index_in_db(log_file.uid, indexing_attributes=["user_id"])

        with open(file_path, "a", encoding="utf-8") as file:
            file.write('{"user_id":"user-101","message":"New"}\n')

        out = StringIO()
        err = StringIO()

        call_command("logsearch", file=file_path, filter=["user_id=user-101"], stdout=out, stderr=err)

        logs = [json.loads(line)for line in out.getvalue().splitlines() if line.startswith("{")]

        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["message"], "Original")

        print("Stale index Test Passed Successfully!!")