import json

import boto3

import mysql.connector
import smart_city

event_body = None
mydb = None
mycursor = None

def lambda_handler(event, context):

    global event_body
    event_body = json.loads(event["body"])

    # check input to ensure it is valid
    invalid_size = validate_input_size()
    if invalid_size:
        return invalid_size
    
    # connect to MySQL
    global mydb
    global mycursor    
    mydb, mycursor = smart_city.db_connect()

    # check input to ensure it is valid
    invalid = validate_input()
    if invalid:
        return invalid
    
    # prepare event_body variable for LogProblem & next validations
    prepare_data()

    invalid_request = validate_request()
    if invalid_request:
        return invalid_request

    return update_tables()

def validate_input_size():
    # check input size to ensure it is valid
    if len(event_body) != 3:
        return {
            'statusCode': 400,
            'body': f'Three items required. Received {len(event_body)}.\nInput: {json.dumps(event_body)}'
        }
    
def validate_input():

    # validate problem id
    id_number = event_body["id"]
    if not isinstance(id_number, int):
        return {
            'statusCode': 400,
            'body': "The ID must be of type int"
        }
    mycursor.execute("SELECT id FROM problems")
    id_data = mycursor.fetchall()
    id_list = [i[0] for i in id_data]
    if id_number not in id_list:
        return {
            'statusCode': 400,
            'body': "The ID you requested is not in the problems table"
        }
    
    # validate employee id
    employee_id = event_body["employee_id"]
    if not isinstance(employee_id, int):
        return {
            'statusCode': 400,
            'body': "The ID must be of type int"
        }
    mycursor.execute("SELECT id FROM employees")
    employee_id_data = mycursor.fetchall()
    employee_id_list = [i[0] for i in employee_id_data]
    if employee_id not in employee_id_list:
        return {
            'statusCode': 400,
            'body': f"The ID you requested is not in the employees table"
        }

    # validate current_status
    status_list = ['Open', 'In Progress', 'Complete']
    if event_body['current_status'] not in status_list:
        return {
            'statusCode': 400,
            'body': "'current_status' must be set to 'Open', 'In Progress', or 'Complete'"
        }

def prepare_data():
    mycursor.execute(f'SELECT * FROM problems WHERE id = {event_body["id"]}')
    data = mycursor.fetchall()[0]
    event_body['id_number'] = data[0]
    event_body['problem_type'] = data[1]
    event_body['problem_description'] = data[2]
    event_body['time_found'] = str(data[3])
    event_body['previous_status'] = data[4]
    event_body['image_path'] = data[6]
    mycursor.execute(f'SELECT ST_AsText(location) AS coordinates FROM problems WHERE id = {event_body["id"]}')
    location = mycursor.fetchall()[0][0]
    location_list = location[6:-1].split()
    event_body["location"] = location_list
    event_body["assigned_employee_id"] = event_body["employee_id"]

def validate_request():

    # ensure current_status is not equivalent to previous_status
    if event_body['current_status'] == event_body['previous_status']:
        return {
            'statusCode': 400,
            'body': "'current_status' must not be the same as 'previous_status'"
        }

    # ensure selected employee has the same department as problem
    mycursor.execute(f"SELECT department FROM employees WHERE id = {event_body['employee_id']}")
    employee_department = mycursor.fetchall()[0][0]
    if event_body["problem_type"] != employee_department:
        return {
            'statusCode': 400,
            'body': f'The employee selected must be in the same department as the specific problem. (Employee department: {employee_department}, Specific problem: {event_body["problem_type"]})'
        }

def update_tables():
 
    # update status and current_assignment_id in problems and employees table 
    lambda_client = boto3.client('lambda')
    id_to_delete = {"id": event_body['id']}
    
    if event_body["previous_status"] == 'Open':
        # updating status to Complete
        if event_body["current_status"] == 'Complete':
            lambda_client.invoke(
                FunctionName='CloudFormation-DeleteProblem',
                InvocationType='Event',
                Payload=json.dumps(id_to_delete)
            )
        # updating status to Open
        elif event_body["current_status"] == 'In Progress':
            mycursor.execute(f"SELECT current_assignment_id FROM employees WHERE id = {event_body['employee_id']}")
            assignment_id = mycursor.fetchall()[0][0]
            if assignment_id != None:
                return {
                    'statusCode': 400,
                    'body': 'The employee is currently busy, please try another employee'
                }
            mycursor.execute(f'UPDATE employees SET current_assignment_id = {event_body["id"]} where id = {event_body["employee_id"]}')
            mycursor.execute(f'UPDATE problems SET current_status = "{event_body["current_status"]}" WHERE id = {event_body["id"]}')

    if event_body["previous_status"] == 'In Progress':
        # updating status to Complete
        if event_body["current_status"] == "Complete":
            mycursor.execute(f'UPDATE employees SET current_assignment_id = NULL where id = {event_body["employee_id"]}')
            lambda_client = boto3.client('lambda')
            lambda_client.invoke(
                FunctionName='CloudFormation-DeleteProblem',
                InvocationType='Event',
                Payload=json.dumps(id_to_delete)
            )
        # updating status to Open
        elif event_body["current_status"] == 'Open':
            mycursor.execute(f'UPDATE employees SET current_assignment_id = NULL where id = {event_body["employee_id"]}')
            mycursor.execute(f'UPDATE problems SET current_status = "{event_body["current_status"]}" WHERE id = {event_body["id"]}')
    
    mydb.commit()
    mycursor.close()
    mydb.close()
    
    # insert log to logs_history
    lambda_client.invoke(
        FunctionName='CloudFormation-LogProblem',
        InvocationType='Event',
        Payload=json.dumps(event_body)
    )
    
    return {
        'statusCode' : 200,
        'body': f'Success! ID {event_body["id_number"]} updated to {event_body["current_status"]}'
    }