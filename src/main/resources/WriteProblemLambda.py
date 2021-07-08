import base64
import datetime
import json
import boto3
import botocore.config
import mysql.connector

def lambda_handler(event, context):
    
    # check input to ensure it is valid

    if len(event) != 4:
        s = ""
        for item in event:
            s = s + '\n' + item + ": " + str(event[item])
        return {
            'statusCode': 400,
            'body': "Four items required. Received " + str(len(event)) + "\n\nInput = " + s
        }
    
    problem_type_list = ['Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire', 'Water Damage', 'Other']
    if "problem_type" not in event or event["problem_type"] not in problem_type_list:
        return {
            'statusCode': 400,
            'body': "'problem_type' is a required field and must be 'Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire', 'Water Damage', or 'Other'"
        }
    
    if "problem_description" not in event or not isinstance(event["problem_description"], str):
        return {
            'statusCode': 400,
            'body': "'problem_description' is a required field and must be of type string"
        }
    
    if "location" not in event or not isinstance(event["location"], list) or len(event["location"]) != 2 or not all(isinstance(i, float) for i in event["location"]) or not -90 <= event["location"][0] <= 90 or not -180 <= event["location"][1] <= 180:
        return {
            'statusCode': 400,
            'body': "'location' is a required field which takes a list of two points, both of type float. The first represents the latitude (which must be a number between -90 and 90) and the second represents the longitude (which must be a number between -180 and 180)"
        }
        
    if "image_path" not in event or not isinstance(event["image_path"], list) or not all(isinstance(i, str) for i in event["image_path"]):
        return {
            'statusCode': 400,
            'body': "'image_path' is a required field which must be a list of strings"
        }
    
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
    mycursor = mydb.cursor()
    
    # get id number
    mycursor.execute(f"SELECT AUTO_INCREMENT FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{credentials['dbname']}' AND TABLE_NAME = 'problems'")
    id_number = mycursor.fetchall()[0][0]

    # upload images to new folder in S3 Bucket
    counter = 0
    s3_client = boto3.client('s3', 'us-east-1', config=botocore.config.Config(s3={'addressing_style':'path'}))
    for img in event["image_path"]:
        file_name = f'img{counter}.jpg'
        lambda_path = f'{id_number}/{file_name}'
        img = base64.b64decode(event["image_path"][counter])
        s3_client.put_object(Bucket="smartcitytestbucket", Key=lambda_path, Body=img)
        counter += 1
    
    # prepare and insert problem into problems table
    image_path = f'https://s3.console.aws.amazon.com/s3/buckets/smartcitytestbucket?region=us-east-1&prefix={id_number}/'
    
    insert = "INSERT INTO problems (problem_type, problem_description, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    val = (event["problem_type"], event["problem_description"], event["location"][1], event["location"][0], image_path)
    mycursor.execute(insert, val)
    mydb.commit()
    
    # prepare and insert data for logs_history table
    event['id_number'] = id_number
    mycursor.execute(f"SELECT time_found FROM problems WHERE id = {id_number}")
    event['time_found'] = str(mycursor.fetchall()[0][0])
    event['current_status'] = "Open"
    event['previous_status'] = None
    event['assigned_employee_id'] = None
    event['image_path'] = image_path
    
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
        FunctionName='arn:aws:lambda:us-east-1:287420233372:function:LogLambda',
        InvocationType='Event',
        Payload=json.dumps(event)
    )
    
    return {
        'statusCode' : 200,
        'response': "Success, problem ticket uploaded. An employee will soon take care of the issue."
    }