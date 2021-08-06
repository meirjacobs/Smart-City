import json

import boto3

import mysql.connector
import smart_city

event_body = None
mydb = None
mycursor = None

def lambda_handler(event, context):

    global event_body
    event_body = event

    # check input to ensure it is valid
    validate_input()

    # connect to MySQL
    global mydb
    global mycursor
    mydb, mycursor = smart_city.db_connect()

    # delete problem from problems table & return whether delete was succesful or not
    return delete_problem()

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

def delete_problem():
    id_number = event_body["id"]
    mycursor.execute(f"DELETE from problems WHERE id = {id_number}")
    mydb.commit()
    
    effected_rows = mycursor.rowcount
    mycursor.close()
    mydb.close()
    if effected_rows == 0:
        return {
            'statusCode': 400,
            'body': f"ID {id_number} does not exist in table or has already been deleted"
        }
    else:
        return {
            'statusCode': 200,
            'body': f"ID {id_number} deleted succesfully"
        }