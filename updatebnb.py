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

def getBNBAmountByETH(ethaddress):
    ERC20_ABI = json.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_spender","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Approval","type":"event"}]')  # noqa: 501
    BNB = w3.eth.contract(address='0xB8c77482e45F1F44dE1745F52C74426C631bDD52', abi=ERC20_ABI)
    return BNB.functions.balanceOf(w3.toChecksumAddress(ethaddress)).call()/1000000000000000000


########################################

kogeconfig = configparser.ConfigParser()
kogeconfig.read("koge48.conf")
db = pymysql.connect(
  kogeconfig.get("mysql","host"),
  kogeconfig.get("mysql","user"),
  kogeconfig.get("mysql","passwd"),
  kogeconfig.get("mysql","database")
)

c = db.cursor()

c.execute("SELECT * FROM `apikey`")
res = c.fetchall()
for each in res:
    bnbamount = getBNBAmountByAPI(each[1],each[2])
    print(bnbamount)
    c.execute("INSERT INTO bnb (uid,offchain) VALUES (%s,%s) ON DUPLICATE KEY UPDATE offchain=%s",[each[0],bnbamount,bnbamount])

c.execute("SELECT * FROM `eth`")
res = c.fetchall()
for each in res:
    bnbamount = getBNBAmountByETH(each[1])
    print(bnbamount)
    c.execute("INSERT INTO bnb (uid,onchain) VALUES (%s,%s) ON DUPLICATE KEY UPDATE onchain=%s",[each[0],bnbamount,bnbamount])

db.commit()
