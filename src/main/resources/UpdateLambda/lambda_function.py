import mysql.connector
import json
import boto3

def lambda_handler(event, context):
    
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
    
    # check input to ensure it is valid
    mycursor = mydb.cursor()
    mycursor.execute("SELECT MAX(id) FROM Smart_City")
    last_id = mycursor.fetchall()[0][0]
    id_number = event["id"]
    if not isinstance(id_number, int) or 1 > id_number <= last_id:
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
    update = f'UPDATE Smart_City SET current_status = "{event["current_status"]}" WHERE id = {id_number}'
    mycursor.execute(update)
    mydb.commit()
    
    success = f'Success! ID {id_number} updated to {event["current_status"]}'
    return {
        'statusCode' : 200,
        'string': success
    }