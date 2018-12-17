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
(a) Install boto3

Reference [boto3 Quickstart](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) Documents.

(b) Configure boto3
Config AWS CLI so that it can run for the root account.
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
(a) make json file
(b) create aws accounts

### (1) Create IAM user
(a) make json file
(b) create IAM users


## Licence
Apache License 2.0
## Author
[N.Fujita/noppy](https://github.com/Noppy)