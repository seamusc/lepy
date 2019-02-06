"""
tests
"""
import pytest
import requests_mock
from logsearch.logsearch import LogSearch

__API_KEY = 'DUMMY_API_KEY'
__API_KEY_HEADER = {'x-api-key': __API_KEY}

__API_KEY_URL = 'https://eu.rest.logs.insight.rapid7.com/management/organizations/apikeys'

__SEARCH_QUERY_URL = "https://eu.rest.logs.insight.rapid7.com/query/logs?limit=1"

__LOG_ID ='a96d464b-acf7-43c8-b133-4df8551e718d'

__SEARCH_QUERY_RESULTS_URL = 'https://eu.rest.logs.insight.rapid7.com/query/' \
    'f9eab513-2b74-49e9-8a60-421880324294:1:43e3ccb9c280164eeb5b1167164975c094a21f2b' \
    '::ff9470943e7ae1b73c9f4067560a769f7007b544:' \
    '?log_keys=%s&query=where(main)+calculate(count)&time_range=Last+24+Hours' % __LOG_ID

__SEARCH_QUERY_RESPONSE_JSON = {
    "logs": ["a96d464b-acf7-43c8-b133-4df8551e718d"],
    "progress": 0,
    "events": [],
    "partial": {
        "cardinality": 0,
        "granularity": 8640000,
        "from": 1549383619380,
        "to": 1549470019380,
        "type": "count",
        "stats": {
            "global_timeseries": {
                "count": 0
            }
        },
        "groups": [],
        "status": 200,
        "timeseries": {
            "global_timeseries": [
                {"count": 0},
                {"count": 0},
                {"count": 0},
                {"count": 0},
                {"count": 0},
                {"count": 0},
                {"count": 0},
                {"count": 0},
                {"count": 0},
                {"count": 0}
            ]
        },
        "count": 0
    },
    "links": [
        {
            "rel": "Self",
            "href": "https://eu.rest.logs.insight.rapid7.com/query/f9eab513-2b74-49e9-8a60-421880324294:1:43e3ccb9c280164eeb5b1167164975c094a21f2b::ff9470943e7ae1b73c9f4067560a769f7007b544:?log_keys=a96d464b-acf7-43c8-b133-4df8551e718d&query=where(main)+calculate(count)&time_range=Last+24+Hours"
        }
    ],
    "id": "f9eab513-2b74-49e9-8a60-421880324294:1:43e3ccb9c280164eeb5b1167164975c094a21f2b::ff9470943e7ae1b73c9f4067560a769f7007b544:",
    "leql": {
        "statement": "where(main) calculate(count)",
        "during": {
            "from": 1549383619380,
            "to": 1549470019380,
            "time_range": "Last 24 Hours"
        }
    }
}

__SEARCH_QUERY_RESULTS_RESPONSE_JSON = {
    "logs": ["a96d464b-acf7-43c8-b133-4df8551e718d"],
    "statistics": {
        "cardinality": 0,
        "granularity": 8640000,
        "from": 1549383619380,
        "to": 1549470019380,
        "type": "count",
        "stats": {
            "global_timeseries": {
                "count": 143
            }
        },
        "groups": [],
        "status": 200,
        "timeseries": {
            "global_timeseries": [
                {"count": 0},
                {"count": 0},
                {"count": 0},
                {"count": 0},
                {"count": 0},
                {"count": 0},
                {"count": 0},
                {"count": 59},
                {"count": 84},
                {"count": 0}
            ]
        },
        "count": 143
    },
    "leql": {
        "statement": "where(main) calculate(count)",
        "during": {
            "from": 1549383619380,
            "to": 1549470019380,
            "time_range": "Last 24 Hours"
        }
    }
}

__REGIONS = ['US', 'EU', 'AU', 'CA']


def test_load_logsearch_with_api_key_makes_request_to_rest():
    with requests_mock.Mocker() as m:
        m.get(__API_KEY_URL, request_headers=__API_KEY_HEADER, text='ok')
        LogSearch(api_key=__API_KEY)


def test_load_logsearch_with_invalid_api_key_raises_value_error():
    with requests_mock.Mocker() as m:
        m.get(__API_KEY_URL, request_headers=__API_KEY_HEADER, status_code=404)

        with pytest.raises(ValueError) as excinfo:
            LogSearch(api_key=__API_KEY)

        assert str(excinfo.value) == 'API Key is not valid or a readonly key'


def test_load_logsearch_with_region_makes_request_to_correct_region():
    for region in __REGIONS:
        with requests_mock.Mocker() as m:
            url = __API_KEY_URL.replace('eu.', region + '.')
            m.get(url, request_headers=__API_KEY_HEADER, text='ok')
            LogSearch(api_key=__API_KEY, region=region)


def test_load_logsearch_with_invalid_region():
    with pytest.raises(ValueError) as excinfo:
        LogSearch(api_key=__API_KEY, region='FR')

    assert str(excinfo.value) == "Unrecognised region 'FR' valid regions are [EU, US, CA, AU]"


def test_simple_query_when_lerest_returns_202_continuation():
    with requests_mock.Mocker() as m:
        m.get(__API_KEY_URL,
              request_headers=__API_KEY_HEADER,
              json={'apikeys': [__LOG_ID]},
              status_code=200)

        dummy_continuation_link_dict = {
            'rel': 'Self',
            'href': __SEARCH_QUERY_RESULTS_URL
        }

        resp_body = {
            'events': [],
            'links': [dummy_continuation_link_dict,],
            'progress': 0
        }

        m.post(__SEARCH_QUERY_URL,
               request_headers=__API_KEY_HEADER,
               status_code=202,
               json=resp_body)

        m.get(__SEARCH_QUERY_RESULTS_URL, json=__SEARCH_QUERY_RESULTS_RESPONSE_JSON)

        ls = LogSearch(api_key=__API_KEY)
        query = ls.search(query='where(main) calculate(count)',
                          log_ids=[__LOG_ID],
                          time_range='Last 24 Hours',
                          limit=1)
        assert query.get_resp().json() == __SEARCH_QUERY_RESULTS_RESPONSE_JSON


def test_simple_query_when_lerest_returns_200_no_continuation():
    with requests_mock.Mocker() as m:
        m.get(__API_KEY_URL,
              request_headers=__API_KEY_HEADER,
              json={'apikeys': [__LOG_ID]},
              status_code=200)

        m.post(__SEARCH_QUERY_URL,
               request_headers=__API_KEY_HEADER,
               status_code=200,
               json=__SEARCH_QUERY_RESULTS_RESPONSE_JSON)

        ls = LogSearch(api_key=__API_KEY)

        query = ls.search(query='where(main) calculate(count)',
                          log_ids=[__LOG_ID],
                          time_range='Last 24 Hours',
                          limit=1)
        assert query.get_resp().json() == __SEARCH_QUERY_RESULTS_RESPONSE_JSON
