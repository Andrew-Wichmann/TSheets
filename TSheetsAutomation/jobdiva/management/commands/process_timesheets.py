import logging

from django.core.management.base import BaseCommand
from django.core import management

from Timesheets.models import TimesheetEntry


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger = logging.getLogger("management")

        logger.info("Loading TSheets timesheets and supplementary data")
        management.call_command("load_tsheets_models")
        logger.info("Loading Jobdiva hires and supplementary data")
        management.call_command("load_jobdiva_models")

        for timesheet_entry in filter(
            lambda entry: not entry.processed, TimesheetEntry.objects.all()
        ):
            logger.info(
                f"Processing timesheets for {timesheet_entry.user.email} for the weekendingdate of {timesheet_entry.weekendingdate}"
            )
            timesheet_entry.process()
