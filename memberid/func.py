#encoding=gb18030
#-*- coding:gb18030-*-
import os
import sys
import re

STATUS = {'STANDBY':0, 'OK':1, 'RETRY':2, 'FAILED':3}
TYPES = {'INVALID':-1, 'M1688':0, 'TMALL':1, 'TAOBAO':2}
ORACLE_SEARCH_LISTPAGE_STATUS = {'STANDBY':0, 'OK':1, 'FAILED':2}
ERR_CODE = {'OK':1, 'CLOSE':2, 'BLOCK':3, 'TEMP':4}
SLEEP_TIME = 10

def get_errcode(status, jump_url):
    err_str = {
        '/wrongpage.html': ERR_CODE['CLOSE'],
        '/noshop.html': ERR_CODE['CLOSE'],
        '/close.html': ERR_CODE['CLOSE'],
        '/weidaoda.html': ERR_CODE['CLOSE'],
        '//wo.1688.com': ERR_CODE['CLOSE'],
        '/wgxj.html': ERR_CODE['CLOSE'],
        '': ERR_CODE['CLOSE'],
        'login': ERR_CODE['BLOCK'],
        'anti': ERR_CODE['BLOCK'],
        '/deny.html': ERR_CODE['BLOCK'],
        'checkcodev': ERR_CODE['BLOCK'],
        'kylin': ERR_CODE['BLOCK']
    }

    if status == 404:
        return ERR_CODE['CLOSE']

    for k in err_str:
        if jump_url.find(k) >= 0:
            return err_str[k]

    return ERR_CODE['TEMP']
