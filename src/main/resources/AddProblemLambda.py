import base64
import datetime
import json

import boto3
import botocore.config

import mysql.connector

def lambda_handler(event, context):

    jsonbody = json.loads(event["body"])

    # check input to ensure it is valid

    if len(jsonbody) != 4:
        return {
            'statusCode': 400,
            'body': f'Four items requires. Received {len(event)}. \n Input: {json.dumps(event)}'
        }

    problem_type_list = ['Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire', 'Water Damage', 'Other']
    if "problem_type" not in jsonbody or jsonbody["problem_type"] not in problem_type_list:
        return {
            'statusCode': 400,
            'body': "'problem_type' is a required field and must be 'Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire', 'Water Damage', or 'Other'"
        }

    if "problem_description" not in jsonbody or not isinstance(jsonbody["problem_description"], str):
        return {
            'statusCode': 400,
            'body': "'problem_description' is a required field and must be of type string"
        }

    if "location" not in jsonbody or not isinstance(jsonbody["location"], list) or len(jsonbody["location"]) != 2 or not all(isinstance(i, float) for i in jsonbody["location"]) or not -90 <= jsonbody["location"][0] <= 90 or not -180 <= jsonbody["location"][1] <= 180:
        return {
            'statusCode': 400,
            'body': "'location' is a required field which takes a list of two points, both of type float. The first represents the latitude (which must be a number between -90 and 90) and the second represents the longitude (which must be a number between -180 and 180)"
        }

    if "image_path" not in jsonbody or not isinstance(jsonbody["image_path"], list) or not all(isinstance(i, str) for i in jsonbody["image_path"]):
        return {
            'statusCode': 400,
            'body': "'image_path' is a required field which must be a list of strings"
        }

    # connect to MySQL
    sm_client = boto3.client("secretsmanager")
    secret = sm_client.get_secret_value(SecretId='MySQL-Credentials')
    credentials = json.loads(secret['SecretString'])
    mydb = mysql.connector.connect(
        host=credentials['host'],
        user=credentials['username'],
        password=credentials['password'],
        database=credentials['dbname']
    )
    mycursor = mydb.cursor()

    # get id number
    mycursor.execute(f"SHOW CREATE TABLE problems")
    id_number = mycursor.fetchall()[0][1]
    if len(id_number) == 521:
        id_number = 1
    else:
        id_number = int(id_number[486:-51])

    # upload images to new folder in S3 Bucket
    counter = 0
    s3_client = boto3.client('s3')
    for img in jsonbody["image_path"]:
        file_name = f'img{counter}.jpg'
        lambda_path = f'{id_number}/{file_name}'
        img = base64.b64decode(jsonbody["image_path"][counter])
        s3_client.put_object(Bucket="smart-city-s3-bucket", Key=lambda_path, Body=img)
        counter += 1

    # prepare and insert problem into problems table
    image_path = f'https://s3.console.aws.amazon.com/s3/buckets/smart-city-s3-bucket?region=us-east-1&prefix={id_number}/'

    insert = "INSERT INTO problems (problem_type, problem_description, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    val = (jsonbody["problem_type"], jsonbody["problem_description"], jsonbody["location"][1], jsonbody["location"][0],
           image_path)
    mycursor.execute(insert, val)
    mydb.commit()

    # email employees in the specific department of this issue
    mycursor.execute(f"SELECT email FROM employees WHERE current_assignment_id IS null AND department = '{event['problem_type']}'")
    employees_email_list = [employee_email[0] for employee_email in mycursor.fetchall()]
    location_url = f'https://www.google.com/maps/search/?api=1&query={event["location"][0]}%2C{event["location"][1]}'    
    message = \
    f"""The following issue has just been uploaded to our system and to all available employees who work in Department: {event['problem_type']}.
    Please take a look at the issue, its details, and decide if you can take it on.
    ID: {id_number}
    Location: {location_url}
    Problem Type: {event['problem_type']}
    Description: {event['problem_description']}"""
    lambda_client = boto3.client('lambda')
    if len(employees_email_list) != 0:
        email_event = {"email_list": employees_email_list,"subject": f"New {event['problem_type']} Issue Uploaded", "message": message}
        lambda_client.invoke(
            FunctionName='CloudFormation-Emailer',
            InvocationType='Event',
            Payload=json.dumps(email_event)
        )

    # prepare and insert data for logs_history table
    jsonbody['id_number'] = id_number
    mycursor.execute(f"SELECT time_found FROM problems WHERE id = {id_number}")
    jsonbody['time_found'] = str(mycursor.fetchall()[0][0])
    jsonbody['current_status'] = "Open"
    jsonbody['previous_status'] = None
    jsonbody['assigned_employee_id'] = None
    jsonbody['image_path'] = image_path

    lambda_client.invoke(
        FunctionName='CloudFormation-LogLambda',
        InvocationType='Event',
        Payload=json.dumps(jsonbody)
    )

    return {
        'statusCode': 200,
        'body': "Success, problem ticket uploaded. An employee will soon take care of the issue."
    }