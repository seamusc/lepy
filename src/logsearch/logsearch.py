import datetime
import json as JSON
import time
import uuid

import requests
import tabulate
from progress.bar import Bar

session = requests.Session()
session.headers.update({'User-Agent': 'lepy scawley@rapid7.com'})


def ms_to_date_string(timestamp):
    return datetime.datetime.fromtimestamp(timestamp/1000.0).strftime('%d/%m/%y %H:%M:%S.%f')


def to_timestamp(date_string):
    """
    Generate a timestamp from a date string in the format dd/mm/yy hh:mm
    """
    return int(datetime.datetime.strptime(date_string, '%d/%m/%y %H:%M').strftime('%s')) * 1000


class LogSearch(object):
    """
    LogSearch API

    :param region: The region the Account is in (EU|US|CA|AP)
    :param api_key: The API Key to use
    """
    class LSException(Exception, object):
        def __init__(self, messsage):
            super(Exception).__init__(self, messsage)

    class APIError(LSException, object):
        def __init__(self, message):
            super(Exception).__init__(self, message)


    REGIONS = ['EU', 'US', 'CA', 'AU']

    class Query(object):

        def __init__(self, resp, progress, parent):
            self.__resp = resp
            self.__events = []
            self.__error = False
            self.__parent = parent

            if progress:
                self.__progress = Bar("Progress", max=100, suffix='%(percent)d%% %(elapsed)ds %(eta_td)s')
            else:
                self.__progress = None

        def poll_query(self):
            while True:
                res = self.__resp.json()
                continue_url = res['links'][0]['href']
                percentage = res['progress']

                if 'events' in res and res['events']:
                    self.__events.extend(res['events'])

                if self.__progress:
                    self.__progress.goto(percentage)
                res = session.get(continue_url, headers=self.__parent.headers)
                self.__resp = res
                if not (200 <= self.__resp.status_code <= 300 and 'links' in self.__resp.json() and self.__resp.json()['links'][0]['rel'] == 'Self'):
                    break
                time.sleep(1)

            if self.__resp.status_code == 200:
                res = self.__resp.json()
                if 'events' in res and res['events']:
                    self.__events.extend(res['events'])

                if self.__progress:
                    self.__progress.goto(100)
                    self.__progress.finish()
                return self

            self.__error = True
            raise LogSearch.APIError("There was an api error")

        def get_resp(self):
            return self.__resp

        def events(self):
            if not self.__error:
                return [e['message'] for e in self.__events]
            else:
                raise LogSearch.APIError("There was an api error")

        def count(self):
            if self.__error:
                raise LogSearch.APIError("There was an api error")

            res = self.__resp.json()
            if res['statistics']['groups'] != []:
                raise LogSearch.LSException("This query does not contain count information")

            calc_type = res['statistics']['type']
            if calc_type == 'count':
                key = 'global_timeseries'
            else:
                key = calc_type
            timeseries = res['statistics']['timeseries']

            if key not in timeseries:
                key = timeseries.keys()[0]

            return calc_type, [v[calc_type] for v in res['statistics']['timeseries'][key]]


        def groups(self):
            if self.__error:
                raise LogSearch.APIError("There was an api error")
            table = []
            for group in self.__resp.json()['statistics']['groups']:
                group_name = group.keys()[0]
                value = group.values()[0].values()[0]
                table.append((group_name, value,))
            return table

        def display(self, table_format=None):
            if self.__error:
                raise LogSearch.APIError("There was an api error")
            print(JSON.dumps(self.__resp.json()['leql'], indent=4, sort_keys=True))
            if 'events' in self.__resp.json():
                print(JSON.dumps(self.__resp.json(), indent=4, sort_keys=True))
                return
            elif 'statistics' in self.__resp.json():
                from_time = self.__resp.json()['statistics']['from']
                to_time = self.__resp.json()['statistics']['to']
                calc_type = self.__resp.json()['statistics']['type']
                key = self.__resp.json()['statistics'].get('key', 'global_timeseries')
                print('Statistics response',)
                if 'groups' in self.__resp.json()['statistics'] and self.__resp.json()['statistics']['groups']:
                    print('groupby(%s)' % self.__resp.json()['statistics']['key'],)
                    print('calculate(%s)' % calc_type + ' : ' + key if key != 'global_timeseries' else calc_type)
                    headers = ["Group", self.__resp.json()['statistics']['type']]
                    table = self.groups()
                    print(tabulate.tabulate(table, headers=headers, tablefmt=table_format))
                    return
                if 'timeseries' in self.__resp.json()['statistics'] and self.__resp.json()['statistics']['timeseries']:
                    print('calculate(', calc_type + ' : ' + key if key != 'global_timeseries' else calc_type, ')')

                    table = []
                    headers = ["Timestamp", calc_type + ' : ' + key if key != 'global_timeseries' else calc_type]
                    timeseries = self.__resp.json()['statistics']['timeseries'][key]
                    interval = (from_time - to_time) / len(timeseries)
                    timestamp = from_time
                    for ts in timeseries:
                        table.append((ms_to_date_string(timestamp), str(ts[calc_type]), ))
                        timestamp += interval
                    print(tabulate.tabulate(table, headers=headers, tablefmt=table_format))
                    return

                print(JSON.dumps(self.__resp.json(), indent=4, sort_keys=True))
                return

        @staticmethod
        def __validate_table_format(table_format):
            if table_format not in tabulate.tabulate_formats and table_format != 'csv':
                raise ValueError("Invalid table format '%s', valid values are '%s'" % (table_format, ', '.join(tabulate.tabulate_formats)))

    @property
    def __region_url(self):
        return "https://%s.rest.logs.insight.rapid7.com/" % self.region.lower()

    @property
    def __query_url(self):
        return self.__region_url + "query/logs"

    @property
    def headers(self):
        return {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "x-api-key": self.__api_key,
                "User-Agent": "lepy"
                }

    def __init__(self, region='EU', api_key=None):
        if region in LogSearch.REGIONS:
            self.region = region
        else:
            raise ValueError("Unrecognised region '%s' valid regions are [%s]" % (region, ', '.join(LogSearch.REGIONS)))

        if api_key is None:
            raise ValueError("`api_key` is a required parameter")
        self.__api_key = api_key
        self.__queries = []
        res = self.rest_call('get', 'management/organizations/apikeys')
        if res.status_code == 404:
            raise ValueError("API Key is not valid or a readonly key")

    def rest_call(self, method, path, json=None, extra_headers=None, expected_status=None):
        headers = self.headers
        if extra_headers is not None:
            headers.update(extra_headers)

        res = session.request(method=method, url=self.__region_url + path, json=json, headers=headers)
        if expected_status and res.status_code != expected_status:
            raise self.APIError("Unexpected status code. Expected %s, got %s with body %s" % (
            expected_status, res.status_code, res.content))
        return res

    def get_logs(self):
        """Retrieve a list of all Logs in the Account
        """
        res = self.rest_call('get', 'management/logs', expected_status=200)
        return res.json()['logs']

    def find_logs(self, name, display=True):
        """Find Logs in the Account which have `name` in the name

        :param name: the string to search for
        :param display: Should the results be displayed in a table, default True

        :returns: a list of matching Logs
        """
        data = [(l['name'], l['id']) for l in self.get_logs() if name in l['name']]
        if display:
            print(tabulate.tabulate(data, headers=["Log Name", "Log Id"]))
        return data

    def search(self, query='', log_ids=None, time_range=None, from_time=None, to_time=None, progress=True, limit=500, query_params=None):
        """Perform a LEQL query against a list of logs over the specified time period

        Note: One of `time_range` or `from_time` is required
              if `time_range` is supplied `from_time` and `to_time` should not be supplied
              if `from_time` is supplied `to_time` may be supplied, or if not the current time is assumed

        :param query: the LEQL query to run
        :param log_ids: a list of log ids
        :param time_range: The time range to search (Optional)
        :param from_time: The time in ms to search from (Optional)
        :param to_time: The time in ms to search to (Optional)
        :param progress: Should progress be displayed (Default True)
        :param limit: The limit to the number of events returned (Default 500)
        :param query_params: Any additional query parameters (Default empty)

        :return: a Query Object

        :type query: basestring
        :type log_ids: list
        :type time_range: basestring
        :type from_time: int
        :type to_time: int
        :type progress: bool
        :type limit: int
        :type query_params: dict
        :rtype: LogSearch.Query
        """
        self.__validate_query_params(log_ids, time_range, from_time, to_time)
        request_body = {
                "leql": {
                    "during": {
                        "from": from_time,
                        "to": to_time,
                        "time_range": time_range
                        },
                    "statement": query,
                    },
                "logs": log_ids
            }
        params = {'limit': limit}
        params.update(query_params)
        res = session.post(self.__query_url, json=request_body, headers=self.headers, params=params)
        return LogSearch.Query(res, progress, self).poll_query()

    @staticmethod
    def __validate_query_params(log_ids, time_range, from_time, to_time):
        """
        Validate that the query parameters are correct
        """
        if log_ids is None or not isinstance(log_ids, list):
            raise ValueError("`log_ids` is a required parameter and must be a list")

        for log_id in log_ids:
            try:
                uuid.UUID(log_id)
            except:
                raise ValueError("`log_ids` must be a list of valid uuids. '%s' is not a valid uuid" % log_id)

        if (time_range is None and from_time is None) or (time_range is not None and from_time is not None):
            raise ValueError("One of `time_range` or `from_time` is required")

        if from_time is not None and to_time is not None:
            if not isinstance(from_time, int) or not isinstance(to_time, int):
                raise ValueError("`from_time` and `to_time` must be integers")
            if from_time >= to_time:
                raise ValueError("`from_time` must be before `to_time`")
