import json

import pytest
import urllib3
from urllib3.packages.six import b

http = urllib3.PoolManager()
url = "https://rpixnvd51i.execute-api.us-east-1.amazonaws.com/deployedStage"

def test_invalid_id_type():
    query = {
        "id": "what"
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 400
    assert response.data == b'The ID you requested is not in the problems table.'

def test_invalid_id_number():
    query = {
        "id": 999999
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 400
    assert response.data == b'The ID you requested is not in the problems table.'

def test_invalid_problem_type():
    query = {
        "problem_type": "test"
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 400
    assert response.data == b"problem_type must be set to 'Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire', 'Water Damage', or 'Other'"

def test_too_many_times():
    query = {
        "time_found": "2021-07-07T17:29,2021-07-07T17:30,2021-07-07T17:31"
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 400
    assert response.data == b"'time_found' takes a string of two 'times' seperated by a comma. 'time' is formatted as follows: YYYY-MM-DD HH:MM"

def test_invalid_time_format():
    query = {
        "time_found": "2021-07-07T17-28,2021-07-07T17-30"
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 400
    assert response.data == b"Each time in 'time_found' must be formatted as follows: YYYY-MM-DD HH:MM"

def test_time_with_seconds():
    query = {
        "time_found": "2021-07-07T17:29:14,2021-07-07T17:29:16"
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 400
    assert response.data == b"Each time in 'time_found' must be formatted as follows: YYYY-MM-DD HH:MM"

def test_invalid_time_type():
    query = {
        "time_found": 202107071728202107071730
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 400
    assert response.data == b"'time_found' takes a string of two 'times' seperated by a comma. 'time' is formatted as follows: YYYY-MM-DD HH:MM"

def test_negative_time():
    query = {
        "time_found": "2021-07-07T17:30,2021-07-07T17:28"
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 400
    assert response.data == b"The second time must be later than the first. 'time' is formatted as follows: YYYY-MM-DD HH:MM"

def test_invalid_current_status():
    query = {
        "current_status": "haha"
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 400
    assert response.data == b"Current Status must be set to 'Open', 'In Progress', or 'Complete'"

def test_negative_distance():
    query = {
        "location": "36.2091451339212,-115.199571145999",
        "distance": -1
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 400
    assert response.data == b"'distance' must be at least 0"

def test_invalid_location():
    query = {
        "location": "136.2091451339212,-115.199571145999",
        "distance": 7
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 400
    assert response.data == b"'location' takes a string of two points (both of type float) seperated by a comma. The first represents the latitude (which must be a number between -90 and 90) and the second represents the longitude (which must be a number between -180 and 180)"

def test_invalid_distance():
    query = {
        "location": "36.2091451339212,-115.199571145999",
        "distance": "close"
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 400
    assert response.data == b"'distance' must be a number."

def test_only_location():
    query = {
        "location": "36.2091451339212,-115.199571145999"
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 400
    assert response.data == b"'location must always be paired with 'distance'"

def test_only_distance():
    query = {
        "distance": 5
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 400
    assert response.data == b"'distance' must always be paired with 'location'"

def test_full_param_search():
    query = {
        "id": 1,
        "problem_type": "Road Hazard",
        "problem_description": "bad guy",
        "time_found": "2021-07-22T13:48,2021-07-22T13:50",
        "current_status": "Open",
        "location": "25.123,50.456",
        "distance": 0.01,
        "image_path": 'https://s3.console.aws.amazon.com/s3/buckets/smartcitystack-smartcitys3bucket-21vjidos6mgc?prefix=1/'
  }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 200
    assert len(json.loads(response.data)) == 1
    # assert response.data == b

def test_id():
    query = {
        "id": 1
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 200
    assert len(json.loads(response.data)) == 1

def test_problem_type():
    query = {
        "problem_type": "Road Hazard"
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 200
    # assert len(json.loads(response.data)) == 1

def test_problem_description():
    query = {
        "problem_description": "bad guy"
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 200
    assert len(json.loads(response.data)) == 1

def test_time_found():
    query = {
        "time_found": "2021-07-22T13:48,2021-07-22T13:50"
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 200
    assert len(json.loads(response.data)) == 1

def test_location_distance(): # put several points 2km of eachother and ensure length
    query = {
        "location": "25.123,50.456",
        "distance": 2,
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 200
    # assert len(json.loads(response.data)) == 1

def test_image_path():
    query = {
        "image_path": 'https://s3.console.aws.amazon.com/s3/buckets/smartcitystack-smartcitys3bucket-21vjidos6mgc?prefix=1/'
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 200
    # assert len(json.loads(response.data)) == 1