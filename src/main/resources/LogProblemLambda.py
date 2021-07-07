import datetime
import json
import boto3
import mysql.connector

def lambda_handler(event, context):
    
    # connect to MySQL
    sm_client = boto3.client("secretsmanager")
    secret = sm_client.get_secret_value(SecretId='test/MySQL')
    credentials = json.loads(secret['SecretString'])
    mydb = mysql.connector.connect(
        host=credentials['host'],
        user=credentials['user'],
        password=credentials['password'],
        database=credentials['dbname']
    )
    
    # insert log into logs_history table
    insert = "INSERT INTO logs_history (problem_id, problem_type, problem_description, time_found, current_status, previous_status,assigned_employee_id, location, image_path) VALUES (%s, %s, %s, %s, %s, %s,%s,  point(%s, %s), %s)"
    val = (event["id_number"], event["problem_type"], event["problem_description"], event["time_found"], event["current_status"], event["previous_status"],event["assigned_employee_id"], event["location"][0], event["location"][1], event["image_path"])
    mycursor = mydb.cursor()
    mycursor.execute(insert, val)
    mydb.commit()

    return {
        'statusCode' : 200,
        'response': "Success, logs updated"
    }