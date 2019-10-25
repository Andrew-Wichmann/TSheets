from django.db import models


DISCARDED_REGULARTIMESHEET_FIELDS = [
    "customfields",
    "attached_files",
    "created_by_user_id",
]

DISCARDED_MANUALTIMESHEET_FIELDS = [
    "customfields",
    "attached_files",
    "start",
    "end",
    "created_by_user_id",
]

DISCARDED_USER_FIELDS = [
    "group_id",
    "pto_balances",
    "manager_of_group_ids",
    "permissions",
    "customfields",
    "hire_date",
    "term_date",
    "payroll_id",
]

DISCARDED_JOBCODE_FIELDS = [
    "parent_id",
    "required_customfields",
    "filtered_customfielditems",
    "locations",
]


class User(models.Model):
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


class ManualTimesheet(models.Model):
    user = models.ForeignKey(
        User, related_name="manual_timesheet", on_delete=models.PROTECT
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


class RegularTimesheet(models.Model):
    user = models.ForeignKey(
        User, related_name="regular_timesheet", on_delete=models.PROTECT
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


class LoadTimesheets(models.Model):
    run_at = models.DateTimeField(auto_now=True)
