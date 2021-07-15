# Smart City

Code repository for the Smart City team for Yeshiva University's Industrial Software Development Summer Project

## Steps for Deployment

- Prerequisite: AWS Account with appropriate permissions and sufficient credits.

1. Navigate to [S3](s3.console.aws.amazon.com/s3/home?) and select 'Create bucket'.
  Name the bucket ---, scroll down to the bottom of the page and click 'Create bucket'. Repeat this process with a bucket name of ---.
  Download [all-lambdas.zip](https://github.com/meirjacobs/Smart-City/blob/main/src/main/resources/all-lambdas.zip) and put it the --- bucket.
  Download [mysql_layer_zip.zip](https://github.com/meirjacobs/Smart-City/tree/main/src/main/dependencies/mysql_layer/mysql_layer_zip.zip) and put it in the --- bucket.

2. Create an [AWS CloudFormation Stack](https://docs.aws.amazon.com/cloudformation/index.html) with the [Smart City template](https://github.com/meirjacobs/Smart-City/blob/main/src/main/resources/smartcitytemplate.yml).

3. Navigate to [Secrets Manager](https://console.aws.amazon.com/secretsmanager/home?/listSecrets) and select 'Email-Credentials'.  
  Scroll down to 'Secret value' and select 'Retrieve secret value'.
  Click 'edit' and update the field to the right of 'username' with the email address you wish to send emails from, and in the field to the right of the 'password' box with the password to the email.

4. More steps to come soon iyH.