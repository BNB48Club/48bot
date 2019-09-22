#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'BNB48'
__reference__='https://gist.github.com/mrluanma/6000424'
import configparser
import sys
import time
import random
from weibo import APIClient

def get_access_token(app_key, app_secret, callback_url):
    client = APIClient(app_key=app_key, app_secret=app_secret, redirect_uri=callback_url)
    # 获取授权页面网址
    auth_url = client.get_authorize_url()
    print(auth_url)

    # 在浏览器中访问这个URL，会跳转到回调地址，回调地址后面跟着code，输入code
    code = input("Input code:")
    r = client.request_access_token(code)
    access_token = r.access_token
    # token过期的UNIX时间
    expires_in = r.expires_in
    print('access_token:', access_token)
    print('expires_in:', expires_in)

    return access_token, expires_in

UID=""
def init_weibo(account):
    callback_url = 'https://api.weibo.com/oauth2/default.html'
    weiboconfig = configparser.ConfigParser()
    weiboconfig.read("conf/weibo.conf")
    app_key = weiboconfig.get(account,"app_key")
    app_secret = weiboconfig.get(account,"app_secret")
    #access_token, expires_in = get_access_token(app_key, app_secret, callback_url)
    access_token = weiboconfig.get(account,"access_token")
    expires_in = weiboconfig.get(account,"expires_in")
    global UID
    UID = weiboconfig.get(account,"uid")


    client = APIClient(app_key=app_key, app_secret=app_secret, redirect_uri=callback_url)
    client.set_access_token(access_token, expires_in)
    return client

def send_pic(client,picpath,title):
    # send a weibo with img
    f = open(picpath, 'rb')
    mes = title.decode('utf-8')
    r = client.statuses.share.post(status=mes+" https://www.binance.co/register.html?ref=10150829", pic=f)
    f.close()  # APIClient不会自动关闭文件，需要手动关闭
    return "https://weibo.com/{}/{}".format(UID,mid2str(r['mid']))

def send_mes(client,message):
    mes = message.decode('utf-8')
    r = client.statuses.share.post(status=mes+" https://www.binance.co/register.html?ref=10150829")
    return "https://weibo.com/{}/{}".format(UID,mid2str(r['mid']))
    '''
    utext = unicode(message,"UTF-8")
    return mid2str(client.post.statuses__share(status=message)['mid'])
    '''



ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def rsplit(s, count):
    f = lambda x: x > 0 and x or 0
    return [s[f(i - count):i] for i in range(len(s), 0, -count)]


def mid2str(mid):
    result = ''
    for i in rsplit(mid, 7):
        str62 = base62_encode(int(i))
        result = str62.zfill(4) + result
    return result.lstrip('0')


def str2mid(input):
    result = ''
    for i in rsplit(input, 4):
        str10 = str(base62_decode(i)).zfill(7)
        result = str10 + result
    return result.lstrip('0')


def base62_encode(num, alphabet=ALPHABET):
    """Encode a number in Base X
    `num`: The number to encode
    `alphabet`: The alphabet to use for encoding
    """
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def base62_decode(string, alphabet=ALPHABET):
    """Decode a Base X encoded string into the number
    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for encoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1
    return num


def test():
    assert mid2str('231101124784859058') == 'Bh0tgako3U'
    assert str2mid('Bh0tgako3U') == '231101124784859058'

    assert mid2str('3491273850170657') == 'yCirT0Iox'
    assert str2mid('yCirT0Iox') == '3491273850170657'



if __name__ == '__main__':
    time.sleep(600*random.random())
    client = init_weibo('BNB48Club')
    #print(send_pic(client,"temp.png","testtitle"))
    print((send_mes(client,"币安宝什么时候出不限量的活期版本？没有我明天再问一下")))
