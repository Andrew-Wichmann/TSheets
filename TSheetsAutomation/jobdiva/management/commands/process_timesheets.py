import logging
from datetime import datetime

import sentry_sdk
from django.core.management.base import BaseCommand
from django.core import management

from Timesheets.models import TimesheetEntry
from jobdiva.models import ProcessTimesheetsRun


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger = logging.getLogger("management")
        logger.info("Start processing timesheets")

        start_date = (
            ProcessTimesheetsRun.objects.order_by("run_at")
            .last()
            .run_at.strftime("%Y-%m-%d")
        )
        end_date = datetime.now().strftime("%Y-%m-%d")

        logger.info("Loading TSheets timesheets and supplementary data")
        management.call_command(
            "load_tsheets_models", start_date=start_date, end_date=end_date
        )
        logger.info("Loading Jobdiva hires and supplementary data")
        management.call_command(
            "load_jobdiva_models", start_date=start_date, end_date=end_date
        )

        # NOTE: We can't use TimesheetEntry.objects.filter() here because .processed is a property of the TimesheetEntry class.
        # Ie. it's NOT a column that can be filtered on. Maybe the better way to do that would
        # be to put a .post_save hook on the Timesheet models and set the parent TimesheetEntry
        # field if all Timesheets are processed.
        for timesheet_entry in filter(
            lambda entry: not entry.processed, TimesheetEntry.objects.all()
        ):
            logger.info(
                f"Processing timesheets for {timesheet_entry.user.email} for the weekendingdate of {timesheet_entry.weekendingdate}"
            )
            processed = timesheet_entry.process()
            if not processed:
                sentry_sdk.capture_message(
                    f"Timesheet for {timesheet_entry.user.email} for the weekendingdate of {timesheet_entry.weekendingdate} not processed."
                )

        ProcessTimesheetsRun().save()
        logger.info("Finished processing timesheets")
