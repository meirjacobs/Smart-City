import json

import boto3
import urllib3

import mysql.connector

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
    mysql_connect()

    # ensure email is unique within database
    invalid_email = validate_email()
    if invalid_email:
        return invalid_email
    
    # insert employee into employees table
    insert_employee()

    return {
        'statusCode' : 200,
        'response': f"Success, inserted {event_body['first_name']} {event_body['last_name']} into table"
    }

def validate_input():
    if len(event_body) != 4:
        return {
            'statusCode': 400,
            'body': f'Four items requires. Received {len(event_body)}.\nInput: {json.dumps(event_body)}'
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
   
    department_list = ['Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire', 'Water Damage', 'Other']
    if "department" not in event_body or event_body["department"] not in department_list:
        return {
            'statusCode': 400,
            'body': "'department' is a required field and must be 'Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire', 'Water Damage', or 'Other'"
        }

def mysql_connect():
    sm_client = boto3.client("secretsmanager")
    secret = sm_client.get_secret_value(SecretId='MySQL-Credentials')
    credentials = json.loads(secret['SecretString'])
    global mydb
    mydb = mysql.connector.connect(
        host=credentials['host'],
        user=credentials['username'],
        password=credentials['password'],
        database=credentials['dbname']
    )
    global mycursor
    mycursor = mydb.cursor()

def validate_email():
    mycursor.execute(f'SELECT * FROM employees WHERE email = "{event_body["email"]}"')
    present = mycursor.fetchall()
    if present:
        return {
            'statusCode': 400,
            'body': "The email you entered already exists in this table."
        }

def insert_employee():
    insert = "INSERT INTO employees (first_name, last_name, email, department) VALUES (%s, %s, %s, %s)"
    val = (event_body["first_name"], event_body["last_name"], event_body["email"], event_body["department"])
    mycursor.execute(insert, val)
    mydb.commit()