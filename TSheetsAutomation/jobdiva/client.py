import logging
from datetime import datetime
from dateutil import relativedelta
from functools import wraps
from time import sleep

from zeep import Client
from utils import get_credentials

DATETIME_STRING_FMT = "%Y-%m-%d"

one_sunday_ago = relativedelta.relativedelta(weekday=relativedelta.SU(-5))
last_sunday_string = (datetime.now() + one_sunday_ago).strftime(DATETIME_STRING_FMT)
two_mondays_ago = relativedelta.relativedelta(weekday=relativedelta.MO(-6))
two_mondays_ago_string = (datetime.now() - two_mondays_ago).strftime(DATETIME_STRING_FMT)

RETRY_ATTEMPTS = 2


class BaseJobDivaClient:
    def __init__(self, service):
        self.username, self.password = get_credentials("jobdiva_username_and_password.txt")
        self.logger = logging.getLogger(f"JobDivaClient - {service}")
        self._client = Client(f"https://ws.jobdiva.com/axis2-1.6.1/services/{service}?wsdl")

        for method_name in dir(self._client.service):
            if not method_name.startswith("__"):
                api = getattr(self._client.service, method_name)
                setattr(self, method_name, self.wrapped_api_call(api, service))

    def wrapped_api_call(self, api, service):
        @wraps(api)
        def add_creds(*args, **kwargs):
            if service == "JobDivaAPI":
                _kwargs = {
                    "clientid": 665,
                    "username": self.username,
                    "password": self.password,
                    **kwargs,
                }
            elif service == "BIData":
                _kwargs = {
                    "ClientID": 665,
                    "Username": self.username,
                    "Password": self.password,
                    **kwargs,
                }

            ret = api(**_kwargs)
            for _ in range(0, RETRY_ATTEMPTS):
                if not ret.Data:
                    if "There are too many API requests in the queue." in ret.Message:
                        self.logger.log(
                            logging.warning, "Too many api requests. Sleeping for 4 minutes."
                        )
                        sleep(60 * 4)
                        ret = api(**_kwargs)
                    else:
                        raise Exception(ret.Message)
                else:
                    self.logger.log(logging.DEBUG, f"Received {ret} from {service} for {_kwargs}")
                    return ret

        return add_creds


def cast_ids_to_ints(fields):
    return {field: int(value) if "ID" in field else value for field, value in fields.items()}


class JobDivaAPIClient(BaseJobDivaClient):
    def __init__(self):
        super().__init__(service="JobDivaAPI")


class BIDataClient(BaseJobDivaClient):
    def __init__(self):
        super().__init__(service="BIData")

    def get(
        self,
        metric,
        from_string=two_mondays_ago_string,
        to_string=last_sunday_string,
        parameters=None,
    ):
        data = self.get_raw_data(metric, from_string, to_string, parameters)
        if data.Data:
            row_data = data.Data.Row
        else:
            raise Exception(f"{data.Message}")
        metrics = []
        for datum in row_data:
            metrics_dict = {}
            for datumum in datum["RowData"]:
                metrics_dict[datumum["Name"]] = datumum["Value"]
            metrics.append(metrics_dict)
        return metrics

    def get_raw_data(
        self,
        metric,
        from_string=two_mondays_ago_string,
        to_string=last_sunday_string,
        parameters=None,
    ):
        ret = self.getBIData(
            MetricName=metric, FromDate=from_string, ToDate=to_string, Parameters=parameters
        )
        return ret

    def get_object(self, metric, parameters=None, **kwargs):
        data = self.get(metric, parameters=parameters, **kwargs)
        if data:
            if type(data) == list:
                data = data[0]
            return data

    def new_hires(self, from_date, to_date):
        return self.get(
            metric="New Hires",
            from_string=from_date.strftime(DATETIME_STRING_FMT),
            to_string=to_date.strftime(DATETIME_STRING_FMT),
        )


"""
>>> myc.myClient.service.getBIData(
... MetricName='Employee Billing Records Detail',
...             ClientID=665,
...             Username=<username>,
...             Password=<password>,
...             FromDate=from_string,
...             ToDate=to_string,
... Parameters=6139585375286)
<xsd:element maxOccurs="1" minOccurs="1" name="date" type="xsd:dateTime"/>
<xsd:element maxOccurs="1" minOccurs="1" name="hours" type="xsd:double"/>
<xsd:element maxOccurs="1" minOccurs="0" name="timeIn" type="xsd:dateTime"/>
<xsd:element maxOccurs="1" minOccurs="0" name="lunchIn" type="xsd:dateTime"/>
<xsd:element maxOccurs="1" minOccurs="0" name="lunchOut" type="xsd:dateTime"/>
<xsd:element maxOccurs="1" minOccurs="0" name="timeOut" type="xsd:dateTime"/>
{'date': '2019-10-28T21:34:55', 'hours': 30},


<xsd:element maxOccurs="1" minOccurs="1" name="clientid" type="xsd:long"/>
<xsd:element maxOccurs="1" minOccurs="1" name="username" type="xsd:string"/>
<xsd:element maxOccurs="1" minOccurs="1" name="password" type="xsd:string"/>
<xsd:element maxOccurs="1" minOccurs="1" name="employeeid" type="xsd:long"/>
<xsd:element maxOccurs="1" minOccurs="0" name="jobid" type="xsd:long"/>
<xsd:element maxOccurs="1" minOccurs="1" name="weekendingdate" type="xsd:dateTime"/>
<xsd:element maxOccurs="1" minOccurs="1" name="approved" type="xsd:boolean"/>
<xsd:element maxOccurs="7" minOccurs="7" name="TimesheetEntry" type="tns:TimesheetEntryType"/>



<xsd:element maxOccurs="1" minOccurs="1" name="clientid" type="xsd:long"/>
<xsd:element maxOccurs="1" minOccurs="1" name="username" type="xsd:string"/>
<xsd:element maxOccurs="1" minOccurs="1" name="password" type="xsd:string"/>
<xsd:element maxOccurs="1" minOccurs="1" name="employeeid" type="xsd:long"/>
<xsd:element maxOccurs="1" minOccurs="0" name="jobid" type="xsd:long"/>
<xsd:element maxOccurs="1" minOccurs="1" name="weekendingdate" type="xsd:dateTime"/>
<xsd:element maxOccurs="1" minOccurs="1" name="payrate" type="xsd:double"/>
<xsd:element maxOccurs="1" minOccurs="0" name="overtimepayrate" type="xsd:double"/>
<xsd:element maxOccurs="1" minOccurs="0" name="doubletimepayrate" type="xsd:double"/>
<xsd:element maxOccurs="1" minOccurs="1" name="billrate" type="xsd:double"/>
<xsd:element maxOccurs="1" minOccurs="0" name="overtimebillrate" type="xsd:double"/>
<xsd:element maxOccurs="1" minOccurs="0" name="doubletimebillrate" type="xsd:double"/>
<xsd:element maxOccurs="1" minOccurs="0" name="location" type="xsd:string"/>
<xsd:element maxOccurs="1" minOccurs="1" name="title" type="xsd:string"/>
<xsd:element maxOccurs="1" minOccurs="0" name="rolenumber" type="xsd:string"/>
<xsd:element maxOccurs="1" minOccurs="0" name="timesheetid" type="xsd:long"/>
<xsd:element maxOccurs="1" minOccurs="0" name="externalid" type="xsd:string"/>
<xsd:element maxOccurs="1" minOccurs="0" name="compcode" type="xsd:string"/>
<xsd:element maxOccurs="7" minOccurs="1" name="timesheetentry" type="tns:TimesheetEntryTimeInOutType"/>
<xsd:element maxOccurs="unbounded" minOccurs="0" name="expenses" type="tns:ExpenseEntryType"/>
<xsd:element maxOccurs="unbounded" minOccurs="0" name="emailrecipients" type="xsd:string"/>

employeeid = 10947061895756
jobid = 19-00886
timesheetentries = [{"date": "2019-11-04T00:00:00", "hours": 30}, {"date": "2019-11-05T00:00:00", "hours": 30}, {"date": "2019-11-06T00:00:00", "hours": 30} ,{"date": "2019-11-07T00:00:00", "hours": 30}, {"date": "2019-11-08T00:00:00", "hours": 30}, {"date": "2019-11-09T00:00:00", "hours": 30}, {"date": "2019-11-10T00:00:00", "hours": 30}]
weekendingdate="2019-11-10T00:00:00"

"""

# api(ClientID=665, Username=self.username, Password=self.password, **kwargs)
