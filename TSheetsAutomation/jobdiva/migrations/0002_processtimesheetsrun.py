# Generated by Django 2.2.6 on 2019-11-17 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobdiva', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessTimesheetsRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('run_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]