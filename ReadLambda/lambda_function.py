import mysql.connector
import json
import datetime

def lambda_handler(event, context):
    
    # connect to MySQL
    mydb = mysql.connector.connect(
        host="smart-city-rds-0.ccmkepymppq8.us-east-1.rds.amazonaws.com",
        user="admin",
        password="Tester123",
        database="Smart_City_0"
    )
    
    # check input to ensure it is valid & initialize search string
    event = event["queryStringParameters"]
    mycursor = mydb.cursor()
    search_string = "SELECT * FROM Smart_City WHERE "
    search_list = []

    mycursor.execute("SELECT MAX(id) FROM Smart_City")
    last_id = mycursor.fetchall()[0][0]
    if "id" in event:
        if not isinstance(event["id"], int) or event["id"] > last_id or event["id"] < 1:
            return {
                'statusCode': 400,
                'body': "The ID you requested is not in the database. The ID must be of type int."
            }
        search_list.append("id = " + str(event["id"]))

    if "problem" in event:
        if not isinstance(event["problem"], str):
            return {
                'statusCode': 400,
                'body': "The 'problem' must be of type string"
            }
        search_list.append("problem = '" + event["problem"] + "'")

    if "time_found" in event:
        print(all(not isinstance(event["time_found"], str) for i in event["time_found"]))
        if len(event["time_found"]) != 2 or not all(isinstance(i, str) for i in event["time_found"]):
            return {
                'statusCode': 400,
                'body': "'time_found' takes a list of two 'times', both of type string. 'time' is formatted as follows: YYYY-MM-DD HH:MM:SS"
            }
        time_list = [datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S') for time in event["time_found"]]
        if time_list[0] >= time_list[1]:
            return {
                'statusCode': 400,
                'body': "The second time must be later than the first. 'time' is formatted as follows: YYYY-MM-DD HH:MM:SS"
            }
        search_list.append("time_found BETWEEN '" + str(event["time_found"][0]) + "' AND '" + str(event["time_found"][1]) + "'")

    if "current_status" in event:
        status_list = ['Open', 'In Progress', 'Complete']
        if event['current_status'] not in status_list:
            return {
                'statusCode': 400,
                'body': "Current Status must be set to 'Open', 'In Progress', or 'Complete'"
                }
        search_list.append("current_status = '" + event["current_status"] + "'")

    if "location" in event:
        if "distance" not in event:
            return {
                'statusCode': 400,
                'body': "'location must always be paired with 'distance'"
                }
        if len(event["location"]) != 2 or not all(isinstance(i, float) for i in event["location"]) or not -90 <= event["location"][0] <= 90 or not -180 <= event["location"][1] <= 180:
            return {
                'statusCode': 400,
                'body': "'location' takes a list of two points, both of type float. The first represents the latitude (which must be a number between -90 and 90) and the second represents the longitude (which must be a number between -180 and 180)"
                }
        if not isinstance(event["distance"], (int, float)) or event["distance"] < 0:
            return {
                'statusCode': 400,
                'body': "'distance' must be a number that is at least 0"
                }
        search_list.append("ST_Distance_Sphere(point(" + str(event["location"][1]) + ", " + str(event["location"][0]) + "), location) <= " + str(event["distance"]))

    if "distance" in event and "location" not in event:
        return {
            'statusCode': 400,
            'body': "'distance' must always be paired with 'location'"
        }

    if "image_path" in event: # dont think this would ever be searched...
        if not isinstance(event["image_path"], str):
            return {
                'statusCode': 400,
                'body': "'image_path' must be of type string"
                }
        search_list.append("image_path = '" + event["image_path"] + "'")
    
    for search in search_list:
        if search != search_list[-1]:
            search_string += search + " AND "
        else:
            search_string += search

    # get and format data from database
    mycursor.execute(search_string)
    data_list = mycursor.fetchall()
    data_json = []
    for data in data_list:
        data_dict = {
            'id': data[0],
            'problem': data[1],
            'time_found': str(data[2]),
            'current_status': data[3]
        }
        mycursor.execute("SELECT ST_AsText(location) AS coordinates FROM Smart_City WHERE id = " + str(data[0]))
        location = mycursor.fetchall()[0][0]
        location_list = location[6:-1].split()
        location_url = "https://www.google.com/maps/search/?api=1&query=" + location_list[1] + "%2C" + location_list[0]
        data_dict['location'] = location_url
        data_dict['image_path'] = str(data[5])
        data_json.append(data_dict)

    return {
        "status code": 200,
        "body": json.dumps(data_json)
    }