from datetime import datetime
import requests

from django.core.management.base import BaseCommand
from django.db.models.fields.related import ForeignKey
from Timesheets.models import (
    LoadTimesheets,
    ManualTimesheet,
    RegularTimesheet,
    TSheetsUser,
    JobCode,
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

            def create_model_objects(model, fields):
                def filter_unused_fields(model, fields):
                    captured_fields = []
                    for field in model._meta.get_fields():
                        if type(field) == ForeignKey:
                            captured_fields.append(field.name + "_id")
                        else:
                            captured_fields.append(field.name)
                    for discard in [
                        field for field in fields if field not in captured_fields
                    ]:
                        fields.pop(discard)
                    return fields

                def map_ids_to_models(model, fields):
                    id_field_to_model = {
                        "jobcode_id": JobCode,
                        "user_id": TSheetsUser,
                        "created_by_user_id": TSheetsUser,
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
                    return fields

                fields = filter_unused_fields(model, fields)
                fields = map_ids_to_models(model, fields)

                id = fields.pop("id")
                model.objects.update_or_create(id=id, defaults=fields)

            for user in response["supplemental_data"].get("users", {}).values():
                create_model_objects(TSheetsUser, user)

            for jobcode in response["supplemental_data"].get("jobcodes", {}).values():
                create_model_objects(JobCode, jobcode)

            for timesheet in response["results"]["timesheets"].values():
                _type = timesheet.pop("type")
                if _type == "regular":
                    create_model_objects(RegularTimesheet, timesheet)
                elif _type == "manual":
                    create_model_objects(ManualTimesheet, timesheet)
            # more = bool(response["more"])
            more = False

        LoadTimesheets().save()
