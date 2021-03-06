# Hands-on environments generator
It is python tool what generates Hands-on environments. As a prerequisite to the execution of this tool, AWS Organizations environment is required.
## Description
This tool provides support functions for generating Hands-on environments. This tool provides following functions.
1. Generate member accounts in AWS Organizations.
1. Generate IAM user(s) in each member account.

This tool requires permissions what allows to create a member account on the AWS Organizations root account, and allow to  Assume Role to the created account's Administorator policy.
![Overview](Documents/Readme-overview.png)
## Requirement
This tool requires following modules and permissions.
- Executing environment for This tools
    - python
    - AWS SDK for Python(Boto3)
- AWS Environment
    - AWS Organization
        - Prepare a OU(Organization Unit) for workshop
## Install
### (1)git clone
```
https://github.com/Noppy/Handso-on_Generator.git
```
### (2)install and Configure aws cli
(a) Install boto3 and AWS CLI

Reference [boto3 Quickstart](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) Documents. (AWS CLI is used for configuring boto3.)

(b) Configure boto3

Configure AWS CLI so that it can run for the root account.
```
$ aws configure
AWS Access Key ID []: <root account - Access key>
AWS Secret Access Key []: <root account - Secret Key>
Default region name []: ap-northeast-1
Default output format [None]: 
```
### (3)Create OU for Hands-on
Create a OU(Organizational Units) for grouping created accounts. And take a meme OU-ID. OU-ID is used in create_account command.
![Create OU](Documents/Readme-OU.png)
## Usage
### (1) Create AWS Accounts
(a) make a json file

Generate a JSON file for create_accounts.py command.
```
./create_accounts.py -s dummy > AccountsConf.json
```
Modify AccountsConf.json. OuId, number.min, number.max email.MailAccount, email.domain, email.domai.
```
{
    "OuId": "ou-xxxx-xxxxxxxx",  <-Modify to created OU ID
    "number": {
        "max": 10, <- Max value of serial number
        "min": 0   <- Min value of serial number
    }, 
    "AccountNameHead": "Workshop",
    "email": {
        "ailias": "workshop", 
        "domain": "Mail.domain.com",　 
        "MailAccount": "mail-account"
    }
}
```
According to the setting of json above, 10 accounts with the following settings are created.

| AccountName | Mail Address | OU           | 
|:-----------:|:------------:|:------------:|
|Workshop00|mail-account00@Mail.domain.com|ou-xxxx-xxxxxxxx|
|Workshop01|mail-account01@Mail.domain.com|ou-xxxx-xxxxxxxx|
|:|:|:|
|Workshop10|mail-account10@Mail.domain.com|ou-xxxx-xxxxxxxx|

(b) create aws accounts

Create AWS accounts. The account information created by the command is output to the accounts.json file.
```
./create_accounts.py AccountsConf.json
```

### (2) Create IAM user
(a) make json file

Generate a JSON file for create_iamuser.py command.
```
./create_iamuser.py -s dummy > create_iamuser_config.json
```
Modify create_iamuser_config.json. 
```
{
    "Iam": {
        "UserName": "user", 
        "PolicyName": "HandsonIamUserPolicy", 
        "Max": 1, 
        "Min": 1
    }, 
    "AccountRole": "OrganizationAccountAccessRole", 
    "Region": "ap-northeast-1"
}
```
AccountRole and Regin are use for Assume Role. 
According to the setting of json above, a IAM user with the following settings are created.

| IAM User    | Policy       | 
|:-----------:|:------------:|
|user01|HandsonIamUserPolicy|

(b) create IAM users

Create IAM user(s) in each AWS account. the information of created IAM user is written to a JSON file whose name is "iamuserlogin.json".
```
./create_iamuser.py -c create_iamuser_config.json accounts.json
cat iamuserlogin.json
```

If you convert iamuserlogin.json to CSV file, execute following command. Note that [jq](https://stedolan.github.io/jq/) is required by this command.
```
cat iamuserlogin.json | jq -r '["AccountId","ConsoleUrl","UserName","Password"],(.[]|[.AccountId,.ConsoleUrl,.UserName,.Password]) | @csv' 
```
## Licence
Apache License 2.0
## Author
[N.Fujita/noppy](https://github.com/Noppy)