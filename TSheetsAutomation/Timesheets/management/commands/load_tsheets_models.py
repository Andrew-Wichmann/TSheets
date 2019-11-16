import os
import requests
from datetime import datetime
from dateutil import relativedelta

from django.core.management.base import BaseCommand
from Timesheets.models import (
    LoadTimesheets,
    ManualTimesheet,
    RegularTimesheet,
    TSheetsUser,
    JobCode,
    TimesheetEntry,
)
from django.conf import settings
from TSheetsAutomation.utils import create_model_from_dict


class Command(BaseCommand):
    def handle(self, *args, **options):
        url = "https://rest.tsheets.com/api/v1/timesheets"

        import pdb;pdb.set_trace()
        last_run = LoadTimesheets.objects.order_by("run_at").last().run_at
        querystring = {
            "start_date": last_run.strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d"),
            "on_the_clock": "no",
            "per_page": 50,
            "page": 1,
        }

        def get_token():
            with open(os.path.join(settings.CREDENTIALS_FOLDER, "tsheets_token"), "r") as fd:
                return fd.readline().split("\n")[0]

        headers = {"Authorization": f"Bearer {get_token()}"}

        more = True
        while more:
            response = requests.request("GET", url, headers=headers, params=querystring).json()

            for user in response["supplemental_data"].get("users", {}).values():
                create_model_from_dict(TSheetsUser, user)

            for jobcode in response["supplemental_data"].get("jobcodes", {}).values():
                create_model_from_dict(JobCode, jobcode)

            for timesheet in response["results"]["timesheets"].values():
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

        LoadTimesheets().save()
