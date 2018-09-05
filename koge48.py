import random
import json
import time
import ConfigParser
import mysql.connector
import logging

from binance.client import Client



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)

class Koge48:
    @staticmethod
    def getBNBAmount(key,secret):
        try:
            client = Client(key,secret)
            bnb = client.get_asset_balance(asset='BNB')
            return float(bnb['locked']) + float(bnb['free'])
        except:
            return 0
    def BNBAirDrop(self):
        self._mycursor.execute("SELECT * FROM `apikey`")
        res = self._mycursor.fetchall()
        for each in res:
            bnbamount = Koge48.getBNBAmount(each[1],each[2])
            if bnbamount > 0:
                if bnbamount > 50000:
                    bnbamount = 50000
                self.changeBalance(each[0],bnbamount/24,'bnbairdrop')
            time.sleep(1)
        
    def __init__(self,host,user,passwd,database):

        self._mydb = mysql.connector.connect(
            host=host,
            user=user,
            passwd=passwd,
            database=database
        )
        self._mycursor = self._mydb.cursor()

        self._prob = 0.06
        self._tries = 0
        self._cache = {}
        return


    def setApiKey(self,userid,apikey,apisecret):
        updatesql = "INSERT INTO apikey (uid,apikey,apisecret) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE apikey=%s,apisecret=%s"
        self._mycursor.execute(updatesql,(userid,apikey,apisecret,apikey,apisecret))
        self._mydb.commit()
        
    def changeBalance(self,userid,number,memo=""):
        strid = str(userid)
        balance = self.getBalance(strid)
        assert balance + float(number) > -0.001
        newblocksql = "INSERT INTO changelog (uid,differ,memo) VALUES (%s,%s,%s)"
        self._mycursor.execute(newblocksql,(userid,number,memo))
        self._mydb.commit()

        self._cache[strid]=balance + float(number)
        return self._cache[strid]

    def _getBalanceFromDb(self,strid):
        self._mycursor.execute("SELECT `bal` FROM `balance` WHERE `uid` = {}".format(strid))
        res = self._mycursor.fetchone()
        if res is None:
            return 0
        else:
            return res[0]

    def getBalance(self,userid):
        strid = str(userid)
        #if strid in self._cache:
        if False:
            return self._cache[strid]
        else:
            balance = self._getBalanceFromDb(strid)
            self._cache[strid]=balance
            return balance
    def mine(self,minerid):
        strid = str(minerid)
        self._tries+=1;
        if random.random()<self._prob:
            self.changeBalance(strid,1,"mining")            
            self._tries = 0
            logger.warning("{} mined one".format(strid))
            return True
        else:
            return False
