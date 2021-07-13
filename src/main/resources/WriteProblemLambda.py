import base64
import datetime
import json
import boto3
import botocore.config
import mysql.connector
import os


def lambda_handler(event, context):
    jsonbody = json.loads(event["body"])

    # check input to ensure it is valid

    if len(jsonbody) != 4:
        s = ""
        for item in jsonbody:
            s = s + '\n' + item + ": " + str(jsonbody[item])
        return {
            'statusCode': 400,
            'body': "Four items required. Received " + str(len(jsonbody)) + "\n\nInput = " + s
        }

    problem_type_list = ['Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire',
                         'Water Damage', 'Other']
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

    if "location" not in jsonbody or not isinstance(jsonbody["location"], list) or len(
            jsonbody["location"]) != 2 or not all(isinstance(i, float) for i in jsonbody["location"]) or not -90 <= \
                                                                                                             jsonbody[
                                                                                                                 "location"][
                                                                                                                 0] <= 90 or not -180 <= \
                                                                                                                                 jsonbody[
                                                                                                                                     "location"][
                                                                                                                                     1] <= 180:
        return {
            'statusCode': 400,
            'body': "'location' is a required field which takes a list of two points, both of type float. The first represents the latitude (which must be a number between -90 and 90) and the second represents the longitude (which must be a number between -180 and 180)"
        }

    if "image_path" not in jsonbody or not isinstance(jsonbody["image_path"], list) or not all(
            isinstance(i, str) for i in jsonbody["image_path"]):
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
    s3_client = boto3.client('s3', 'us-east-1', config=botocore.config.Config(s3={'addressing_style': 'path'}))
    for img in jsonbody["image_path"]:
        file_name = f'img{counter}.jpg'
        lambda_path = f'{id_number}/{file_name}'
        img = base64.b64decode(jsonbody["image_path"][counter])
        s3_client.put_object(Bucket="smartcitys3bucket", Key=lambda_path, Body=img)
        counter += 1

    # prepare and insert problem into problems table
    image_path = f'https://s3.console.aws.amazon.com/s3/buckets/smartcitys3bucket?region=us-east-1&prefix={id_number}/'

    insert = "INSERT INTO problems (problem_type, problem_description, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    val = (jsonbody["problem_type"], jsonbody["problem_description"], jsonbody["location"][1], jsonbody["location"][0],
           image_path)
    mycursor.execute(insert, val)
    mydb.commit()

    # prepare and insert data for logs_history table
    jsonbody['id_number'] = id_number
    mycursor.execute(f"SELECT time_found FROM problems WHERE id = {id_number}")
    jsonbody['time_found'] = str(mycursor.fetchall()[0][0])
    jsonbody['current_status'] = "Open"
    jsonbody['previous_status'] = None
    jsonbody['assigned_employee_id'] = None
    jsonbody['image_path'] = image_path

    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
        FunctionName='CloudFormation-LogLambda',
        InvocationType='Event',
        Payload=json.dumps(jsonbody)
    )

    client = boto3.client('sns')
    response = client.publish(
        TopicArn=os.environ['SNS_TOPIC'],
        Message="Problem Type: " + jsonbody['problem_type'] + "\nProblem Description: " + jsonbody[
            'problem_description'] + "\nLocation: " + str(jsonbody["location"][0]) + ", " + str(
            jsonbody["location"][1]),
        Subject="New Issue Report"
    )

    return {
        'statusCode': 200,
        'body': "Success, problem ticket uploaded. An employee will soon take care of the issue."
    }