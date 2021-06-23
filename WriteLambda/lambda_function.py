import mysql.connector
import json
import base64
import boto3
import datetime

def lambda_handler(event, context):
    
    # check input to ensure it is valid
    
    if len(event) != 5:
        s = ""
        for item in event:
            s = s + '\n' + item + ": " + str(event[item])
        return {
            'statusCode': 400,
            'body': "Five items required. Received " + str(len(event)) + "\n\nInput = " + s
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
        
    if "time_found" not in event or not isinstance(event["time_found"], str):
        return {
            'statusCode': 400,
            'body': "'time_found' is a required field"
        }
    else:
        try:
            datetime.datetime.strptime(event["time_found"], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return {
                'statusCode': 400,
                'body': "'time_found' must be formatted as follows: YYYY-MM-DD HH:MM:SS"
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
    client = boto3.client("secretsmanager")
    secret = client.get_secret_value(SecretId='test/MySQL')
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
    id_number = mycursor.fetchall()[0][0]+1
    
    # upload images to new folder in S3 Bucket
    counter = 0
    print(74)
    s3 = boto3.resource("s3")
    print(76)
    bucket = s3.Bucket("smartcitytestbucket")
    print(78)
    for img in event["image_path"]:
        file_name = "img" + str(counter) + ".jpg"
        lambda_path = str(id_number) + "/" + file_name
        print(82)
        
        img = base64.b64decode(event["image_path"][counter])     # decode the encoded image data (base64)
        print(85)
        
        bucket.put_object(Key=lambda_path, Body=img)
        counter += 1
        print(89)
    
    # insert data into database
    insert = "INSERT INTO Smart_City (problem_type, problem_description, time_found, location, image_path) VALUES (%s, %s, %s, point(%s, %s), %s)"
    val = (event["problem_type"], event["problem_description"], event["time_found"], event["location"][0], event["location"][1], "https://s3.console.aws.amazon.com/s3/buckets/smartcitytestbucket?region=us-east-1&prefix=" + str(id_number) + "/")
    mycursor.execute(insert, val)
    mydb.commit()


    return {
        'statusCode' : 200,
        'response': "Success"
    }