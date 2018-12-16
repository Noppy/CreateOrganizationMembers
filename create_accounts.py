#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  create_menber.py
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
import sys
import time

import boto3
from botocore.exceptions import ClientError

from modules import common_modules as common

# Json skeleton for skeleton_AccountsConfJsonFile
skeleton_AccountsConfJsonFile = {
    "AccountNameHead": "Workshop",
    "OuId": "ou-xxxx-xxxxxxxx",
    "email": {
        "local":  "MailAccount",
        "domain": "Mail.domain.com",
        "ailias": "workshop"
    },
    "number": {
        "min": 0,
        "max": 10
    }
}

# ---------------------------
# Initialize
# ---------------------------
def get_args():
    parser = argparse.ArgumentParser(
        description='create member accounts in AWS Organizations.')

    parser.add_argument('AccountsConfJsonFile',
        help='A Json File path for registered accounts information')

    parser.add_argument('-o','--output',
        action='store',
        default='accounts.json',
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
        help='Print a JSON skeleton for AccountsConfJsonFile(Specify a dummy parameter to AccountsConfJsonFile.)')

    parser.add_argument('-v', '--version',
        action='version',
        version='%(prog)s 0.1')

    return( parser.parse_args() )


# ---------------------------
# functions
# ---------------------------
def create_mail_address(args, conf):
    
    r = conf['number']
    m  = conf['email']
    ouid = conf.get('OuId')
    mlist = []

    # Check parameter
    if r['min'] < 0 or r['min'] > r['max']+1 \
       or len(m['local']) <= 0 or len(m['ailias']) <= 0 or m['domain'] <= 0:
        print("invalid a json file.")
        return

    # Create e-mail address list
    for i in range(r['min'],r['max']+1 ):
            mlist.append( {
                'mail': '{}+{}{:03d}@{}'.format(m['local'], m['ailias'], i, m['domain']),
                'name': '{}{:03d}'.format(conf['AccountNameHead'],i),
                'ouid': ouid
            })
    if args.debug:
        print(json.dumps(mlist, indent=2))
    return mlist


def checkmails(mails):
    print('AccountName     e-mail address                            ouid')
    print('--------------+---------------------------------------+----------------')
    for i in mails:
        print( '{:15s}{:40s}{}'.format(i["name"],i["mail"],i["ouid"]) )
    print('--------------+---------------------------------------+----------------')
    return common.answer("Are you OK?")


def CreateAccount(client, item):

    # Create a member of the organization
    try:
        createAccountRequest = client.create_account(
            Email = item['mail'],
            AccountName = item['name'],
            #RoleName = string,
            IamUserAccessToBilling = 'DENY'
        )
        createAccountRequestId = createAccountRequest["CreateAccountStatus"]["Id"]
    except ClientError as e:
        print(e)
        return False

    # Wait until complete creating a member account 
    account_status = 'IN_PROGRESS'
    while account_status == 'IN_PROGRESS':
        time.sleep(5)
        res = client.describe_create_account_status(
                CreateAccountRequestId=createAccountRequestId
        )
        account_status = res["CreateAccountStatus"]["State"]
    
    if account_status == 'SUCCEEDED':
        account_id = res['CreateAccountStatus']['AccountId']
    elif account_status == 'FAILED':
        print("Account creation failed: " + res['CreateAccountStatus']['FailureReason'])
        return False

    # Get Root that are defined in the Organization.
    root_id = client.list_roots().get('Roots')[0].get('Id')

    # Move a member accunt from root to specified OU.
    if str(item['ouid']) != 'None':
        try:
            res = client.describe_organizational_unit(
                    OrganizationalUnitId=item['ouid'])
            res = client.move_account(
                    AccountId=account_id,
                    SourceParentId=root_id,
                    DestinationParentId=item['ouid'])
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r} "
            message = template.format(type(ex).__name__, ex.args)
            # create_organizational_unit(organization_unit_id)
            print(message)

    # Get a created member account information
    res = client.describe_account(AccountId=account_id)['Account']
    
    # return 
    keys = ['Id', 'Arn', 'Email', 'Name']
    return dict( (k, res[k]) for k in keys if k in res )


def CreateAccounts(maillist):

    create_accounts = []

    # Get session
    client = boto3.client('organizations')

    for i in maillist:
        print('create account(name='+i['name']+'  email='+i['mail']+')')
        responce = CreateAccount(client, i)
        if responce != False:
            create_accounts.append(responce)

    return create_accounts

# ---------------------------
# The main function
# ---------------------------
def main():

    # Initialize
    args = get_args()

    if args.skeleton:
        print(json.dumps(skeleton_AccountsConfJsonFile,indent=4))
        return

    # Read Json configuration file and generate accounts list
    config = common.read_json_conf(args.AccountsConfJsonFile, debug=args.debug)
    if config is None: return False

    maillist = create_mail_address(args, config)
    if maillist is None: return False

    # Check
    ret = checkmails(maillist)
    if not ret: return False

    # Create Menber accounts
    result = CreateAccounts(maillist)

    # Output result
    with open(args.output, 'w') as f:
        f.write(json.dumps(result, indent=2))
        f.close()

if __name__ == "__main__":
    sys.exit(main())
