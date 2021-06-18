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
    status_list = ['Open', 'In Progress', 'Complete']
    if event['current_status'] not in status_list:
        return {
            'statusCode': 400,
            'body': "Current Status must be set to 'Open', 'In Progress', or 'Complete'"
        }

    # update data
    mycursor.execute("UPDATE Smart_City SET current_status = '" + event['current_status'] + "' WHERE id = " + str(event['id']))
    mydb.commit()

    return {
        'string': "Success",
        'statusCode' : 200
    }