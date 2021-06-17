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
    
    # check input to ensure it is valid
    mycursor = mydb.cursor()
    mycursor.execute("SELECT MAX(id) FROM Smart_City")
    last_id = mycursor.fetchall()[0][0]
    id_number = event["id"]
    if id_number > last_id or id_number < 1:
        return {
            'statusCode': 400,
            'body': "The ID you requested is not in the database"
        }

    # get and format data from database
    mycursor.execute("SELECT * FROM Smart_City WHERE id = " + str(id_number))
    data_list = mycursor.fetchall()[0]
    data = {
        'id': data_list[0],
        'image_path': data_list[1],
        'problem': data_list[2]
    }
    mycursor.execute("SELECT ST_AsText(location) AS coordinates FROM Smart_City WHERE id = " + str(id_number))
    location = mycursor.fetchall()[0][0]
    location_list = location[6:-1].split()
    location_url = "https://www.google.com/maps/search/?api=1&query=" + location_list[1] + "%2C" + location_list[0]
    data['location'] = location_url
    data['time_found'] = str(data_list[4])

    return data