#!/usr/bin/python
import configparser
import json
from web3.auto.infura import w3
#import MySQLdb
import pymysql


file = open("erc20.abi","r")
ERC20_ABI = json.load(file)
BNB_CONTRACT = w3.eth.contract(address='0xB8c77482e45F1F44dE1745F52C74426C631bDD52', abi=ERC20_ABI)

def getBNBAmountByETH(ethaddress):
    global BNB_CONTRACT
    return BNB_CONTRACT.functions.balanceOf(w3.toChecksumAddress(ethaddress)).call()/1000000000000000000

print(w3.eth.accounts)
# BNB_CONTRACT.functions.transfer('0xa350E4b339aB3f685844B4Ca7B0d0C93A68C76d7',500)
