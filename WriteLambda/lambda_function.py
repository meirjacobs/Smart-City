import mysql.connector
import json
import base64
import boto3

def lambda_handler(event, context):
    
    # check input to ensure it is valid
    if len(event) != 4:
        s = ""
        for x in event:
            s = s + '\n' + x + ": " + str(event[x])
        return {
            'statusCode': 400,
            'body': "Four items required. Received " + str(len(event)) + "\n\nInput = " + s
        }
    elif event["problem"] == None:
        return {
            'statusCode': 400,
            'body': "Problem is a required field"
        }
    elif event["time_found"] == None:
        return {
            'statusCode': 400,
            'body': "Time Found is a required field"
        }
    elif event["location"] == None:
        return {
            'statusCode': 400,
            'body': "Location is a required field"
        }
    elif event["image_path"] == None:
        return {
            'statusCode': 400,
            'body': "Image Path is a required field"
        }
    
    # connect to MySQL
    mydb = mysql.connector.connect(
        host="smart-city-rds-0.ccmkepymppq8.us-east-1.rds.amazonaws.com",
        user="admin",
        password="Tester123",
        database="Smart_City_0"
    )
    
    # get id number
    mycursor = mydb.cursor()
    mycursor.execute("SELECT MAX(id) FROM Smart_City")
    id = mycursor.fetchall()[0][0]+1
    
    # upload images to new folder in S3 Bucket
    counter = 0
    s3 = boto3.resource("s3")
    bucket = s3.Bucket("smartcitytestbucket")
    for img in event["image_path"]:
        file_name = "img" + str(counter) + ".jpg"
        lambda_path = str(id) + "/" + file_name

        img = base64.b64decode(event["image_path"][counter])     # decode the encoded image data (base64)
        
        bucket.put_object(Key=lambda_path, Body=img)
        counter += 1
    
    # insert data into database
    insert = "INSERT INTO Smart_City (problem, time_found, location, image_path) VALUES (%s, %s, point(%s, %s), %s)"
    val = (event["problem"], event["time_found"], event["location"][0], event["location"][1], "https://s3.console.aws.amazon.com/s3/buckets/smartcitytestbucket?region=us-east-1&prefix=" + str(id) + "/");
    mycursor.execute(insert, val)
    mydb.commit()


    return {
        'response': "Success",
        'statusCode' : 200
    }