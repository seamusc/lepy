import json

import requests_mock
from logsearch.logsearch import LogSearch, VISUAL_EFFECTS_ENABLED


__API_KEY = 'DUMMY_API_KEY'

__API_KEY_URL = 'https://eu.rest.logs.insight.rapid7.com/management/organizations/apikeys'

__SEARCH_QUERY_URL = "https://eu.rest.logs.insight.rapid7.com/query/logs?limit=1"

__SEARCH_QUERY_RESULTS_URL = 'https://eu.rest.logs.insight.rapid7.com/query/f9eab513-2b74-49e9-8a60-421880324294:1:43e3ccb9c280164eeb5b1167164975c094a21f2b::ff9470943e7ae1b73c9f4067560a769f7007b544:?log_keys=a96d464b-acf7-43c8-b133-4df8551e718d&query=where(main)+calculate(count)&time_range=Last+24+Hours'

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


def test_logsearch_with_progress_bar():
    try:
        import tabulate
        from progress.bar import Bar
    except ImportError:
        assert VISUAL_EFFECTS_ENABLED is False
        return  # Cannot continue this test, because required dependencies are not imported

    with requests_mock.Mocker() as m:
        m.get(__API_KEY_URL,
              request_headers={'x-api-key': __API_KEY},
              text='ok')
        m.post(__SEARCH_QUERY_URL,
               request_headers={'x-api-key': __API_KEY, 'Content-Type': 'application/json'},
               text=json.dumps(__SEARCH_QUERY_RESPONSE_JSON))
        m.get(__SEARCH_QUERY_RESULTS_URL,
              request_headers={'x-api-key': __API_KEY},
              text=json.dumps(__SEARCH_QUERY_RESULTS_RESPONSE_JSON))
        ls = LogSearch(region='EU', api_key=__API_KEY)
        result = ls.search(query='where(main) calculate(count)',
                           log_keys=['a96d464b-acf7-43c8-b133-4df8551e718d'],
                           time_range='Last 24 Hours',
                           show_progress=True,
                           limit=1)
        assert result._Query__progress is not None


def test_logsearch_without_progress_bar():
    with requests_mock.Mocker() as m:
        m.get(__API_KEY_URL,
              request_headers={'x-api-key': __API_KEY},
              text='ok')
        m.post(__SEARCH_QUERY_URL,
               request_headers={'x-api-key': __API_KEY, 'Content-Type': 'application/json'},
               text=json.dumps(__SEARCH_QUERY_RESPONSE_JSON))
        m.get(__SEARCH_QUERY_RESULTS_URL,
              request_headers={'x-api-key': __API_KEY},
              text=json.dumps(__SEARCH_QUERY_RESULTS_RESPONSE_JSON))
        ls = LogSearch(region='EU', api_key=__API_KEY)
        result = ls.search(query='where(main) calculate(count)',
                           log_keys=['a96d464b-acf7-43c8-b133-4df8551e718d'],
                           time_range='Last 24 Hours',
                           show_progress=False,
                           limit=1)
        assert result._Query__progress is None
