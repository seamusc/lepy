import pytest
import requests_mock
from logsearch.logsearch import LogSearch


def test_load_logsearch_with_api_key_makes_request_to_rest():
    with requests_mock.Mocker() as m:
        m.get(
            "https://eu.rest.logs.insight.rapid7.com/management/organizations/apikeys", 
            request_headers={'x-api-key': 'dummy_key'},
            text='ok'
            )
        ls = LogSearch(api_key='dummy_key')

def test_load_logsearch_with_invalid_api_key_raises_value_error():
    with requests_mock.Mocker() as m:
        m.get(
            "https://eu.rest.logs.insight.rapid7.com/management/organizations/apikeys", 
            request_headers={'x-api-key': 'dummy_key'},
            status_code=404
            )
        with pytest.raises(ValueError) as excinfo:
            ls = LogSearch(api_key='dummy_key')        
        assert str(excinfo.value) == 'API Key is not valid or a readonly key'


def test_load_logsearch_with_region_makes_request_to_correct_region():
    for region in ['US', 'EU', 'AU', 'CA']:
        with requests_mock.Mocker() as m:
            m.get(
                "https://%s.rest.logs.insight.rapid7.com/management/organizations/apikeys" % region,
                request_headers={'x-api-key': 'dummy_key'},
                text='ok'
                )
            ls = LogSearch(api_key='dummy_key', region=region)


def test_load_logsearch_with_invalid_region():
    with pytest.raises(ValueError) as excinfo:
        ls = LogSearch(api_key='dummy_key', region='FR')

    assert str(excinfo.value) == "Unrecognised region 'FR' valid regions are [EU, CA, AU, US]"