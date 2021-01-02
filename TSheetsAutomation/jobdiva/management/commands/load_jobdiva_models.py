import logging
import time
from datetime import date, datetime
from dateutil import relativedelta

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from Timesheets.models import TSheetsUser
from jobdiva.models import Candidate, Job, Company, Hire
from jobdiva.client import BIDataClient
from TSheetsAutomation.utils import create_model_from_dict

DATETIME_STRING_FMT = "%Y-%m-%d"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--start_date", type=str)
        parser.add_argument("--end_date", type=str)

    def handle(self, *args, **options):
        logger = logging.getLogger("management")
        biclient = BIDataClient()
        activities = biclient.get(
            "Submittal/Interview/Hire Activities List",
            from_string=options["start_date"],
            to_string=options["end_date"],
        )
        activities = list(filter(lambda x: x["HIREFLAG"] == "1", activities))
        logger.log(
            logging.INFO,
            f"Found {len(activities)} hire activities from {options['start_date']} to {options['end_date']}.",
        )
        for hire in activities:
            candidate = biclient.get(
                "Candidate Detail", parameters=hire["CANDIDATEID"]
            )[0]
            tsheets_user = TSheetsUser.objects.filter(email=candidate["EMAIL"]).first()
            if tsheets_user:
                logger.log(logging.INFO, f"Found tsheets user {candidate['EMAIL']} in jobdiva.")
                create_model_from_dict(
                    Candidate, {**candidate, "tsheets_user": tsheets_user}, id="ID"
                )

                company = biclient.get("Company Detail", parameters=hire["COMPANYID"])[
                    0
                ]
                create_model_from_dict(Company, company, id="ID")

                job = biclient.get("Job Detail", parameters=hire["JOBID"])[0]
                create_model_from_dict(Job, job, id="ID")
                create_model_from_dict(Hire, hire, id="ACTIVITYID")
            else:
                logger.warning(f"Did not find jobdiva candidate {candidate['EMAIL']} in our tsheets DB.")
            time.sleep(2)
