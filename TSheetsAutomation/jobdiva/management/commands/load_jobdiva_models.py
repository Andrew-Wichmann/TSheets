import time
from datetime import date, datetime
from dateutil import relativedelta

from django.core.management.base import BaseCommand
from Timesheets.models import TSheetsUser
from jobdiva.models import Candidate, Job, Company, Hire
from jobdiva.client import BIDataClient
from TSheetsAutomation.utils import create_model_from_dict

DATETIME_STRING_FMT = "%Y-%m-%d"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--weeks_ago", type=int, default=1)

    def handle(self, *args, **options):
        sunday_ago = relativedelta.relativedelta(weekday=relativedelta.SU(-options["weeks_ago"]))
        sunday = (datetime.now() + sunday_ago).strftime(DATETIME_STRING_FMT)
        mondays_ago = relativedelta.relativedelta(weekday=relativedelta.MO(-(options["weeks_ago"])))
        monday = (datetime.now() - mondays_ago).strftime(DATETIME_STRING_FMT)
        biclient = BIDataClient()
        activities = biclient.get(
            "Submittal/Interview/Hire Activities List", from_string=monday, to_string=sunday
        )
        hires = []
        for activity in activities:
            if activity["HIREFLAG"] == "1":
                hires.append(activity)
        for hire in hires:
            candidate = biclient.get("Candidate Detail", parameters=hire["CANDIDATEID"])[0]
            tsheets_user = TSheetsUser.objects.filter(email=candidate["EMAIL"]).first()
            if tsheets_user:
                create_model_from_dict(
                    Candidate, {**candidate, "tsheets_user": tsheets_user}, id="ID"
                )
                job = biclient.get("Job Detail", parameters=hire["JOBID"])[0]
                create_model_from_dict(Job, job, id="ID")

                company = biclient.get("Company Detail", parameters=hire["COMPANYID"])[0]
                create_model_from_dict(Company, company, id="ID")
                create_model_from_dict(Hire, hire, id="ACTIVITYID")
            time.sleep(2)
