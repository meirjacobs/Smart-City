import json

import boto3

import mysql.connector

def lambda_handler(event, context):
    
    # check input to ensure it is valid
    if len(event) != 1:
        s = ""
        for item in event:
            s = s + '\n' + item + ": " + str(event[item])
        return {
            'statusCode': 400,
            'body': "One item required. Received " + str(len(event)) + "\n\nInput = " + s
        }
    
    if "id" not in event or not isinstance(event["id"], int):
        return {
            'statusCode': 400,
            'body': "'id' is a required field and must be of type int"
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

    # check input to ensure it is valid
    mycursor.execute("SELECT id FROM employees")
    id_data = mycursor.fetchall()
    id_list = [id[0] for id in id_data]
    id_number = event["id"]
    if id_number not in id_list:
        return {
            'statusCode': 400,
            'body': f"The ID {id_number} you requested is not in the database"
        }
        
    # store employee's data
    mycursor.execute(f'SELECT * FROM employees WHERE id = {id_number}')
    data = mycursor.fetchall()[0]

    # delete employee from employees table
    delete = f'DELETE FROM employees WHERE id = {id_number}'
    mycursor.execute(delete)
    mydb.commit()

    return {
        'statusCode' : 200,
        'response': f'Success, deleted: {data} from the table'
    }