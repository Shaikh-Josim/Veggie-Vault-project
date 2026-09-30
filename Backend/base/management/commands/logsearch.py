import json

from django.core.management.base import BaseCommand, CommandError

from base.models import LogFile
from base.log_reader import LogReader


def parse_filters(filters):
    parsed_filters = {}

    for filter_value in filters:
        try:
            key, value = filter_value.split("=", maxsplit=1)
            key, value = key.strip(), value.strip()
        except ValueError:
            raise ValueError("Invalid filter format. Use key=value.") from None

        if not key or not value:
            raise ValueError(
                "Filter key and value cannot be empty."
            )

        if key in parsed_filters:
            raise ValueError(
                f"Duplicate filter key: {key}"
            )

        parsed_filters[key] = value

    return parsed_filters


def parse_indent(indent):
    try:
        if indent is None:
            return
        
        parsed_indent = int(indent)
        if parsed_indent < 0:
            raise ValueError
    except ValueError as e:
        raise ValueError("Invalid indent format. Use a Non-Negative Integer value.") from None
    
    return parsed_indent

def parse_limit(limit, logs):
    try:
        if limit is None:
            return len(logs)
        
        parsed_limit = int(limit)
        if parsed_limit < 0:
            raise ValueError("Invalid limit format. Use a Non-Negative Integer value.") from None

        if parsed_limit > len(logs):
            return len(logs)

    except ValueError as e:
        raise ValueError(e)
    
    return parsed_limit

class Command(BaseCommand):
    help = "Search indexed JSONL log files"


    def print_logs(self, logs):
        if self.quiet:
            """for i,log in enumerate(logs):
                self.stdout.write(json.dumps(log, indent=self.parsed_indent))"""
            for i in range(self.parsed_limit):
                self.stdout.write(json.dumps(logs[i-1], indent=self.parsed_indent))
        else:
            #self.stdout.write(f"Found log file: {self.log_file.path}")
            """for i,log in enumerate(logs):
                self.stdout.write(f'log {i+1}:')
                self.stdout.write(json.dumps(log, indent=self.parsed_indent), ending='\n--------\n')"""
            for i in range(self.parsed_limit):
                self.stdout.write(f'log {i+1}:')
                self.stdout.write(json.dumps(logs[i], indent=self.parsed_indent), ending='\n--------\n')

    def handle(self, *args, **options):
        file_path = options["file"]
        filters = options.get("filter", [])
        indent = options.get("indent")
        self.quiet = options.get("quiet")
        limit = options.get("limit")

        try:
            parsed_filters = parse_filters(filters)
        except ValueError as exc:
            raise CommandError(str(exc))


        try:
            self.parsed_indent = parse_indent(indent)
        except ValueError as exc:
            raise CommandError(str(exc))


        try:
            self.log_file = LogFile.objects.get(path=file_path)
        except LogFile.DoesNotExist:
            self.stderr.write(self.style.ERROR("Log file is not registered."))
            return

        if not self.quiet:
            self.stdout.write(f"Found log file: {self.log_file.path}")
        

        indexed_attributes = set(self.log_file.locations.values_list("indexes__attribute_name", flat=True)) #type:ignore

        for attribute in parsed_filters:
            if attribute not in indexed_attributes:
                self.stderr.write(self.style.ERROR(f"Filter attribute '{attribute}' is not indexed for this log file."))
                return

        reader = LogReader()

        locations = reader.search_log_using_db(parsed_filters)
        locations = locations.filter(log_file= self.log_file).order_by("start_position")

        try:
            logs = reader.read_log_using_db(locations)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Log file is missing from disk: {self.log_file.path}"))
            return

        if not logs:
            self.stdout.write("No matching logs found.")
            return

        try:
            self.parsed_limit = parse_limit(limit, logs)
        except ValueError as exc:
            raise CommandError(str(exc))

        self.print_logs(logs)
        


    def add_arguments(self, parser):
        parser.add_argument("--file", required=True, help="Path to the JSONL log file")
        parser.add_argument("--filter", action="append", default=[], help="Filter logs using key=value. Can be repeated.")
        parser.add_argument("--indent", default=None, help="Pretty-print JSON output with the specified indentation.")
        parser.add_argument("--quiet", action="store_true", help="Suppress informational output.")
        parser.add_argument("--limit", default=None, help="Limit.")
        


    