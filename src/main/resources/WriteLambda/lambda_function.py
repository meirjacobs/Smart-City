import mysql.connector
import json
import base64
import boto3
import botocore.config
import datetime
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
    sm = boto3.client("secretsmanager")
    secret = sm.get_secret_value(SecretId='test/MySQL')
    credentials = json.loads(secret['SecretString'])
    mydb = mysql.connector.connect(
        host=credentials['host'],
        user=credentials['user'],
        password=credentials['password'],
        database=credentials['dbname']
    )

    # get id number
    mycursor = mydb.cursor()
    mycursor.execute("SELECT MAX(id) FROM Smart_City")
    id_number = mycursor.fetchall()[0][0] + 1

    # upload images to new folder in S3 Bucket
    counter = 0
    s3 = boto3.client('s3', 'us-east-1', config=botocore.config.Config(s3={'addressing_style': 'path'}))
    for img in jsonbody["image_path"]:
        file_name = f'img{counter}.jpg'
        lambda_path = f'{id_number}/{file_name}'

        img = base64.b64decode(jsonbody["image_path"][counter])  # decode the encoded image data (base64)

        # bucket.put_object(Key=lambda_path, Body=img)
        s3.put_object(Bucket=os.environ['BUCKET_NAME'], Key=lambda_path, Body=img)
        counter += 1

    # insert data into database
    insert = "INSERT INTO Smart_City (problem_type, problem_description, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    val = (jsonbody["problem_type"], jsonbody["problem_description"], jsonbody["location"][0], jsonbody["location"][1],
           "https://s3.console.aws.amazon.com/s3/buckets/smartcitytestbucket?region=us-east-1&prefix=" + str(
               id_number) + "/")
    mycursor.execute(insert, val)
    mydb.commit()

    # sns_client = boto3.client('sns', region_name=region)
    # sns_client.publish(TopicArn=topic_arn, Message=message, MessageAttributes=message_attributes)
    # client = boto3.client('sns')
    # response = client.publish(
    #  TopicArn=os.environ['SNS_TOPIC'],
    #  Message="Problem Type: " + jsonbody['problem_type'] + "\nProblem Description: " + jsonbody['problem_description'] + "\nLocation: " + str(jsonbody["location"][0]) + ", " + str(jsonbody["location"][1]),
    #  Subject="New Issue Report"
    # )

    return {
        'statusCode': 200,
        'body': "Success"
    }