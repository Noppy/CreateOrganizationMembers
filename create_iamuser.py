#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  create_iamuser.py
#  ======
#  Copyright (C) 2018 n.fujita
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
from __future__ import print_function

import argparse
import json
import random
import string
import sys
import time

import boto3
from botocore.exceptions import ClientError

from modules import common_modules as common
from modules import assume_role

# Json skeleton for skeleton_IamUserConfJsonFile
skeleton_IamUserConfJsonFile = {
    "AccountRole": "OrganizationAccountAccessRole",
    "Region": "ap-northeast-1",
    "Iam": {
        "PolicyName": "HandsonIamUserPolicy",
        "UserName": "user",
        "Min": 1,
        "Max": 1
    }
}


# ---------------------------
# Initialize
# ---------------------------
def get_args():
    parser = argparse.ArgumentParser(
        description='add role, iam group and iam user.')

    parser.add_argument('AccountJsonFile',
        help='A Json File path that was created by createmember.py command')

    parser.add_argument('-c','--conf',
        action='store',
        default='create_iamuser_config.json',
        type=str,
        required=False,
        help='configuration json file.')

    parser.add_argument('-o','--output',
        action='store',
        default='iamuserlogin.json',
        type=str,
        required=False,
        help='Output json file name.')

    parser.add_argument('-d','--debug',
        action='store_true',
        default=False,
        required=False,
        help='Enable dry-run')

    parser.add_argument('-s','--skeleton',
        action='store_true',
        default=False,
        required=False,
        help='Print a JSON skeleton for create_iamuser_config.json(Specify a dummy parameter to AccountJsonFile.)')

    parser.add_argument('-v', '--version',
        action='version',
        version='%(prog)s 0.1')

    return( parser.parse_args() )


def check_config(config):

    keys = [ 'AccountRole', 'Region', 'Iam']
 
    flag = True
    # Check Level 1
    res = [ k for k in keys if k not in config ]
    if len(res) > 0:
        flag = False
        for i in res:
            print('Not found "'+i+'"')
    
    # Check Level 2 in "Iam"
    keys = [ 'PolicyName', 'UserName', 'Min', 'Max' ]
    target = config.get('Iam')
    res = [ k for k in keys if k not in target ]
    if len(res) > 0:
        flag = False
        for i in res:
            print('Not found "'+i+'" in "Iam"')
    
    return flag


# ---------------------------
# functions
# ---------------------------
def checkaccount(account):

    print('Account ID     Account Name')
    print('------------+--------------------')
    for i in account:
        print( '{:13s}{:20s}'.format(i['Id'], i['Name'] ))
    print('------------+--------------------')
    return common.answer("Are you OK?")


def add_iamuser(credentials, accountid, username, policyname, usernamehead, switchrole, region, args):

    iam = boto3.client('iam',
                          aws_access_key_id=credentials['AccessKeyId'],
                          aws_secret_access_key=credentials['SecretAccessKey'],
                          aws_session_token=credentials['SessionToken'],
                          region_name=region)

    # First message
    print("  Create or replace IAM user("+username+")")

    # Delete existing users and policies
    # Delete login profile
    try:
        res = iam.get_login_profile(UserName=username)
    except ClientError as e:
        if e.response['ResponseMetadata']['HTTPStatusCode'] != 404:
            print(e)
            return False
    else:
        print("    Delete existing login password for IAM user.")
        res = iam.delete_login_profile(UserName=username)
 
    # Delete inline users policy
    try:
        res = iam.delete_user_policy(
            UserName = username,
            PolicyName=policyname,
        )
    except ClientError as e:
        if e.response['ResponseMetadata']['HTTPStatusCode'] != 404:
            print(e)
            return False

    # Delete existing users
    UserArnList = [ i['Arn'] for i in iam.list_users()['Users'] if i['UserName'] == username ]
    if len(UserArnList) > 0:
        print("    Delete existing IAM user.")
        for i in UserArnList:
            iam.delete_user(UserName=username)

    # Create IAM User
    print("    Create a IAM User.")
    try:
        res = iam.create_user(
            Path='/',
            UserName=username
        )
    except ClientError as e:
        if e.response['ResponseMetadata']['HTTPStatusCode'] != 409:
            print(e)
            return False

    # Put inline policy to the IAM User
    print("    Put inline policy.")
    my_managed_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*"
            },
            {
                "Effect": "Deny",
                "Action": [
                    "iam:*"
                ],
                "Resource": [
                    "arn:aws:iam::*:role/"+switchrole,
                    "arn:aws:iam::*:user/"+usernamehead+"*"
                ]
            }
        ]
    }
    try:
        res = iam.put_user_policy(
            UserName = username,
            PolicyName=policyname,
            PolicyDocument=json.dumps(my_managed_policy)
        )
    except ClientError as e:
        if e.response['ResponseMetadata']['HTTPStatusCode'] != 409:
            print(e)
            return False

    # Create login profile User
    print("    Set a assword.")
    password = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(8)])
    if args.debug : print("    password= "+password)
    try:
        res = iam.create_login_profile(
            UserName = username,
            Password = password,
            PasswordResetRequired = False
        )
    except Exception as e:
            print(e)
            return False
        
    # set responce and return successful
    res = {
        "AccountId": accountid,
        "ConsoleUrl": "https://" + accountid + ".signin.aws.amazon.com/console",
        "UserName": username,
        "Password": password
    }
    return res


def add_resource(config, accounts, args):
 
    # execute each account
    LoginInformation = []
    for id in [ i['Id'] for i in accounts ]:
        print("Account ID: "+id)
        credentials = assume_role.assume_role(id, config)

        for i in range(config['Iam']['Min'],config['Iam']['Max']+1 ):
            usernamehead = config['Iam']['UserName']
            username = '{}{:02d}'.format(usernamehead,i)
            policyname = config['Iam']['PolicyName']
            region = config['Region']
            switchrole = config['AccountRole']
            res = add_iamuser(credentials, id, username, policyname, usernamehead, switchrole, region, args)
            if res != False:
                LoginInformation.append(res)

    return LoginInformation

# ---------------------------
# The main function
# ---------------------------
def main():

    # Initialize
    args = get_args()

    if args.skeleton:
        print(json.dumps(skeleton_IamUserConfJsonFile,indent=4))
        return

    # Read Json configuration file and generate accounts list
    config = common.read_json_conf(args.conf, debug=args.debug)
    if config is None: return False
    if not check_config(config): return False

    # Read accounts json file
    accounts = common.read_json_conf(args.AccountJsonFile, debug=args.debug)
    if accounts is None: return False

    # Check
    ret = checkaccount(accounts)
    if not ret: return False

    # Do
    LoginInformation = add_resource(config, accounts, args)

    # Output result
    with open(args.output, 'w') as f:
        f.write(json.dumps(LoginInformation, indent=2))
        f.close()

if __name__ == "__main__":
    sys.exit(main())
