import json
import os
import smtplib
from email.message import EmailMessage

import boto3

def lambda_handler(event, context):
    
    # get email credentials
    sm_client = boto3.client("secretsmanager")
    secret = sm_client.get_secret_value(SecretId='Email-Credentials')
    credentials = json.loads(secret['SecretString'])
    
    # set up email
    msg = EmailMessage()
    msg['Subject'] = event["subject"]
    msg['From'] = credentials['username']
    msg['Bcc'] = ", ".join(event["email_list"])
    msg.set_content(event["message"])
    
    # attach pictures
    s3_client = boto3.client('s3')
    bucket = os.environ["BUCKET_NAME"]
    imgs = s3_client.list_objects_v2(Bucket=bucket, Prefix=f'{event["id_number"]}/')
    imgs = imgs.get("Contents", {})
    for img in imgs:
        img_key = img["Key"]
        img = s3_client.get_object(Bucket="smartcitytestbucket", Key=img_key)['Body']
        image_data = img.read()
        msg.add_attachment(image_data, maintype='image', subtype='jpg', filename=img_key)
    
    # send email
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