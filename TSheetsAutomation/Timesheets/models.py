from django.db import models


class Owner(models.Model):
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email = models.EmailField()


class Timesheet(models.Model):
    owner = Owner()
    start = models.DateField()
    end = models.DateField()

