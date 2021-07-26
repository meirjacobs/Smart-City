# Smart City

Code repository for the Smart City team for Yeshiva University's Industrial Software Development Summer Project

## Steps for Deployment

Prerequisites: 
- AWS Account with appropriate permissions and sufficient credits.
- Gmail account
- Maybe more?

Steps:
1. Create an [S3 Bucket](https://s3.console.aws.amazon.com/s3/home) with the default settings. Copy the name of the bucket for the next step.\
Download [lambdas.zip](https://github.com/meirjacobs/Smart-City/blob/main/CloudFormation/lambdas.zip) and [mysql_layer.zip](https://github.com/meirjacobs/Smart-City/blob/main/CloudFormation/mysql_layer.zip) and add them to the bucket.

2. Create an [CloudFormation Stack](https://console.aws.amazon.com/cloudformation/home) with the [Smart City template](https://github.com/meirjacobs/Smart-City/blob/main/CloudFormation/smart_city_template.yml).\
Follow the instructions in the 'Parameters' section.

3. Wait about 10 minutes for the Stack to finish deploying.

4. More steps to come soon iyH.