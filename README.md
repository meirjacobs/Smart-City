# Smart City

Code repository for the Smart City team for Yeshiva University's Industrial Software Development Summer Project. Created in Summer 2021 by [Nir Solooki](https://www.linkedin.com/in/nir-solooki-018702204/), [Ephraim Crystal](https://www.linkedin.com/in/ephraim-crystal-429a8020a/), [Max Friedman](https://www.linkedin.com/in/max-friedman-98a77a205/), and [Meir Jacobs](https://www.linkedin.com/in/jordan-meir-jacobs/), under the guidance of [David Rosenstark](https://www.linkedin.com/in/david-rosenstark-3b070b8/).

## About
We created a Smart City Reporting System, a system in which users can report and search for issues in their respective cities, and employees can log in to a portal where they can take on issues and update data. We made the backend with AWS (in particular, CloudFormation, API Gateway, Lambda, RDS, S3, Secrets Manager, and CloudWatch). We used Spring Boot to create a web application built on our AWS system. Finally, we used Docker to create an executable file that anyone can easily run on their computer.\
For more details, please take a look at our [YouTube video](https://youtu.be/Sxdd5BMu2iI). Alternatively, you can view our [slideshow](https://github.com/meirjacobs/Smart-City/blob/main/Smart%20City%20Reporting%20System.pptx).

## Steps for Deployment

Prerequisites: 
- AWS Account with appropriate permissions and sufficient credits
- Gmail account with [less secure app access](https://myaccount.google.com/lesssecureapps) enabled
- Docker desktop app installed

Steps:
1. Create an [S3 Bucket](https://s3.console.aws.amazon.com/s3/home) with the default settings. Copy the name of the bucket for the next step.\
Download [lambdas.zip](https://github.com/meirjacobs/Smart-City/blob/main/CloudFormation/lambdas.zip) and [mysql_layer.zip](https://github.com/meirjacobs/Smart-City/blob/main/CloudFormation/mysql_layer.zip) and add them to the bucket.

2. Create a [CloudFormation Stack](https://console.aws.amazon.com/cloudformation/home) with the [Smart City template](https://github.com/meirjacobs/Smart-City/blob/main/CloudFormation/smart_city_template.yml).\
Follow the instructions in the 'Parameters' section.

3. Wait about 10 minutes for the Stack to finish deploying.

4. Open a command line and run\
`docker run -p 8080:8080 -e API_URL=api_gateway_link -e SPRING_DATASOURCE_URL=jdbc:mysql://database_link:3306/Smart_City -e SPRING_DATASOURCE_PASSWORD="password" ecrystal/smart_city_repository:latest`, but replace `api_gateway_link` with the Invoke URL to your API Gateway, `database_link` with your database hostname, and `password` with your database password (see below for assistance).
    * To find the URL to your API Gateway, visit the [API Gateway Console](https://console.aws.amazon.com/apigateway/main/apis) and click SmartCityAPIGateway. On the left of the screen, click Stages. Click deployedStage. The URL next to Invoke URL is what you need.
    * To find the hostname and password to your database, visit the [Secrets Manager Console](https://console.aws.amazon.com/secretsmanager/home), select MySQL-Credentials, scroll down a little and click "Retrieve secret value." You should see key-value pairs for "host" and "password."

5. Open your browser of choice, visit [localhost:8080](https://localhost:8080), and enjoy.

6. (Optional) If you would like to run the tests that we have created, please follow these steps:
    * Download the [test files](https://downgit.github.io/#/home?url=https://github.com/meirjacobs/Smart-City/tree/main/src/test) then extract them.
    * Make sure you have all the correct libraries installed by checking the requirements.txt. To install them, navigate to the test/dependencies folder and run: `pip install -r requirements.txt`.
    * Create a .env file in the test/resources folder to hold the environment variables for the tests. As mentioned earlier, these values may be retrieved from the [API Gateway Console](https://console.aws.amazon.com/apigateway/main/apis) and the [Secrets Manager Console](https://console.aws.amazon.com/secretsmanager/home).\
    Please use the template below. Don't use quotes:
    ```
    URL=
    DB_HOST=
    DB_USERNAME=
    DB_PASSWORD=
    DB_NAME=
    ```
    * Open a terminal to the test/resources folder and run: `py -m pytest` or `python -m pytest` depending on your device.