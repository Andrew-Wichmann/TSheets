import logging
import os
import requests
from datetime import datetime
from dateutil import relativedelta
from time import sleep

from django.conf import settings
from django.core.management.base import BaseCommand
import sentry_sdk

from Timesheets.models import (
    ManualTimesheet,
    RegularTimesheet,
    TSheetsUser,
    JobCode,
    TimesheetEntry,
)
from TSheetsAutomation.utils import create_model_from_dict
from jobdiva.models import Candidate


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--start_date", type=str)
        parser.add_argument("--end_date", type=str)

    def handle(self, *args, **options):
        logger = logging.getLogger("management")
        url = "https://rest.tsheets.com/api/v1/timesheets"

        querystring = {
            "start_date": options["start_date"],
            "end_date": options["end_date"],
            "on_the_clock": "no",
            "per_page": 50,
            "page": 1,
        }

        def get_token():
            return os.environ["TSHEETS_TOKEN"]

        headers = {"Authorization": f"Bearer {get_token()}"}

        more = True
        while more:
            response = requests.request("GET", url, headers=headers, params=querystring)
            if response.status_code != 200:
                if response.status_code == 429:  # Too Many Requests
                    sleep(5 * 60)  # Sleep for 5 minutes
                else:
                    response.raise_for_status()
            response = response.json()
            for user in response.get("supplemental_data", {}).get("users", {}).values():
                tsheets_user = create_model_from_dict(TSheetsUser, user)
                jobdiva_user = Candidate.objects.filter(
                    email=user["email"].lower()
                ).first()
                if jobdiva_user:
                    logger.error(
                        f'Jobdiva Candidate {user["email"]} not found while loading tsheets models'
                    )
                    sentry_sdk.capture_message(
                        f'Jobdiva Candidate {user["email"]} not found while loading tsheets models'
                    )
                    continue
                else:
                    jobdiva_user.tsheets_user = tsheets_user
                    jobdiva_user.save()

            for jobcode in response["supplemental_data"].get("jobcodes", {}).values():
                create_model_from_dict(JobCode, jobcode)

            timesheets = response["results"]["timesheets"].values()
            logger.info(f"Found {len(timesheets)} timesheets")
            for timesheet in timesheets:
                _type = timesheet.pop("type")
                if _type == "regular":
                    model_obj = create_model_from_dict(RegularTimesheet, timesheet)
                elif _type == "manual":
                    model_obj = create_model_from_dict(ManualTimesheet, timesheet)
                next_sunday = relativedelta.relativedelta(weekday=relativedelta.SU(1))
                timesheet_entry, _ = TimesheetEntry.objects.get_or_create(
                    weekendingdate=(
                        datetime.strptime(model_obj.date, "%Y-%m-%d") + next_sunday
                    ).date(),
                    user=model_obj.user,
                )
                model_obj.timesheet_entry = timesheet_entry
                model_obj.save()
            more = bool(response["more"])
            querystring.update({"page": querystring["page"] + 1})
