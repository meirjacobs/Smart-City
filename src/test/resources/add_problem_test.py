import time
import json
import os
import uuid

import mysql.connector
import pytest
import urllib3
from dotenv import load_dotenv

load_dotenv()
url = os.environ["URL"]
http = urllib3.PoolManager()
prefix = uuid.uuid4()

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

def test_no_image(mysql_cursor):
    mycursor = mysql_cursor
    test_body = {
        "location": [40.850457801219434, -73.92896647291006],
        "problem_type": "Criminal Act",
        "problem_description": f"{prefix}-test1",
        "image_path": [""]
    }
    response = http.request(
        "POST",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 200
    assert response.data == b"Success, problem ticket uploaded. An employee will soon take care of the issue."
    mycursor.execute(f"SELECT COUNT(*) FROM problems WHERE problem_description = '{prefix}-test1'")
    assert mycursor.fetchone()[0] == 1
    mycursor.execute(f"DELETE FROM problems WHERE problem_description = '{prefix}-test1'")
    time.sleep(3)
    mycursor.execute(f"SELECT COUNT(*) FROM logs_history WHERE problem_description = '{prefix}-test1'")
    assert mycursor.fetchone()[0] == 1
    mycursor.execute(f"DELETE FROM logs_history WHERE problem_description = '{prefix}-test1'")

def test_one_image(mysql_cursor):
    mycursor = mysql_cursor
    test_body = {
        "location": [48.858412701736306, 2.2944841892005536],
        "problem_type": "Road Hazard",
        "problem_description": f"{prefix}-test2",
        "image_path": ["iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAIAAAACDbGyAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAARSURBVBhXY/j/CQVRxv/EAACvCDCKJ2FhswAAAABJRU5ErkJggg=="]
    }
    response = http.request(
        "POST",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 200
    assert response.data == b"Success, problem ticket uploaded. An employee will soon take care of the issue."
    mycursor.execute(f"SELECT COUNT(*) FROM problems WHERE problem_description = '{prefix}-test2'")
    assert mycursor.fetchone()[0] == 1
    mycursor.execute(f"DELETE FROM problems WHERE problem_description = '{prefix}-test2'")
    time.sleep(3)
    mycursor.execute(f"SELECT COUNT(*) FROM logs_history WHERE problem_description = '{prefix}-test2'")
    assert mycursor.fetchone()[0] == 1
    mycursor.execute(f"DELETE FROM logs_history WHERE problem_description = '{prefix}-test2'")

def test_multiple_images(mysql_cursor):
    mycursor = mysql_cursor
    test_body = {
        "location": [25.196991463303913, 55.27423730825178],
        "problem_type": "Environmental Hazard",
        "problem_description": f"{prefix}-test3",
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
    mycursor.execute(f"SELECT COUNT(*) FROM problems WHERE problem_description = '{prefix}-test3'")
    assert mycursor.fetchone()[0] == 1
    mycursor.execute(f"DELETE FROM problems WHERE problem_description = '{prefix}-test3'")
    time.sleep(3)
    mycursor.execute(f"SELECT COUNT(*) FROM logs_history WHERE problem_description = '{prefix}-test3'")
    assert mycursor.fetchone()[0] == 1
    mycursor.execute(f"DELETE FROM logs_history WHERE problem_description = '{prefix}-test3'")