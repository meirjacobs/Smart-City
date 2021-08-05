import json

import boto3

import mysql.connector

def db_connect():
    sm_client = boto3.client("secretsmanager")
    secret = sm_client.get_secret_value(SecretId='MySQL-Credentials')
    credentials = json.loads(secret['SecretString'])
    mydb = mysql.connector.connect(
        host=credentials['host'],
        user=credentials['username'],
        password=credentials['password'],
        database=credentials['dbname'],
        autocommit=True
    )
    mycursor = mydb.cursor()
    return mydb, mycursor