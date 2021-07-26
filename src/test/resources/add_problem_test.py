import json

import pytest
import urllib3

http = urllib3.PoolManager()
url = "https://rpixnvd51i.execute-api.us-east-1.amazonaws.com/deployedStage"


def test_not_enough_fields():
    test_body = {
        "location": [36.20914513392121, -115.19957114599852],
        "problem_type": "Criminal Act",
        "problem_description": "bank heist"
    }
    response = http.request(
        "POST",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b'Four items required. Received 3.\nInput: {"location": [36.20914513392121, -115.19957114599852], "problem_type": "Criminal Act", "problem_description": "bank heist"}'

def test_invalid_location_type():
    test_body = {
        "location": "my house",
        "problem_type": "Criminal Act",
        "problem_description": "bank heist",
        "image_path": [""]
    }
    response = http.request(
        "POST",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b"'location' is a required field which takes a list of two points, both of type float. The first represents the latitude (which must be a number between -90 and 90) and the second represents the longitude (which must be a number between -180 and 180)"

def test_invalid_location_value():
    test_body = {
        "location": [136.20914513392121, -115.19957114599852],
        "problem_type": "Criminal Act",
        "problem_description": "bank heist",
        "image_path": [""]
    }
    response = http.request(
        "POST",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b"'location' is a required field which takes a list of two points, both of type float. The first represents the latitude (which must be a number between -90 and 90) and the second represents the longitude (which must be a number between -180 and 180)"

def test_invalid_problem_type():
    test_body = {
        "location": [36.20914513392121, -115.19957114599852],
        "problem_type": "the third one",
        "problem_description": "bank heist",
        "image_path": [""]
    }
    response = http.request(
        "POST",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b"'problem_type' is a required field and must be 'Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire', 'Water Damage', or 'Other'"

def test_invalid_problem_description():
    test_body = {
        "location": [36.20914513392121, -115.19957114599852],
        "problem_type": "Criminal Act",
        "problem_description": 7,
        "image_path": [""]
    }
    response = http.request(
        "POST",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b"'problem_description' is a required field and must be of type string"

def test_invalid_image_path():
    test_body = {
        "location": [36.20914513392121, -115.19957114599852],
        "problem_type": "Criminal Act",
        "problem_description": "bank heist",
        "image_path": {"pic": "img"}
    }
    response = http.request(
        "POST",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b"'image_path' is a required field which must be a list of strings"

def test_no_image():
    test_body = {
        "location": [31.77715670567932, 35.234471536758164],
        "problem_type": "Criminal Act",
        "problem_description": "test - bank heist 1",
        "image_path": [""]
    }
    response = http.request(
        "POST",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 200
    assert response.data == b"Success, problem ticket uploaded. An employee will soon take care of the issue."

def test_one_image():
    test_body = {
        "location": [31.772476274945593, 35.20411435593286],
        "problem_type": "Criminal Act",
        "problem_description": "test - bank heist 2",
        "image_path": ["iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAIAAAACDbGyAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAARSURBVBhXY/j/CQVRxv/EAACvCDCKJ2FhswAAAABJRU5ErkJggg=="]
    }
    response = http.request(
        "POST",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 200
    assert response.data == b"Success, problem ticket uploaded. An employee will soon take care of the issue."

def test_multiple_images():
    test_body = {
        "location": [31.788206782571194, 35.21833711571499],
        "problem_type": "Criminal Act",
        "problem_description": "test - bank heist 3",
        "image_path": [
            "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAIAAAACDbGyAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAARSURBVBhXY/j/CQVRxv/EAACvCDCKJ2FhswAAAABJRU5ErkJggg==",
            "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAIAAAACDbGyAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAASSURBVBhXY1jsuQQZUcb3XAIAGxEnEfe2ak0AAAAASUVORK5CYII="
            ]
    }
    response = http.request(
        "POST",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 200
    assert response.data == b"Success, problem ticket uploaded. An employee will soon take care of the issue."