import json

import boto3

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

    # check id to ensure it is valid
    validate_id()

    # store employee's data
    mycursor.execute(f'SELECT * FROM employees WHERE id = {event_body["id"]}')
    data = mycursor.fetchall()[0]

    # delete employee from employees table
    delete_employee()

    return {
        'statusCode' : 200,
        'response': f'Success, deleted: {data} from the table'
    }

def validate_input():
    if len(event_body) != 1:
        return {
            'statusCode': 400,
            'body': f'One item required. Received {len(event_body)}.\nInput: {json.dumps(event_body)}'
        }
    
    if "id" not in event_body or not isinstance(event_body["id"], int):
        return {
            'statusCode': 400,
            'body': "'id' is a required field and must be of type int"
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

def validate_id():
    mycursor.execute("SELECT id FROM employees")
    id_data = mycursor.fetchall()
    id_list = [id[0] for id in id_data]
    id_number = event_body["id"]
    if id_number not in id_list:
        return {
            'statusCode': 400,
            'body': f"The ID {id_number} you requested is not in the database"
        }

def delete_employee():
    delete = f'DELETE FROM employees WHERE id = {event_body["id_number"]}'
    mycursor.execute(delete)
    mydb.commit()