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

def get_memberid(browser, url):
    assert(broswer)
    assert(url)

    broswer.get(url)
    try:
        xpath_handle = browser.find_element_by_xpath("//head/meta[@name='mobile-agent']")
    except NoSuchElementException:
        source = browser.page_source
        if source.find('anti_Spider-html-checkcode') > 0 or browser.current_url.find('anti_Spider-html-checklogin') > 0:
            return (ERR_CODE['BLOCK'], '')
        else:
            return (get_errcode(200, broswer.current_url), '')

    content = xpath_handle.get_attribute('content')
    memberid = re.findall(r'(?<=winport/).*?(?=\.html)', content, re.S) if content else ''
    memberid = '' if not memberid else memberid[0]

    return (ERR_CODE['OK'], memberid)


if __name__ == '__main__':
    dir_path, file_name = os.path.split(os.path.realpath(__file__))
    log_file = dir_path + '/logs/' + file_name.replace('.py', '.log')
    logInit(logging.INFO, log_file, 0, True)

    ab = AntiBan('Phantomjs', True, False)
    broswer = ab.get_broswer()
    broswer.implicitly_wait(5)
    broswer.set_page_load_timeout(5)

    mongo_db = pymongo.MongoClient('192.168.60.65', 10010).ali_company

    while True:
        mongo_handle = mongo_db.usernames.find({'status': {'$in': [0, 1]}, 'memberid_fetched': False}, {'username': 1})
        usernames = [item['username'] for item in mongo_handle]
        mongo_handle = mongo_db.usernames.find({'status': 0, 'memberid_fetched': {'$exists': False}}, {'username': 1})
        usernames1 = [item['username'] for item in mongo_handle]
        usernames.extend(usernames1)

        if not usernames:
            logging.info('not find need fetch usernames! sleep 10')
            sleep(10)
            continue

        logging.info('need fetch usernames %s', len(usernames))

        for username in usernames:
            if not username:
                continue
            fetch_url = 'http://%s.1688.com/page/merchants.htm?tbpm=3' % (username)
            logging.info('create news request %s', fetch_url)

            try:
                status, memberid = get_memberid(broswer, fetch_url)
            except Exception as e:
                logging.error('get body error! (%s)', str(e))
                broswer = ab.get_broswer()
                continue

            if status == ERR_CODE['OK']:
                try:
                    mongo_db.memberids.insert_one({'username': username, 'memberid': memberid, 'insert_date': datetime.datetime.now()})
                except pymongo.errors.DuplicateKeyError:
                    pass
                except Exception, e:
                    logging.error('[insert to mongo error!] %s %s %d %s', username, memberid, status, str(e))
                    ab.browser_quit()
                    continue
                mongo_db.usernames.update({'username': username}, {'$set': {'memberid_fetched': True}}, False, True)
                logging.info('[SUCCEED] %s %s', username, memberid)
                broswer = ab.get_broswer()
            elif status == ERR_CODE['BLOCK']:
                logging.info('[BLOCK] %s %s', username, memberid)
                sleep(SLEEP_TIME)
                broswer = ab.get_broswer()
            elif status == ERR_CODE['CLOSE']:
                mongo_db.usernames.update({'username': username}, {'$set': {'status': ERR_CODE['CLOSE']}}, False, True)
                logging.info('[CLOSE] %s %s %d', username, memberid, status)
            else:
                logging.error('[SOMETHING WRONG] %s %s %d', username, memberid, status)
