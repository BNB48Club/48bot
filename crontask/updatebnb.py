#!/usr/bin/python
import configparser
from binance.client import Client
import json
from web3.auto.infura import w3
#import MySQLdb
import pymysql


def getBNBAmountByAPI(key,secret):
    try:
        client = Client(key,secret)
        bnb = client.get_asset_balance(asset='BNB')
        return float(bnb['locked']) + float(bnb['free'])
    except:
        return 0

########################################

kogeconfig = configparser.ConfigParser()
kogeconfig.read("../conf/koge48.conf")
db = pymysql.connect(
  kogeconfig.get("mysql","host"),
  kogeconfig.get("mysql","user"),
  kogeconfig.get("mysql","passwd"),
  kogeconfig.get("mysql","database")
)

c = db.cursor()

c.execute("SELECT * FROM `apikey`")
res = c.fetchall()
amounts=[]
for each in res:
    bnbamount = getBNBAmountByAPI(each[1],each[2])
    if bnbamount!=0 and bnbamount in amounts:
        bnbamount=0
        print("redundant api detected!")
        print(each[1])
    else:
        amounts.append(bnbamount)
    print("api: {} {}".format(each[0],bnbamount))
    c.execute("INSERT INTO bnb (uid,offchain) VALUES (%s,%s) ON DUPLICATE KEY UPDATE offchain=%s",[each[0],bnbamount,bnbamount])

'''
c.execute("SELECT * FROM `eth`")
res = c.fetchall()
for each in res:
    bnbamount = getBNBAmountByETH(each[1])
    #print(bnbamount)
    c.execute("INSERT INTO bnb (uid,onchain) VALUES (%s,%s) ON DUPLICATE KEY UPDATE onchain=%s",[each[0],bnbamount,bnbamount])
'''
db.commit()
