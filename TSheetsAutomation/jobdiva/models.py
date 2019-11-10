from django.db import models
from Timesheets.models import TSheetsUser


class ParentCompany(models.Model):
    name = models.CharField(max_length=255)


class Company(models.Model):
    ID = models.CharField(primary_key=True, max_length=64)
    COMPANYNAME = models.CharField(max_length=255)
    parent_company = models.ForeignKey(ParentCompany, on_delete=models.PROTECT, null=True)


class Candidate(models.Model):
    ID = models.CharField(primary_key=True, max_length=64)
    tsheets_user = models.OneToOneField(TSheetsUser, on_delete=models.CASCADE)
    FIRSTNAME = models.CharField(max_length=255)
    LASTNAME = models.CharField(max_length=255)
    EMAIL = models.EmailField()


class Job(models.Model):
    ID = models.CharField(primary_key=True, max_length=64)
    JOBDIVANO = models.CharField(max_length=64)
    employee = models.ForeignKey(Candidate, on_delete=models.PROTECT)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)


class Submittal(models.Model):
    ID = models.CharField(primary_key=True, max_length=64)
    JOB = models.OneToOneField(Job, on_delete=models.PROTECT)
    CANDIDATE = models.OneToOneField(Candidate, on_delete=models.PROTECT)


class Placement(models.Model):
    submittal = models.OneToOneField(Submittal, on_delete=models.PROTECT)


class Hire(models.Model):
    ACTIVITYID = models.CharField(primary_key=True, max_length=64)
    JOB = models.ForeignKey(Job, on_delete=models.PROTECT)
    CANDIDATE = models.ForeignKey(Candidate, on_delete=models.PROTECT)
    COMPANY = models.ForeignKey(Company, on_delete=models.PROTECT)
    ACTIVITYDATE = models.DateTimeField()
