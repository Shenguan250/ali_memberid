#-*- coding:utf-8-*-
import os
import sys
import logging
import re
import json
import codecs
import urllib
import requests
import time
import pymongo
from pymongo import MongoClient
import random
import traceback
sys.path.append('/tools/python_common')
from func import *
from common_func import *
from anti_ban_selenium import AntiBan
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
import datetime
from ipdb import set_trace

if __name__ == '__main__':
    dir_path, file_name = os.path.split(os.path.realpath(__file__))
    log_file = dir_path + '/logs/' + file_name.replace('.py', '.log')
    logInit(logging.INFO, log_file, 0, True)

    mongo_db = pymongo.MongoClient('192.168.60.65', 10010).ali_company


    mongo_handle = mongo_db.usernames.find({'status': {'$in': [0, 1]}, 'memberid_fetched': False}, {'username': 1})
    usernames = [item['username'] for item in mongo_handle]
    mongo_handle = mongo_db.usernames.find({'status': 0, 'memberid_fetched': {'$exists': False}}, {'username': 1})
    usernames1 = [item['username'] for item in mongo_handle]
    usernames.extend(usernames1)
    print len(usernames)

    for index, username in enumerate(usernames):
        mongo_handle = mongo_db.memberids.find_one({'username': username}, {'memberid': 1})
        if mongo_handle and mongo_handle.get('memberid', ''):
            mongo_db.usernames.update({'username': username}, {'$set': {'memberid_fetched': True}}, False, True)
            print index, username
