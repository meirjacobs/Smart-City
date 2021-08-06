import json
import logging

import urllib3
import boto3

import mysql.connector
import smart_city

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler (event, context):
    try:
        request_type = event['RequestType']
        if request_type == 'Create':
            response_data = create_tables()
        elif request_type == 'Update':
            response_data = create_tables()
        elif request_type == 'Delete':
            response_data = {"Data": "Deleted"}
        else:
            raise ValueError("request_type value must be either Create, Update or Delete")
        send(event, context, "SUCCESS", response_data)
    except Exception as e:
        send(event, context, "FAILED", {"exception": str(e)})

def create_tables():
    
    # connect to MySQL
    sm_client = boto3.client("secretsmanager")
    secret = sm_client.get_secret_value(SecretId='MySQL-Credentials')
    credentials = json.loads(secret['SecretString'])
    connection = mysql.connector.connect(
        host=credentials['host'],
        user=credentials['username'],
        password=credentials['password']
    )
    connection_cursor = connection.cursor()
    
    # create schema
    create_schema = "CREATE SCHEMA Smart_City"
    connection_cursor.execute(create_schema)
    
    # connect to database
    mydb, mycursor = smart_city.db_connect()
    
    # create tables
    create_problems = "CREATE TABLE problems (id int NOT NULL AUTO_INCREMENT, problem_type enum('Criminal Act','Environmental Hazard','Road Hazard','Vehicle Damage','Fire','Water Damage','Other') NOT NULL, problem_description text NOT NULL, time_found datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, current_status enum('Open','In Progress','Complete') NOT NULL DEFAULT 'Open', location point NOT NULL, image_path text, PRIMARY KEY (id))"
    create_employees = "CREATE TABLE employees (id int NOT NULL AUTO_INCREMENT, first_name text NOT NULL, last_name text NOT NULL, email text NOT NULL, pwd text NOT NULL, department enum('Criminal Act','Environmental Hazard','Road Hazard','Vehicle Damage','Fire','Water Damage','Other') NOT NULL, current_assignment_id int DEFAULT NULL, PRIMARY KEY (id))"
    create_logs = "CREATE TABLE logs_history (id int NOT NULL AUTO_INCREMENT, time_logged datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, problem_id int NOT NULL, problem_type enum('Criminal Act','Environmental Hazard','Road Hazard','Vehicle Damage','Fire','Water Damage','Other') NOT NULL, problem_description text NOT NULL, time_found datetime NOT NULL, current_status enum('Open','In Progress','Complete') NOT NULL, previous_status enum('Open','In Progress','Complete') DEFAULT NULL, assigned_employee_id int DEFAULT NULL, location point NOT NULL, image_path text, PRIMARY KEY (id))"
    mycursor.execute(create_problems)
    mycursor.execute(create_employees)
    mycursor.execute(create_logs)
    
    # verify that the tables are created
    mycursor.execute("SHOW TABLES LIKE 'problems'")
    problems_result = mycursor.fetchall()[0][0]
    mycursor.execute("SHOW TABLES LIKE 'employees'")
    employees_result = mycursor.fetchall()[0][0]
    mycursor.execute("SHOW TABLES LIKE 'logs_history'")
    logs_result = mycursor.fetchall()[0][0]
    mycursor.close()
    mydb.close()

    if problems_result == None or employees_result == None or logs_result == None:
        return {"Data": "Error: Tables were not created"}
    else:
        return {"Data": "Success! Schema and tables were created"}

# cfnresponse module source code taken from (with some slight alterations): https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-lambda-function-code-cfnresponsemodule.html
http = urllib3.PoolManager()
def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False, reason=None):
    responseUrl = event['ResponseURL']
    logger.info(responseUrl)
    responseBody = {
        'Status' : responseStatus,
        'Reason' : reason or "See the details in CloudWatch Log Stream: {}".format(context.log_stream_name),
        'PhysicalResourceId' : physicalResourceId or context.log_stream_name,
        'StackId' : event['StackId'],
        'RequestId' : event['RequestId'],
        'LogicalResourceId' : event['LogicalResourceId'],
        'NoEcho' : noEcho,
        'Data' : responseData
    }
    json_responseBody = json.dumps(responseBody)
    logger.info(f"Response body: {json_responseBody}")
    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }
    try:
        response = http.request('PUT', responseUrl, headers=headers, body=json_responseBody)
        logger.info(f"Status code: {response.status}")
    except Exception as e:
        logger.info(f"send(..) failed executing http.request(..): {e}")