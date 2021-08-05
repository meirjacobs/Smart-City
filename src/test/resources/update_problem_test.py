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
        "id": 1,
        "current_status": "In Progress"
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b'Three items required. Received 2.\nInput: {"id": 1, "current_status": "In Progress"}'

def test_invalid_id_type():
    test_body = {
        "id": "one",
        "current_status": "In Progress",
        "employee_id": 1
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b"The ID must be of type int"

def test_invalid_status_type(mysql_cursor, temp_id_number):
    mycursor = mysql_cursor
    id_number = temp_id_number
    insert = "INSERT INTO employees (first_name, last_name, email, department) VALUES (%s, %s, %s, %s)"
    val = ("Abraham", "Lincoln", "smartcitysns@gmail.com", "Others")
    mycursor.execute(insert, val)
    employee_id_number = mycursor.lastrowid
    test_body = {
        "id": id_number,
        "current_status": 1,
        "employee_id": employee_id_number
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b"'current_status' must be set to 'Open', 'In Progress', or 'Complete'"

def test_invalid_employee_id_type(temp_id_number):
    id_number = temp_id_number
    test_body = {
        "id": id_number,
        "current_status": "In Progress",
        "employee_id": "the best one!"
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b"The ID must be of type int"

def test_invalid_id():
    test_body = {
        "id": 99999,
        "current_status": "In Progress",
        "employee_id": 1
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b"The ID you requested is not in the problems table"

def test_invalid_status(temp_id_number):
    id_number = temp_id_number
    test_body = {
        "id": id_number,
        "current_status": "yipee!",
        "employee_id": 1
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b"'current_status' must be set to 'Open', 'In Progress', or 'Complete'"

def test_invalid_employee_id(temp_id_number):
    id_number = temp_id_number
    test_body = {
        "id": id_number,
        "current_status": "In Progress",
        "employee_id": 99999
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b"The ID you requested is not in the employees table"

def test_current_is_previous(mysql_cursor):
    mycursor = mysql_cursor
    insert = "INSERT INTO problems (problem_type, problem_description, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    val = ("Vehicle Damage", f"{prefix}-test1", -67.87264013148318, 18.058243617410188, "https://www.test.com/1")
    mycursor.execute(insert, val)
    id_number = mycursor.lastrowid
    insert = "INSERT INTO employees (first_name, last_name, email, department) VALUES (%s, %s, %s, %s)"
    val = ("Python", "Testson", "smartcitysns@gmail.com", "Vehicle Damage")
    mycursor.execute(insert, val)
    employee_id_number = mycursor.lastrowid
    test_body = {
        "id": id_number,
        "current_status": "Open",
        "employee_id": employee_id_number
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b"'current_status' must not be the same as 'previous_status'"
    mycursor.execute(f"DELETE FROM problems WHERE id = {id_number}")
    mycursor.execute(f"DELETE FROM employees WHERE id = {employee_id_number}")

def test_invalid_employee_department(mysql_cursor):
    mycursor = mysql_cursor
    insert = "INSERT INTO problems (problem_type, problem_description, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    val = ("Criminal Act", f"{prefix}-test2", -87.63591557318675, 41.8788793748167, "https://www.test.com/2")
    mycursor.execute(insert, val)
    id_number = mycursor.lastrowid
    insert = "INSERT INTO employees (first_name, last_name, email, department) VALUES (%s, %s, %s, %s)"
    val = ("Jack", "Sparrow", "smartcitysns@gmail.com", "Fire")
    mycursor.execute(insert, val)
    employee_id_number = mycursor.lastrowid
    test_body = {
        "id": id_number,
        "current_status": "In Progress",
        "employee_id": employee_id_number
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b'The employee selected must be in the same department as the specific problem. (Employee department: Fire, Specific problem: Criminal Act)'
    mycursor.execute(f"DELETE FROM problems WHERE id = {id_number}")
    mycursor.execute(f"DELETE FROM employees WHERE id = {employee_id_number}")

def test_open_to_in_progress(mysql_cursor): # update employee & problem + log
    mycursor = mysql_cursor
    insert = "INSERT INTO problems (problem_type, problem_description, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    val = ("Road Hazard", f"{prefix}-test3", 143.81887088450154, -39.6727277630872, "https://www.test.com/3")
    mycursor.execute(insert, val)
    id_number = mycursor.lastrowid
    insert = "INSERT INTO employees (first_name, last_name, email, department) VALUES (%s, %s, %s, %s)"
    val = ("Neo", "Anderson", "smartcitysns@gmail.com", "Road Hazard")
    mycursor.execute(insert, val)
    employee_id_number = mycursor.lastrowid
    test_body = {
        "id": id_number,
        "current_status": "In Progress",
        "employee_id": employee_id_number
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    time.sleep(3)
    assert response.status == 200
    assert response.data == b'Success! ID ' + str(id_number).encode() + b' updated to ' + 'In Progress'.encode()
    mycursor.execute(f"SELECT current_status FROM problems WHERE id = {id_number}")
    assert mycursor.fetchone()[0] == "In Progress"
    mycursor.execute(f"SELECT current_status FROM logs_history WHERE problem_id = {id_number}")
    assert mycursor.fetchone()[0] == "In Progress"
    mycursor.execute(f"SELECT current_assignment_id FROM employees WHERE id = {employee_id_number}")
    assert mycursor.fetchone()[0] == id_number
    mycursor.execute(f"DELETE FROM problems WHERE id = {id_number}")
    mycursor.execute(f"DELETE FROM employees WHERE id = {employee_id_number}")

def test_in_progress_to_open(mysql_cursor): # update employee & problem + log
    mycursor = mysql_cursor
    insert = "INSERT INTO problems (problem_type, problem_description, current_status, location, image_path) VALUES (%s, %s, %s, point(%s, %s), %s)"
    val = ("Environmental Hazard", f"{prefix}-test4", "In Progress", -115.80402207445665, 37.25147866186036, "https://www.test.com/4")
    mycursor.execute(insert, val)
    id_number = mycursor.lastrowid
    insert = "INSERT INTO employees (first_name, last_name, email, department, current_assignment_id) VALUES (%s, %s, %s, %s, %s)"
    val = ("John", "Wick", "smartcitysns@gmail.com", "Environmental Hazard", id_number)
    mycursor.execute(insert, val)
    employee_id_number = mycursor.lastrowid
    test_body = {
        "id": id_number,
        "current_status": "Open",
        "employee_id": employee_id_number
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    time.sleep(3)
    assert response.status == 200
    assert response.data == b'Success! ID ' + str(id_number).encode() + b' updated to ' + 'Open'.encode()
    mycursor.execute(f"SELECT current_status FROM problems WHERE id = {id_number}")
    assert mycursor.fetchone()[0] == "Open"
    mycursor.execute(f"SELECT current_status FROM logs_history WHERE problem_id = {id_number}")
    assert mycursor.fetchone()[0] == "Open"
    mycursor.execute(f"SELECT current_assignment_id FROM employees WHERE id = {employee_id_number}")
    assert mycursor.fetchone()[0] == None
    mycursor.execute(f"DELETE FROM problems WHERE id = {id_number}")
    mycursor.execute(f"DELETE FROM employees WHERE id = {employee_id_number}")

def test_open_to_complete(mysql_cursor): # update employee & problem + log
    mycursor = mysql_cursor
    insert = "INSERT INTO problems (problem_type, problem_description, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    val = ("Vehicle Damage", f"{prefix}-test5", -69.98550144236036, 12.47001091411405, "https://www.test.com/5")
    mycursor.execute(insert, val)
    id_number = mycursor.lastrowid
    insert = "INSERT INTO employees (first_name, last_name, email, department) VALUES (%s, %s, %s, %s)"
    val = ("Michael", "Jordan", "smartcitysns@gmail.com", "Vehicle Damage")
    mycursor.execute(insert, val)
    employee_id_number = mycursor.lastrowid
    test_body = {
        "id": id_number,
        "current_status": "Complete",
        "employee_id": employee_id_number
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    time.sleep(3)
    assert response.status == 200
    assert response.data == b'Success! ID ' + str(id_number).encode() + b' updated to ' + 'Complete'.encode()
    mycursor.execute(f"SELECT COUNT(*) FROM problems WHERE id = {id_number}")
    assert mycursor.fetchone()[0] == 0 # should be deleted from problems table
    mycursor.execute(f"SELECT current_status FROM logs_history WHERE problem_id = {id_number}")
    assert mycursor.fetchone()[0] == "Complete"
    mycursor.execute(f"SELECT current_assignment_id FROM employees WHERE id = {employee_id_number}")
    assert mycursor.fetchone()[0] == None
    mycursor.execute(f"DELETE FROM employees WHERE id = {employee_id_number}")

def test_in_progress_to_complete(mysql_cursor): # update employee & problem + log
    mycursor = mysql_cursor
    insert = "INSERT INTO problems (problem_type, problem_description, current_status, location, image_path) VALUES (%s, %s, %s, point(%s, %s), %s)"
    val = ("Criminal Act", f"{prefix}-test6", "In Progress", -109.34968353475654, -27.112724007216986, "https://www.test.com/6")
    mycursor.execute(insert, val)
    id_number = mycursor.lastrowid
    insert = "INSERT INTO employees (first_name, last_name, email, department, current_assignment_id) VALUES (%s, %s, %s, %s, %s)"
    val = ("George", "Washington", "smartcitysns@gmail.com", "Criminal Act", id_number)
    mycursor.execute(insert, val)
    employee_id_number = mycursor.lastrowid
    test_body = {
        "id": id_number,
        "current_status": "Complete",
        "employee_id": employee_id_number
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    time.sleep(3)
    assert response.status == 200
    assert response.data == b'Success! ID ' + str(id_number).encode() + b' updated to ' + 'Complete'.encode()
    mycursor.execute(f"SELECT COUNT(*) FROM problems WHERE id = {id_number}")
    assert mycursor.fetchone()[0] == 0 # should be deleted from problems table
    mycursor.execute(f"SELECT current_status FROM logs_history WHERE problem_id = {id_number}")
    assert mycursor.fetchone()[0] == "Complete"
    mycursor.execute(f"SELECT current_assignment_id FROM employees WHERE id = {employee_id_number}")
    assert mycursor.fetchone()[0] == None
    mycursor.execute(f"DELETE FROM employees WHERE id = {employee_id_number}")