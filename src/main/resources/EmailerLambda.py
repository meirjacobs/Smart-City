import json
import logging
import smtplib
from email.message import EmailMessage

import boto3

def lambda_handler(event, context):
    
    # get email credentials
    sm_client = boto3.client("secretsmanager")
    secret = sm_client.get_secret_value(SecretId='Email-Credentials')
    credentials = json.loads(secret['SecretString'])

    # send email    
    msg = EmailMessage()
    msg['Subject'] = event["subject"]
    msg['From'] = credentials['username']
    msg['Bcc'] = ", ".join(event["email_list"])
    msg.set_content(event["message"])
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(credentials['username'], credentials['password'])
        server.send_message(msg)
        server.quit()
        return {
            'statusCode': 200,
            'body': "Email Sent!"
        }
    return {
        'statusCode': 400,
        'body': "Email was not able to be sent."
    }