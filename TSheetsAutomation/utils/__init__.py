from django.conf import settings
from datetime import datetime
from dateutil import relativedelta
import os


def get_credentials(filename):
    with open(os.path.join(settings.CREDENTIALS_FOLDER, filename), "r+") as f:
        username = f.readline()
        password = f.readline()

    if username[-1] == "\n":
        username = username[:-1]
    if password[-1] == "\n":
        password = password[:-1]

    return username, password


def get_n_mondays_ago(n):
    today = datetime.now()
    n_mondays_ago = relativedelta.relativedelta(weekday=relativedelta.MO(-n))
    return (today - n_mondays_ago).strftime("%Y-%m-%d")


def get_n_sundays_ago(n):
    today = datetime.now()
    n_sundays_ago = relativedelta.relativedelta(weekday=relativedelta.SU(-n))
    return (today + n_sundays_ago).strftime("%Y-%m-%d")
