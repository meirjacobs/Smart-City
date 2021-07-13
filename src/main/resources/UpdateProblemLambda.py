import json
import boto3
import mysql.connector

def lambda_handler(event, context):
    
    # connect to MySQL
    sm_client = boto3.client("secretsmanager")
    secret = sm_client.get_secret_value(SecretId='MySQL-Credentials')
    credentials = json.loads(secret['SecretString'])
    mydb = mysql.connector.connect(
        host=credentials['host'],
        user=credentials['username'],
        password=credentials['password'],
        database=credentials['dbname']
    )
    mycursor = mydb.cursor()
    
    # check input to ensure it is valid

    mycursor.execute("SELECT id FROM problems")
    id_data = mycursor.fetchall()
    id_list = [i[0] for i in id_data]
    id_number = event["id"]
    if id_number not in id_list:
        return {
            'statusCode': 400,
            'body': f"The ID {id_number} you requested is not in the problems table"
        }
        
    mycursor.execute("SELECT id FROM employees")
    employee_id_data = mycursor.fetchall()
    employee_id_list = [i[0] for i in employee_id_data]
    employee_id = event["employee_id"]
    if employee_id not in employee_id_list:
        return {
            'statusCode': 400,
            'body': f"The ID {id_number} you requested is not in the employees table"
        }
    
    status_list = ['Open', 'In Progress', 'Complete']
    if event['current_status'] not in status_list:
        return {
            'statusCode': 400,
            'body': "'current_status' must be set to 'Open', 'In Progress', or 'Complete'"
        }

    # prepare event variable for LogLambda & next validation
    mycursor.execute(f"SELECT * FROM problems WHERE id = {id_number}")
    data = mycursor.fetchall()[0]
    event["id_number"] = data[0]
    event['problem_type'] = data[1]
    event['problem_description'] = data[2]
    event['time_found'] = str(data[3])
    event['previous_status'] = data[4]
    event["image_path"] = data[6]
    mycursor.execute(f'SELECT ST_AsText(location) AS coordinates FROM problems WHERE id = {id_number}')
    location = mycursor.fetchall()[0][0]
    location = location[6:-1].split()
    location_list = [float(i) for i in location]
    event["location"] = location
    event["assigned_employee_id"] = employee_id
    
    if event['current_status'] == event['previous_status']:
      return {
            'statusCode': 400,
            'body': "'current_status' must not be the same as 'previous_status'"
        }

    # ensure selected employee has the same department as problem
    mycursor.execute(f"SELECT department FROM employees WHERE id = {employee_id}")
    employee_department = mycursor.fetchall()[0][0]
    if (event["problem_type"] != employee_department):
        return {
            'statusCode': 400,
            'body': f'The employee selected must be in the same department as the specific problem. (Employee department: {employee_department}, Specific problem: {event["problem_type"]})'
        }
    
    # ensure employee is free
    mycursor.execute(f"SELECT current_assignment_id FROM employees WHERE id = {employee_id}")
    assignment_id = mycursor.fetchall()[0][0]

    # update status and current_assignment_id in problems and employees table 
    lambda_client = boto3.client('lambda')
    id_to_delete = {
        "id": id_number
    }
    
    if event["previous_status"] == 'In Progress':
        # updating status to Complete
        if event["current_status"] == "Complete":
            mycursor.execute(f'UPDATE employees SET current_assignment_id = NULL where id = {employee_id}')
            lambda_client = boto3.client('lambda')
            lambda_client.invoke(
                FunctionName='arn:aws:lambda:us-east-1:287420233372:function:DeleteLambda',
                InvocationType='Event',
                Payload=json.dumps(id_to_delete)
            )
        # updating status to Open
        elif event["current_status"] == 'Open':
            mycursor.execute(f'UPDATE employees SET current_assignment_id = NULL where id = {employee_id}')
            mycursor.execute(f'UPDATE problems SET current_status = "{event["current_status"]}" WHERE id = {id_number}')

    if event["previous_status"] == 'Open':
        # updating status to Complete
        if event["current_status"] == 'Complete':
            lambda_client.invoke(
                FunctionName='arn:aws:lambda:us-east-1:287420233372:function:DeleteLambda',
                InvocationType='Event',
                Payload=json.dumps(id_to_delete)
            )
        # updating status to Open
        elif event["current_status"] == 'In Progress':
            if assignment_id != None:
                return {
                    'statusCode': 400,
                    'body': 'The employee is currently busy, please try another employee'
                }
            mycursor.execute(f'UPDATE employees SET current_assignment_id = {id_number} where id = {employee_id}')
            mycursor.execute(f'UPDATE problems SET current_status = "{event["current_status"]}" WHERE id = {id_number}')
    mydb.commit()
    
    # insert log to logs_history
    lambda_client.invoke(
        FunctionName='arn:aws:lambda:us-east-1:287420233372:function:LogLambda',
        InvocationType='Event',
        Payload=json.dumps(event)
    )

    return {
        'statusCode' : 200,
        'string': f'Success! ID {id_number} updated to {event["current_status"]}'
    }