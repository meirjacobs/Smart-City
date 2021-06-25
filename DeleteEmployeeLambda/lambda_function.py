import mysql.connector
import json
import boto3

def lambda_handler(event, context):
    
    # check input to ensure it is valid
    if len(event) != 1:
        s = ""
        for item in event:
            s = s + '\n' + item + ": " + str(event[item])
        return {
            'statusCode': 400,
            'body': "One item required. Received " + str(len(event)) + "\n\nInput = " + s
        }
    
    if "id" not in event or not isinstance(event["id"], int):
        return {
            'statusCode': 400,
            'body': "'id' is a required field and must be of type int"
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

    # check input to ensure it is valid    
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id FROM employees")
    id_list = mycursor.fetchall()[0]
    id_number = event["id"]
    if id_number not in id_list:
        return {
            'statusCode': 400,
            'body': "The ID you requested is not in the database"
        }     
        
    mycursor.execute(f'SELECT * FROM employees WHERE id = {event["id"]}')
    info = mycursor.fetchall()[0]

    # delete data from database
    delete = f'DELETE FROM employees WHERE id = {id_number}'
    mycursor.execute(delete)
    mydb.commit()

    return {
        'statusCode' : 200,
        'response': f'Success, deleted: {info} from the table'
    }
