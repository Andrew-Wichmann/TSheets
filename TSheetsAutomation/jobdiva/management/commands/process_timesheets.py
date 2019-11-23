import logging
from datetime import datetime

from django.core.management.base import BaseCommand
from django.core import management

from Timesheets.models import TimesheetEntry
from jobdiva.models import ProcessTimesheetsRun


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger = logging.getLogger("management")

        start_date = ProcessTimesheetsRun.objects.order_by("run_at").last().run_at.strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

        logger.info("Loading TSheets timesheets and supplementary data")
        management.call_command("load_tsheets_models", start_date=start_date, end_date=end_date)
        logger.info("Loading Jobdiva hires and supplementary data")
        management.call_command("load_jobdiva_models", start_date=start_date, end_date=end_date)

        for timesheet_entry in filter(
            lambda entry: not entry.processed, TimesheetEntry.objects.all()
        ):
            logger.info(
                f"Processing timesheets for {timesheet_entry.user.email} for the weekendingdate of {timesheet_entry.weekendingdate}"
            )
            timesheet_entry.process()
        ProcessTimesheetsRun().save()
