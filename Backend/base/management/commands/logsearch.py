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


class Command(BaseCommand):
    help = "Search indexed JSONL log files"

    def handle(self, *args, **options):
        file_path = options["file"]
        filters = options.get("filter", [])
        indent = options.get("indent")

        try:
            parsed_filters = parse_filters(filters)
        except ValueError as exc:
            raise CommandError(str(exc))

        try:
            parsed_indent = parse_indent(indent)
        except ValueError as exc:
            raise CommandError(str(exc))

        try:
            log_file = LogFile.objects.get(path=file_path)
        except LogFile.DoesNotExist:
            self.stderr.write(self.style.ERROR("Log file is not registered."))
            return
        self.stdout.write(f"Found log file: {log_file.path}")

        indexed_attributes = set(log_file.locations.values_list("indexes__attribute_name", flat=True)) #type:ignore
        for attribute in parsed_filters:
            if attribute not in indexed_attributes:
                self.stderr.write(self.style.ERROR(f"Filter attribute '{attribute}' is not indexed for this log file."))
                return

        reader = LogReader()

        locations = reader.search_log_using_db(parsed_filters)
        locations = locations.filter(log_file=log_file).order_by("start_position")

        try:
            logs = reader.read_log_using_db(locations)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Log file is missing from disk: {log_file.path}"))
            return

        if not logs:
            self.stdout.write("No matching logs found.")
            return

        for i,log in enumerate(logs):
            self.stdout.write(f'log {i+1}:')
            #self.stdout.write(json.dumps(log, indent=options["indent"]), ending='\n--------\n')
            self.stdout.write(json.dumps(log, indent=parsed_indent), ending='\n--------\n')
        


    def add_arguments(self, parser):
        parser.add_argument("--file", required=True, help="Path to the JSONL log file")
        parser.add_argument("--filter", action="append", default=[], help="Filter logs using key=value. Can be repeated.")
        parser.add_argument("--indent", default=None, help="Pretty-print JSON output with the specified indentation.")


    