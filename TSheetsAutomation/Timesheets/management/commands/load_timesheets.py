from datetime import datetime
import requests

from django.core.management.base import BaseCommand
from Timesheets.models import (
    LoadTimesheets,
    ManualTimesheet,
    RegularTimesheet,
    User,
    JobCode,
    DISCARDED_REGULARTIMESHEET_FIELDS,
    DISCARDED_MANUALTIMESHEET_FIELDS,
    DISCARDED_JOBCODE_FIELDS,
    DISCARDED_USER_FIELDS,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        url = "https://rest.tsheets.com/api/v1/timesheets"

        # last_run = LoadTimesheets.objects.order_by("run_at").last().run_at
        querystring = {
            # "start_date": last_run.strftime("%Y-%m-%d"),
            "start_date": "2019-10-21",
            "end_date": datetime.now().strftime("%Y-%m-%d"),
            "on_the_clock": "no",
        }

        def get_token():
            with open("creds/tsheets_token", "r") as fd:
                return fd.readline()

        headers = {"Authorization": f"Bearer {get_token()}"}

        more = True
        while more:
            response = requests.request(
                "GET", url, headers=headers, params=querystring
            ).json()

            def create_model_objects(model, fields, discarded_fields):
                for field in discarded_fields:
                    fields.pop(field)
                id_field_to_model = {
                    "jobcode_id": JobCode,
                    "user_id": User,
                    "created_by_user_id": User,
                }
                foreign_fields = dict(
                    filter(lambda elem: elem[0].endswith("_id"), fields.items())
                )
                for foreign_key_field, foreign_key_id in foreign_fields.items():
                    fields.pop(foreign_key_field)
                    if foreign_key_id:
                        foreign_model = id_field_to_model[foreign_key_field]
                        fields[
                            foreign_key_field.split("_id")[0]
                        ] = foreign_model.objects.get(id=foreign_key_id)

                id = fields.pop("id")
                model.objects.update_or_create(id=id, defaults=fields)

            for user in response["supplemental_data"].get("users", {}).values():
                create_model_objects(User, user, DISCARDED_USER_FIELDS)

            for jobcode in response["supplemental_data"].get("jobcodes", {}).values():
                create_model_objects(JobCode, jobcode, DISCARDED_JOBCODE_FIELDS)

            for timesheet in response["results"]["timesheets"].values():
                type = timesheet.pop("type")
                if type == "regular":
                    create_model_objects(
                        RegularTimesheet, timesheet, DISCARDED_REGULARTIMESHEET_FIELDS
                    )
                elif type == "manual":
                    create_model_objects(
                        ManualTimesheet, timesheet, DISCARDED_MANUALTIMESHEET_FIELDS
                    )
            # more = bool(response["more"])
            more = False

        LoadTimesheets().save()
