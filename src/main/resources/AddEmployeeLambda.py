import json

import boto3
import urllib3

import mysql.connector
import smart_city

event_body = None
mydb = None
mycursor = None

def lambda_handler(event, context):

    global event_body
    event_body = event

    # check input to ensure it is valid
    invalid = validate_input()
    if invalid:
        return invalid
    
    # connect to MySQL
    global mydb
    global mycursor
    mydb, mycursor = smart_city.db_connect()

    # ensure email is unique within database
    invalid_email = validate_email()
    if invalid_email:
        return invalid_email
    
    # insert employee into employees table
    insert_employee()

    mycursor.close()
    mydb.close()

    return {
        'statusCode' : 200,
        'body': f"Success, inserted {event_body['first_name']} {event_body['last_name']} into table"
    }

def validate_input():
    if len(event_body) != 5:
        return {
            'statusCode': 400,
            'body': f'Five items requires. Received {len(event_body)}.\nInput: {json.dumps(event_body)}'
        }
    
    if "first_name" not in event_body or not isinstance(event_body["first_name"], str):
        return {
            'statusCode': 400,
            'body': "'first_name' is a required field and must be of type string"
        }
        
    if "last_name" not in event_body or not isinstance(event_body["last_name"], str):
        return {
            'statusCode': 400,
            'body': "'last_name' is a required field and must be of type string"
        }
        
    if "email" not in event_body or not isinstance(event_body["email"], str):
        return {
            'statusCode': 400,
            'body': "'email' is a required field and must be of type string"
        }
    http = urllib3.PoolManager()
    email_address = event_body["email"]
    response = http.request(
        "GET",
        "https://isitarealemail.com/api/email/validate",
        fields = {'email': email_address}
    )
    status = json.loads(response.data)['status']
    if status != "valid":
        return {
            'statusCode': 400,
            'body': "The email you entered was not valid. Please try again."
        }
    
    if "pwd" not in event_body or not isinstance(event_body["pwd"], str):
        return {
            'statusCode': 400,
            'body': "'pwd' is a required field and must be of type string"
        }
        
   
    department_list = ['Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire', 'Water Damage', 'Other']
    if "department" not in event_body or event_body["department"] not in department_list:
        return {
            'statusCode': 400,
            'body': "'department' is a required field and must be 'Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire', 'Water Damage', or 'Other'"
        }

def validate_email():
    mycursor.execute(f'SELECT * FROM employees WHERE email = "{event_body["email"]}"')
    present = mycursor.fetchall()
    if present:
        return {
            'statusCode': 400,
            'body': "The email you entered already exists in this table."
        }

def insert_employee():
    insert = "INSERT INTO employees (first_name, last_name, email, pwd, department) VALUES (%s, %s, %s, %s, %s)"
    val = (event_body["first_name"], event_body["last_name"], event_body["email"], event_body["pwd"], event_body["department"])
    mycursor.execute(insert, val)
    mydb.commit()