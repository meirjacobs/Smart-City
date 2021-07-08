import json
import boto3
import mysql.connector

def lambda_handler(event, context):
    
    # check input to ensure it is valid
    if "id" not in event or not isinstance(event["id"], int):
        return {
            'statusCode': 400,
            'body': "'id' is a required field and must be of type int"
        }
        
    # connect to MySQL
    sm_client = boto3.client("secretsmanager")
    secret = sm_client.get_secret_value(SecretId='test/MySQL')
    credentials = json.loads(secret['SecretString'])
    mydb = mysql.connector.connect(
        host=credentials['host'],
        user=credentials['user'],
        password=credentials['password'],
        database=credentials['dbname']
    )
    mycursor = mydb.cursor()
    
    # delete problem from problems table
    id_number = event["id"]
    mycursor.execute(f"DELETE from problems WHERE id = {id_number}")
    mydb.commit()
    
    effected_rows = mycursor.rowcount
    if effected_rows == 0:
        return {
            'statusCode': 400,
            'body': f"ID {id_number} does not exist in table or has already been deleted"
        }
    else:
        return {
            'statusCode': 200,
            'body': f"ID {id} deleted succesfully"
        }