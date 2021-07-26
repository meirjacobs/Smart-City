import json

import pytest
import urllib3

http = urllib3.PoolManager()
url = "https://rpixnvd51i.execute-api.us-east-1.amazonaws.com/deployedStage"

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

def test_invalid_status_type():
    test_body = {
        "id": 1,
        "current_status": 1,
        "employee_id": 1
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b"'current_status' must be set to 'Open', 'In Progress', or 'Complete'"

def test_invalid_employee_id_type():
    test_body = {
        "id": 1,
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

def test_invalid_status():
    test_body = {
        "id": 1,
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

def test_invalid_employee_id():
    test_body = {
        "id": 1,
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

def test_current_is_previous():
    test_body = {
        "id": 1,
        "current_status": "Open",
        "employee_id": 1
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b"'current_status' must not be the same as 'previous_status'"

def test_invalid_employee_department():
    test_body = {
        "id": 1,
        "current_status": "In Progress",
        "employee_id": 2
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 400
    assert response.data == b'The employee selected must be in the same department as the specific problem. (Employee department: Other, Specific problem: Criminal Act)'

def test_open_to_in_progress(): # update employee & problem + log
    test_body = {
        "id": 1,
        "current_status": "In Progress",
        "employee_id": 1
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 200
    assert response.data == b'Success! ID 1 updated to In Progress'

def test_in_progress_to_open(): # update employee & problem + log
    test_body = {
        "id": 1,
        "current_status": "Open",
        "employee_id": 1
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 200
    assert response.data == b'Success! ID 1 updated to Open'

def test_open_to_complete(): # update employee & problem + log
    test_body = {
        "id": 1,
        "current_status": "Complete",
        "employee_id": 1
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 200
    assert response.data == b'Success! ID 1 updated to Complete'

def test_in_progress_to_complete(): # update employee & problem + log
    prep_body = {
        "id": 2,
        "current_status": "In Progress",
        "employee_id": 1
    }
    http.request(
        "PUT",
        url,
        body = json.dumps(prep_body)
    )
    test_body = {
        "id": 2,
        "current_status": "Complete",
        "employee_id": 1
    }
    response = http.request(
        "PUT",
        url,
        body = json.dumps(test_body)
    )
    assert response.status == 200
    assert response.data == b'Success! ID 1 updated to Complete'