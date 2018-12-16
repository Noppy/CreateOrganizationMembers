#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  common_modules.py
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

import json
import sys


#---------------------------
# "yes or no question" logiA functionsc
#---------------------------
def prompt_for_input(prompt = "", val = None):
    if val is not None:
        return val
    print( prompt + " ")
    return sys.stdin.readline().strip()


def yes_or_no(s):
    s = s.lower()
    if s in ("y", "yes", "1", "true", "t"):
        return True
    elif s in ("n", "no", "0", "false", "f"):
        return False
    raise ValueError("A yes or no response is required")


def answer(message):
    ret = False
    while 1:
        print( "\n" + message )
        res = prompt_for_input("Yes or No?")
        try:
            if yes_or_no(res):
                ret = True
            else:
                ret = False
            break
        except ValueError as e:
            print("ERROR: ", e)

    return ret


#---------------------------
# read a json configuration file
#---------------------------
def read_json_conf(JsonFileName, debug = False):

    try:
        with open(JsonFileName, mode='r') as f:
            data = json.load(f)
            f.close()
            if debug:
                print(json.dumps(data, indent=2))
            return data
    except IOError as e:
        print(e)
    except ValueError:
        type, value, traceback = sys.exc_info()
        print (value)
    except ValueError:
        type, value, traceback = sys.exc_info()
        print (type)
        print (value)
#    except json.JSONDecodeError as e:
#        print('JSONDecodeError: ', e)

    return
