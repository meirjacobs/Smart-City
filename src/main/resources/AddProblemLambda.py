import base64
import datetime
import json
import os

import boto3
import botocore.config

import mysql.connector
import smart_city

event_body = None
mydb = None
mycursor = None
lambda_client = None

def lambda_handler(event, context):

    global event_body
    event_body = json.loads(event["body"])

    # check input to ensure it is valid
    invalid = validate_input()
    if invalid:
        return invalid

    # connect to MySQL
    global mydb
    global mycursor
    mydb, mycursor = smart_city.db_connect()

    # get id number
    event_body["id_number"] = get_id_number()
    
    # upload images to new folder in S3 Bucket
    event_body["image_path"] = upload_images()

    # prepare and insert problem into problems table
    insert_problem()
    
    global lambda_client
    lambda_client = boto3.client('lambda')

    # email employees in the specific department of this issue
    email_employees()

    # prepare and insert data into logs_history table
    log_problem()

    mycursor.close()
    mydb.close()

    return {
        'statusCode': 200,
        'body': "Success, problem ticket uploaded. An employee will soon take care of the issue."
    }

def validate_input():
    if len(event_body) != 4:
        return {
            'statusCode': 400,
            'body': f'Four items required. Received {len(event_body)}.\nInput: {json.dumps(event_body)}'
        }

    problem_type_list = ['Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire', 'Water Damage', 'Other']
    if "problem_type" not in event_body or event_body["problem_type"] not in problem_type_list:
        return {
            'statusCode': 400,
            'body': "'problem_type' is a required field and must be 'Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire', 'Water Damage', or 'Other'"
        }

    if "problem_description" not in event_body or not isinstance(event_body["problem_description"], str):
        return {
            'statusCode': 400,
            'body': "'problem_description' is a required field and must be of type string"
        }

    if "location" not in event_body or not isinstance(event_body["location"], list) or len(event_body["location"]) != 2 or not all(isinstance(i, float) for i in event_body["location"]) or not -90 <= event_body["location"][0] <= 90 or not -180 <= event_body["location"][1] <= 180:
        return {
            'statusCode': 400,
            'body': "'location' is a required field which takes a list of two points, both of type float. The first represents the latitude (which must be a number between -90 and 90) and the second represents the longitude (which must be a number between -180 and 180)"
        }

    if "image_path" not in event_body or not isinstance(event_body["image_path"], list) or not all(isinstance(i, str) for i in event_body["image_path"]):
        return {
            'statusCode': 400,
            'body': "'image_path' is a required field which must be a list of strings"
        }

def get_id_number():
    mycursor.execute(f"SHOW CREATE TABLE problems")
    id_number = mycursor.fetchall()[0][1]
    if len(id_number) == 512:
        return 1
    else:
        return int(id_number[477:-51])

def upload_images():
    if event_body["image_path"][0] == "":
        return None

    bucket = os.environ["BUCKET_NAME"]
    
    counter = 0
    s3_client = boto3.client('s3')
    for img in event_body["image_path"]:
        file_name = f'img{counter}.jpg'
        file_path = f'{event_body["id_number"]}/{file_name}'
        img = base64.b64decode(event_body["image_path"][counter])
        s3_client.put_object(Bucket=bucket, Key=file_path, Body=img)
        counter += 1
    return f'https://s3.console.aws.amazon.com/s3/buckets/{bucket}?prefix={event_body["id_number"]}/'

def insert_problem():
    insert = "INSERT INTO problems (problem_type, problem_description, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    val = (event_body["problem_type"], event_body["problem_description"], event_body["location"][1], event_body["location"][0], event_body["image_path"])
    mycursor.execute(insert, val)
    mydb.commit()

def email_employees():
    mycursor.execute(f"SELECT email FROM employees WHERE current_assignment_id IS null AND department = '{event_body['problem_type']}'")
    employees_email_list = [employee_email[0] for employee_email in mycursor.fetchall()]
    location_url = f'https://www.google.com/maps/search/?api=1&query={event_body["location"][0]}%2C{event_body["location"][1]}'
    message = \
    f"""The following issue has just been uploaded to our system and to all available employees who work in Department: {event_body['problem_type']}.
    Please take a look at the issue, its details, and decide if you can take it on.
    ID: {event_body["id_number"]}
    Problem Type: {event_body['problem_type']}
    Description: {event_body['problem_description']}
    Location: {location_url}""".replace("\n    ","\n")
   
    if len(employees_email_list) != 0:
        email_event = {
            "id_number": event_body["id_number"],
            "email_list": employees_email_list,
            "subject": f"New {event_body['problem_type']} Issue Uploaded", 
            "message": message
        }
        lambda_client.invoke(
            FunctionName='CloudFormation-Emailer',
            InvocationType='Event',
            Payload=json.dumps(email_event)
        )
    
def log_problem():
    mycursor.execute(f"SELECT time_found FROM problems WHERE id = {event_body['id_number']}")
    event_body['time_found'] = str(mycursor.fetchall()[0][0])
    event_body['current_status'] = "Open"
    event_body['previous_status'] = None
    event_body['assigned_employee_id'] = None

    lambda_client.invoke(
        FunctionName='CloudFormation-LogProblem',
        InvocationType='Event',
        Payload=json.dumps(event_body)
    )