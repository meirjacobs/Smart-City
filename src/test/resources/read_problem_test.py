import datetime
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

def test_full_param_search(mysql_cursor):
    mycursor = mysql_cursor
    insert = "INSERT INTO problems (problem_type, problem_description, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    val = ("Road Hazard", f"{prefix}-test1", 35.21962829400858, 31.78087640916267, "https://www.test.com/1")
    mycursor.execute(insert, val)
    id_number = mycursor.lastrowid
    now = datetime.datetime.utcnow()
    one_minute = datetime.timedelta(minutes=1)
    start_time = datetime.datetime.strftime(now - one_minute, '%Y-%m-%dT%H:%M')
    end_time = datetime.datetime.strftime(now + one_minute, '%Y-%m-%dT%H:%M')
    time_query = f"{start_time},{end_time}"
    query = {
        "id": id_number,
        "problem_type": "Road Hazard",
        "problem_description": f"{prefix}-test1",
        "time_found": time_query,
        "current_status": "Open",
        "location": "31.78087640916267,35.21962829400858",
        "distance": 3,
        "image_path": "https://www.test.com/1"
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 200
    assert len(json.loads(response.data)) == 1
    mycursor.execute(f"DELETE FROM problems WHERE problem_description = '{prefix}-test1'")

def test_id(mysql_cursor):
    mycursor = mysql_cursor
    insert = "INSERT INTO problems (problem_type, problem_description, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    val = ("Other", f"{prefix}-test2", 35.21962829400858, 31.78087640916267, "https://www.test.com/2")
    mycursor.execute(insert, val)
    id_number = mycursor.lastrowid
    query = {
        "id": id_number
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 200
    assert len(json.loads(response.data)) == 1
    mycursor.execute(f"DELETE FROM problems WHERE problem_description = '{prefix}-test2'")

def test_problem_type(mysql_cursor):
    mycursor = mysql_cursor
    mycursor.execute(f"SELECT COUNT(*) FROM problems WHERE problem_type = 'Fire'")
    count = mycursor.fetchone()[0]
    query = {
        "problem_type": "Fire"
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 200
    assert len(json.loads(response.data)) == count

def test_problem_description(mysql_cursor):
    mycursor = mysql_cursor
    insert = "INSERT INTO problems (problem_type, problem_description, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    val = ("Other", f"{prefix}-test3", 35.21962829400858, 31.78087640916267, "https://www.test.com/3")
    mycursor.execute(insert, val)
    query = {
        "problem_description": f"{prefix}-test3"
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 200
    assert len(json.loads(response.data)) == 1
    mycursor.execute(f"DELETE FROM problems WHERE problem_description = '{prefix}-test3'")

def test_time_found(mysql_cursor):
    mycursor = mysql_cursor
    insert = "INSERT INTO problems (problem_type, problem_description, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    val = ("Other", f"{prefix}-test4", 35.21962829400858, 31.78087640916267, "https://www.test.com/4")
    mycursor.execute(insert, val)
    now = datetime.datetime.utcnow()
    one_minute = datetime.timedelta(minutes=1)
    start_time = datetime.datetime.strftime(now - one_minute, '%Y-%m-%dT%H:%M')
    end_time = datetime.datetime.strftime(now + one_minute, '%Y-%m-%dT%H:%M')
    time_query = f"{start_time},{end_time}"
    query = {
        "time_found": time_query
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 200
    assert len(json.loads(response.data)) == 1
    mycursor.execute(f"DELETE FROM problems WHERE problem_description = '{prefix}-test4'")

def test_location_distance(mysql_cursor):
    mycursor = mysql_cursor
    mycursor.execute("SELECT COUNT(*) FROM problems WHERE ST_Distance_Sphere(point(61.995984186670654, -80.55866399039516), location) <= 1500")
    count = mycursor.fetchone()[0]
    insert = "INSERT INTO problems (problem_type, problem_description, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    vals = [
        ("Other", f"{prefix}-test5", 62.04679595396581, -80.56541973822662, "https://www.test.com/5"),
        ("Vehicle Damage", f"{prefix}-test6", 61.93281280030372, -80.56373125049183, "https://www.test.com/6"),
        ("'Environmental Hazard", f"{prefix}-test7", 61.99667083217465, -80.54705544360307, "https://www.test.com/7")
    ]
    mycursor.executemany(insert, vals)
    query = {
        "location": "-80.55866399039516, 61.995984186670654",
        "distance": 3
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 200
    assert len(json.loads(response.data)) == count+3
    mycursor.execute(f"DELETE FROM problems WHERE problem_description = '{prefix}-test5'")
    mycursor.execute(f"DELETE FROM problems WHERE problem_description = '{prefix}-test6'")
    mycursor.execute(f"DELETE FROM problems WHERE problem_description = '{prefix}-test7'")

def test_image_path(mysql_cursor):
    mycursor = mysql_cursor
    insert = "INSERT INTO problems (problem_type, problem_description, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    val = ("Other", f"{prefix}-test8", 51.338101799940105, 35.699658241009146, f"https://www.test.com/{prefix}")
    mycursor.execute(insert, val)
    query = {
        "image_path": f"https://www.test.com/{prefix}"
    }
    response = http.request(
        "GET",
        url,
        fields = query
    )
    assert response.status == 200
    assert len(json.loads(response.data)) == 1
    mycursor.execute(f"DELETE FROM problems WHERE problem_description = '{prefix}-test8'")