import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.db import models
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from jobdiva.client import JobDivaAPIClient, last_sunday_string


class TSheetsUser(models.Model):
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    active = models.BooleanField()
    employee_number = models.IntegerField()
    salaried = models.BooleanField()
    exempt = models.BooleanField()
    username = models.CharField(max_length=256)
    email = models.EmailField()
    email_verified = models.BooleanField()
    mobile_number = models.CharField(max_length=16)
    last_modified = models.DateTimeField()
    last_active = models.DateTimeField()
    created = models.DateTimeField()
    client_url = models.CharField(max_length=256)
    company_name = models.CharField(max_length=256)
    profile_image_url = models.URLField()
    submitted_to = models.DateField()
    approved_to = models.DateField()
    require_password_change = models.BooleanField()
    pay_rate = models.FloatField()
    pay_interval = models.CharField(
        max_length=256, choices=[("hour", "hour"), ("year", "year")]
    )


class JobCode(models.Model):
    # parent_id = models.ForeignKey("self", null=True)
    name = models.CharField(max_length=64)
    short_code = models.CharField(max_length=32)
    type = models.CharField(
        max_length=16,
        choices=[
            ("unpaid_break", "unpaid_break"),
            ("regular", "regular"),
            ("pto", "pto"),
            ("paid_break", "paid_break"),
        ],
    )
    billable = models.BooleanField()
    billable_rate = models.FloatField()
    has_children = models.BooleanField()
    assigned_to_all = models.BooleanField()
    active = models.BooleanField()
    last_modified = models.DateTimeField()
    created = models.DateTimeField()

    # class Meta:
    # 	unique_together = [("parent_id", "name"), ("parent_id", "short_code")]


class TimesheetEntry(models.Model):
    weekendingdate = models.DateTimeField()
    user = models.ForeignKey(TSheetsUser, on_delete=models.PROTECT)

    def process(self):
        from jobdiva.models import Hire, Candidate

        logger = logging.getLogger("management")
        timesheet_entries = []
        for date in [
            (self.weekendingdate - relativedelta(days=day)).date()
            for day in range(0, 7)
        ]:
            timesheets = list(
                filter(lambda timesheet: timesheet.date == date, self.timesheets)
            )
            hours = sum([timesheet.hours for timesheet in timesheets])

            timesheet_entries.append({"date": f"{date}T00:00:00", "hours": hours})

        try:
            candidate = self.timesheets[0].user.candidate
        except Candidate.DoesNotExist:
            logger.error("Do not have a Jobdiva user for this timesheet")
            return False

        hire = Hire.objects.filter(CANDIDATE=candidate).last()
        if not hire:
            logger.error("Do not have a Hire object for this user")
            return False
        else:

            payload = {
                "employeeid": self.user.candidate.ID,
                "jobid": hire.JOB.JOBDIVANO.replace("-", ""),
                "weekendingdate": self.weekendingdate.isoformat().split("+")[0],
                "approved": True,
                "TimesheetEntry": timesheet_entries,
            }
            logger.debug(f"mock upload timesheet {payload}")
            JobDivaAPIClient().uploadTimesheet(**payload)
            for timesheet in self.timesheets:
                timesheet.espo_processed = True
                timesheet.save()
        return True

    @property
    def timesheets(self):
        return list(self.manualtimesheet_set.all()) + list(
            self.regulartimesheet_set.all()
        )

    @property
    def processed(self):
        if all([timesheet.espo_processed for timesheet in self.timesheets]):
            return True
        else:
            return False


class ManualTimesheet(models.Model):
    user = models.ForeignKey(
        TSheetsUser, related_name="manual_timesheet", on_delete=models.PROTECT
    )
    jobcode = models.ForeignKey(JobCode, null=True, on_delete=models.PROTECT)
    date = models.DateField()
    duration = models.IntegerField()
    tz = models.IntegerField()
    tz_str = models.CharField(max_length=16)
    location = models.CharField(max_length=256)
    on_the_clock = models.BooleanField()
    locked = models.IntegerField()
    notes = models.TextField(max_length=2048)
    last_modified = models.DateTimeField()

    espo_processed = models.BooleanField(default=False)
    timesheet_entry = models.ForeignKey(
        TimesheetEntry, on_delete=models.PROTECT, null=True
    )

    @property
    def hours(self):
        return self.duration / 3600

    def process(self):
        self.espo_processed = True
        self.save()
        return True


class RegularTimesheet(models.Model):
    user = models.ForeignKey(
        TSheetsUser, related_name="regular_timesheet", on_delete=models.PROTECT
    )
    jobcode = models.ForeignKey(JobCode, null=True, on_delete=models.PROTECT)
    date = models.DateField()
    duration = models.IntegerField()
    tz = models.IntegerField()
    tz_str = models.CharField(max_length=16)
    location = models.CharField(max_length=256)
    on_the_clock = models.BooleanField()
    locked = models.IntegerField()
    notes = models.TextField(max_length=2048)
    last_modified = models.DateTimeField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    origin_hint = models.CharField(max_length=256, null=True)

    espo_processed = models.BooleanField(default=False)
    timesheet_entry = models.ForeignKey(
        TimesheetEntry, on_delete=models.PROTECT, null=True
    )

    @property
    def hours(self):
        return self.duration / 3600

    def process(self):
        # employeeid = 10947061895756
        # jobid = 19-00886
        timesheetentries = [
            {"date": f"{self.date.isoformat()}T00:00:00", "hours": self.duration}
            for _ in range(0, 7)
        ]
        # {"date": "2019-11-04T00:00:00", "hours": 30}, {"date": "2019-11-05T00:00:00", "hours": 30}, {"date": "2019-11-06T00:00:00", "hours": 30} ,{"date": "2019-11-07T00:00:00", "hours": 30}, {"date": "2019-11-08T00:00:00", "hours": 30}, {"date": "2019-11-09T00:00:00", "hours": 30}, {"date": "2019-11-10T00:00:00", "hours": 30}]
        # weekendingdate="2019-11-10T00:00:00"

        # self.espo_processed = True
        # bidata_client = BIDataClient()
        # bidata_client.getBIData(MetricName="Candidate Detail", parameters=None)
        # self.save()
        return True
