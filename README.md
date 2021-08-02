# Smart City

Code repository for the Smart City team for Yeshiva University's Industrial Software Development Summer Project

## Steps for Deployment

Prerequisites: 
- AWS Account with appropriate permissions and sufficient credits
- Gmail account
- Docker desktop app installed

Steps:
1. Create an [S3 Bucket](https://s3.console.aws.amazon.com/s3/home) with the default settings. Copy the name of the bucket for the next step.\
Download [lambdas.zip](https://github.com/meirjacobs/Smart-City/blob/main/CloudFormation/lambdas.zip) and [mysql_layer.zip](https://github.com/meirjacobs/Smart-City/blob/main/CloudFormation/mysql_layer.zip) and add them to the bucket.

2. Create a [CloudFormation Stack](https://console.aws.amazon.com/cloudformation/home) with the [Smart City template](https://github.com/meirjacobs/Smart-City/blob/main/CloudFormation/smart_city_template.yml).\
Follow the instructions in the 'Parameters' section.

3. Wait about 10 minutes for the Stack to finish deploying.

4. Open a command line and run\
`docker run -p 8080:8080 -e API_URL=api_gateway_link -e SPRING_DATASOURCE_URL=jdbc:mysql://database_link:3306/Smart_City -e SPRING_DATASOURCE_PASSWORD="password" ecrystal/smart_city_repository:latest`, but replace `api_gateway_link` with the Invoke URL to your API Gateway, `database_link` with your database hostname, and `password` with your database password (see below for assistance).
    * To find the URL to your API Gateway, visit the [API Gateway console](https://console.aws.amazon.com/apigateway/main/apis) and click SmartCityAPIGateway. On the left of the screen, click Stages. Click deployedStage. The URL next to Invoke URL is what you need.
    * To find the hostname and password to your database, visit the [Secrets Manager Console](https://console.aws.amazon.com/secretsmanager/home), select MySQL-Credentials, scroll down a little and click "Retrieve secret value." You should see key-value pairs for "host" and "password."

5. Open your browser of choice, visit [localhost:8080](https://localhost:8080), and enjoy.