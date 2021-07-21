import datetime
import json

import boto3

import mysql.connector

event_body = None

def lambda_handler(event, context):
    
    global event_body
    event_body = event["queryStringParameters"]

    # connect to MySQL
    mysql_connect()

    # check input to ensure it is valid & initialize search string
    search = validate_input()
    if search["statusCode"] != 200:
        return search
    else:
        search = search["search_string"]

    # get and format data from problems table
    search_results = search_problems(search)
    return {
        "statusCode": 200,
        "body": "Search Results: \n" + json.dumps(search_results)
    }

def mysql_connect():
    sm_client = boto3.client("secretsmanager")
    secret = sm_client.get_secret_value(SecretId='MySQL-Credentials')
    credentials = json.loads(secret['SecretString'])
    global mydb
    mydb = mysql.connector.connect(
        host=credentials['host'],
        user=credentials['username'],
        password=credentials['password'],
        database=credentials['dbname']
    )
    global mycursor
    mycursor = mydb.cursor()
    

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
                'body': f"The ID {id_number} you requested is not in the problems table."
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
        if len(event_body["time_found"]) != 2 or not all(isinstance(i, str) for i in event_body["time_found"]):
            return {
                'statusCode': 400,
                'body': "'time_found' takes a list of two 'times', both of type string. 'time' is formatted as follows: YYYY-MM-DD HH:MM:SS"
            }
        try:
            time_list = [datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S') for time in event_body["time_found"]]
        except ValueError:
            return {
                'statusCode': 400,
                'body': "Each time in 'time_found' must be formatted as follows: YYYY-MM-DD HH:MM:SS"
            }
        if time_list[0] >= time_list[1]:
            return {
                'statusCode': 400,
                'body': "The second time must be later than the first. 'time' is formatted as follows: YYYY-MM-DD HH:MM:SS"
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
        if len(event_body["location"]) != 2 or not all(isinstance(i, float) for i in event_body["location"]) or not -90 <= event_body["location"][0] <= 90 or not -180 <= event_body["location"][1] <= 180:
            return {
                'statusCode': 400,
                'body': "'location' takes a list of two points, both of type float. The first represents the latitude (which must be a number between -90 and 90) and the second represents the longitude (which must be a number between -180 and 180)"
            }
        if not isinstance(event_body["distance"], (int, float)) or event_body["distance"] < 0:
            return {
                'statusCode': 400,
                'body': "'distance' must be a number that is at least 0"
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
            'id': data[0],
            'problem_type': data[1],
            'problem_description': data[2],
            'time_found': str(data[3]),
            'current_status': data[4]
        }
        mycursor.execute(f'SELECT ST_AsText(location) AS coordinates FROM problems WHERE id = {data[0]}')
        location = mycursor.fetchall()[0][0]
        location_list = location[6:-1].split()
        location_url = f'https://www.google.com/maps/search/?api=1&query={location_list[1]}%2C{location_list[0]}'
        data_dict['location'] = location_url
        data_dict['image_path'] = str(data[6])
        data_json.append(data_dict)
    return data_json