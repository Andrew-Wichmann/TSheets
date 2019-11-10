# Generated by Django 2.2.6 on 2019-11-09 20:09

from django.db import migrations, models


def add_zones(apps, schema_editor):
    Company = apps.get_model("Timesheets", "TSheetsCompany")
    Company(id=6373103, name="Zones, Inc.").save()


class Migration(migrations.Migration):

    dependencies = [("Timesheets", "0001_initial")]

    operations = [migrations.RunPython(add_zones)]
