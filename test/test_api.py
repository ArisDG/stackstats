"""
This script contains tests for the statistics API, similar to
the ones exported from postman

"""
import json
from datetime import datetime
import requests

# api endpoint
URL = 'http://localhost:5000/api/v1/stackstats'

# request function
def api_request(data):
    """
    This function is a wrapper for the statistics API request tests
    """
    rsp = requests.get(URL, params=data)
    assert json.loads(rsp.content.decode())
    data = rsp.json()
    return data


if __name__ == "__main__":

    # Get two sample dates in the specified format
    until = datetime.now()
    until = until.strftime("%Y-%m-%d %H:%M:%S")

    since = '2021-04-01 00:00:00'

    # Prepare data for exception testing
    data_sane = {'since': since , 'until': until}
    data_invalid_interval = {'since': until , 'until': since}
    data_missing_since = {'until': until}
    data_missing_until = {'since': since}
    data_wrong_format_since = {'since': since[2:] , 'until': until}
    data_wrong_format_until = {'since': since , 'until': until[3:]}

    # Get responses for various test cases
    rsp_correct_request = api_request(data_sane)
    rsp_invalid_interval = api_request(data_invalid_interval)
    rsp_missing_since = api_request(data_missing_since)
    rsp_missing_until = api_request(data_missing_until)
    rsp_wrong_format_since = api_request(data_wrong_format_since)
    rsp_wrong_format_until = api_request(data_wrong_format_until)

    print("All tests passed!")
