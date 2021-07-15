# Smart City

Code repository for the Smart City team for Yeshiva University's Industrial Software Development Summer Project

## Steps for Deployment

- Prerequisite: AWS Account with appropriate permissions and sufficient credits.

1. Create an [AWS CloudFormation Stack](https://docs.aws.amazon.com/cloudformation/index.html) with the [Smart City template](https://github.com/meirjacobs/Smart-City/blob/main/src/main/resources/smartcitytemplate.yml).
2. Navigate to [Secrets Manager](https://console.aws.amazon.com/secretsmanager/home?/listSecrets) and select 'Email-Credentials'.  
  Scroll down to 'Secret value' and select 'Retrieve secret value'. Click 'edit' and update the field to the right of 'username' with the email address you wish to send emails from, and in the field to the right of the 'password' box with the password to the email.
3. 