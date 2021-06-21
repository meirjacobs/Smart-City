import mysql.connector
import json

def lambda_handler(event, context):
    
    # connect to MySQL
    mydb = mysql.connector.connect(
        host="smart-city-rds-0.ccmkepymppq8.us-east-1.rds.amazonaws.com",
        user="admin",
        password="Tester123",
        database="Smart_City_0"
    )
    
    # check input to ensure it is valid (TODO)
    mycursor = mydb.cursor()

    # initialize search string
    event = event["queryStringParameters"]
    search_string = "SELECT * FROM Smart_City WHERE "
    search_list = []
    if "id" in event:
        search_list.append("id = " + str(event["id"]))
    if "problem" in event:
        search_list.append("problem = '" + event["problem"] + "'")
    if "time_found" in event:
        search_list.append("time_found BETWEEN '" + str(event["time_found"][0]) + "' AND '" + str(event["time_found"][1]) + "'")
    if "current_status" in event:
        search_list.append("current_status = '" + event["current_status"] + "'")
    if "location" in event:
        search_list.append("ST_Distance_Sphere(point(" + str(event["location"][1]) + ", " + str(event["location"][0]) + "), location) <= " + str(event["distance"]))
    if "image_path" in event: # dont think this would ever be searched...
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