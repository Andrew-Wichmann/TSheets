from datetime import datetime
from dateutil import relativedelta


def get_n_mondays_ago(n):
    today = datetime.now()
    n_mondays_ago = relativedelta.relativedelta(weekday=relativedelta.MO(-n))
    return (today - n_mondays_ago).strftime("%Y-%m-%d")


def get_n_sundays_ago(n):
    today = datetime.now()
    n_sundays_ago = relativedelta.relativedelta(weekday=relativedelta.SU(-n))
    return (today + n_sundays_ago).strftime("%Y-%m-%d")
