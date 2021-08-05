import datetime
import json
import os

import boto3

import mysql.connector
import smart_city

event_body = None

def lambda_handler(event, context):
    
    global event_body
    event_body = event["queryStringParameters"]

    # connect to MySQL
    global mydb
    global mycursor
    mydb, mycursor = smart_city.db_connect()

    # check input to ensure it is valid & initialize search string
    search = validate_input()
    if search["statusCode"] != 200:
        return search
    else:
        search = search["search_string"]

    # get and format data from problems table
    search_results = search_problems(search)
    mycursor.close()
    mydb.close()
    return {
        "statusCode": 200,
        "body": json.dumps(search_results)
    }

def validate_input():
    search_string = "SELECT * FROM problems WHERE "
    search_list = []
    
    if "id" in event_body:
        mycursor.execute("SELECT id FROM problems")
        id_data = mycursor.fetchall()
        id_list = [str(i[0]) for i in id_data]
        id_number = str(event_body["id"])
        if id_number not in id_list:
            return {
                'statusCode': 400,
                'body': "The ID you requested is not in the problems table."
            }
        search_list.append(f'id = {event_body["id"]}')
        
    if "problem_type" in event_body:
        problem_type_list = ['Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire', 'Water Damage', 'Other']
        if event_body['problem_type'] not in problem_type_list:
            return {
                'statusCode': 400,
                'body': "problem_type must be set to 'Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire', 'Water Damage', or 'Other'"
            }
        search_list.append(f'problem_type = "{event_body["problem_type"]}"')
        
    if "problem_description" in event_body:
        if not isinstance(event_body["problem_description"], str):
            return {
                'statusCode': 400,
                'body': "'problem_description' must be of type string"
            }
        search_list.append(f'problem_description = "{event_body["problem_description"]}"')

    if "time_found" in event_body:
        event_body["time_found"] = event_body["time_found"].split(",")
        if len(event_body["time_found"]) != 2 or not all(isinstance(i, str) for i in event_body["time_found"]):
            return {
                'statusCode': 400,
                'body': "'time_found' takes a string of two 'times' seperated by a comma. 'time' is formatted as follows: YYYY-MM-DD HH:MM"
            }
        try:
            time_list = [datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M') for time in event_body["time_found"]]
        except ValueError:
            return {
                'statusCode': 400,
                'body': "Each time in 'time_found' must be formatted as follows: YYYY-MM-DD HH:MM"
            }
        if time_list[0] >= time_list[1]:
            return {
                'statusCode': 400,
                'body': "The second time must be later than the first. 'time' is formatted as follows: YYYY-MM-DD HH:MM"
            }
        search_list.append(f'time_found BETWEEN "{event_body["time_found"][0]}" AND "{event_body["time_found"][1]}"')

    if "current_status" in event_body:
        status_list = ['Open', 'In Progress', 'Complete']
        if event_body['current_status'] not in status_list:
            return {
                'statusCode': 400,
                'body': "Current Status must be set to 'Open', 'In Progress', or 'Complete'"
            }
        search_list.append(f'current_status = "{event_body["current_status"]}"')

    if "location" in event_body:
        if "distance" not in event_body:
            return {
                'statusCode': 400,
                'body': "'location must always be paired with 'distance'"
            }
        event_body["location"] = event_body['location'].split(",")
        try:
            event_body["location"] = [float(i) for i in event_body["location"]]
        except ValueError:
            return {
                'statusCode': 400,
                'body': "'location' takes a string of two points (both of type float) seperated by a comma."            
            }
        if len(event_body["location"]) != 2 or not -90 <= event_body["location"][0] <= 90 or not -180 <= event_body["location"][1] <= 180:
            return {
                'statusCode': 400,
                'body': "'location' takes a string of two points (both of type float) seperated by a comma. The first represents the latitude (which must be a number between -90 and 90) and the second represents the longitude (which must be a number between -180 and 180)"
            }
        try:
            event_body["distance"] = float(event_body["distance"])
        except ValueError:
            return {
                'statusCode': 400,
                'body': "'distance' must be a number."
            }
        if event_body["distance"] < 0:
            return {
                'statusCode': 400,
                'body': "'distance' must be at least 0"
            }
        search_list.append(f'ST_Distance_Sphere(point({event_body["location"][1]}, {event_body["location"][0]}), location) <= {event_body["distance"] * 1000}')

    if "distance" in event_body and "location" not in event_body:
        return {
            'statusCode': 400,
            'body': "'distance' must always be paired with 'location'"
        }

    if "image_path" in event_body:
        if not isinstance(event_body["image_path"], str):
            return {
                'statusCode': 400,
                'body': "'image_path' must be of type string"
            }
        search_list.append(f'image_path = "{event_body["image_path"]}"')

    for search in search_list:
        if search != search_list[-1]:
            search_string += search + " AND "
        else:
            search_string += search
    return {
        'statusCode': 200,
        'search_string': search_string
    }

def search_problems(search_string):
    mycursor.execute(search_string)
    data_list = mycursor.fetchall()
    data_json = []
    for data in data_list:
        data_dict = {
            'ID': data[0],
            'Problem Type': data[1],
            'Problem Description': data[2],
            'Time Found': str(data[3]),
            'Current Status': data[4]
        }
        mycursor.execute(f'SELECT ST_AsText(location) FROM problems WHERE id = {data[0]}')
        location = mycursor.fetchall()[0][0]
        location_list = location[6:-1].split()
        location_url = f'https://www.google.com/maps/search/?api=1&query={location_list[1]}%2C{location_list[0]}'
        data_dict['Location'] = location_url
        bucket = os.environ["BUCKET_NAME"]
        s3_client = boto3.client('s3')
        if data[6] == None:
            data_dict['Image Path'] = "No Image Provided"
        else:
            img_links = ""
            imgs = s3_client.list_objects_v2(Bucket=bucket, Prefix=f'{data[0]}/')
            imgs = imgs.get("Contents", {})
            for img in imgs:
                img_links += s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': img["Key"]}, ExpiresIn=3600) + "|"
            data_dict['Image Path'] = img_links

        data_json.append(data_dict)
    return data_json