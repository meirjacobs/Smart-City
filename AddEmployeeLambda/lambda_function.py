import mysql.connector
import json
import boto3

def lambda_handler(event, context):
    
    # check input to ensure it is valid
    if len(event) != 4:
        s = ""
        for item in event:
            s = s + '\n' + item + ": " + str(event[item])
        return {
            'statusCode': 400,
            'body': "Four items required. Received " + str(len(event)) + "\n\nInput = " + s
        }
    
    if "first_name" not in event or not isinstance(event["first_name"], str):
        return {
            'statusCode': 400,
            'body': "'first_name' is a required field and must be of type string"
        }
        
    if "last_name" not in event or not isinstance(event["last_name"], str):
        return {
            'statusCode': 400,
            'body': "'last_name' is a required field and must be of type string"
        }
    if "email" not in event or not isinstance(event["email"], str):
            return {
            'statusCode': 400,
            'body': "'email' is a required field and must be of type string" 
            #specify that it has to be an email address?
        }
   
    specialty_list = ['Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire', 'Water Damage', 'Other']
    if "specialty" not in event or event["specialty"] not in specialty_list:
        return {
            'statusCode': 400,
            'body': "'specialty' is a required field and must be 'Criminal Act', 'Environmental Hazard', 'Road Hazard', 'Vehicle Damage', 'Fire', 'Water Damage', or 'Other'"
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
    
    # insert data into database
    mycursor = mydb.cursor()    
    insert = "INSERT INTO employees (first_name, last_name, email, specialty) VALUES (%s, %s, %s, %s)"
    val = (event["first_name"], event["last_name"], event["email"], event["specialty"])
    mycursor.execute(insert, val)
    mydb.commit()

    return {
        'statusCode' : 200,
        'response': "Success"
    }