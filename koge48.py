import ConfigParser
import random
import json
import datetime
import time
import mysql.connector
import logging
import math

from binance.client import Client



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)

class Koge48:
    SEQUENCE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789o'
    DAY_DECREASE = 0.9
    MINE_SIZE = 1000
    LAMDA = 1/300.00
    def KogeDecrease(self):
        logger.warning("decreasing")
        self._mycursor.execute("SELECT unix_timestamp(ts) FROM `changelog` WHERE `memo` LIKE '%decreasing%' ORDER by height DESC LIMIT 1")        
        try:
            lastts = self._mycursor.fetchone()[0]
            secondsduration = time.time() - lastts
        except:
            secondsduration = 24*3600
        multi_factor = Koge48.DAY_DECREASE**(secondsduration/(24*3600))
        self._mycursor.execute("SELECT `uid`,`bal` FROM `balance`")
        res = self._mycursor.fetchall()
        for each in res:
            uid = each[0]
            bal = each[1]
            self.changeBalance(each[0],each[1]*(multi_factor - 1),'decreasing')
        logger.warning("decreased")
    def BNBAirDrop(self):
        logger.warning("airdroping")
        self._mycursor.execute("SELECT unix_timestamp(ts) FROM `changelog` WHERE `memo` LIKE '%bnbairdrop%' ORDER by height DESC LIMIT 1")        
        try:
            lastts = self._mycursor.fetchone()[0]
            secondsduration = time.time() - lastts
        except:
            secondsduration = 24*3600

        self._mycursor.execute("SELECT *,offchain+onchain as total FROM `bnb`")
        res = self._mycursor.fetchall()

        for each in res:
            bnbamount = each[4]
            if bnbamount > 0:
                self.changeBalance(each[0],secondsduration*bnbamount/(24*3600),'bnbairdrop')
        logger.warning("airdroped")
        
    def __init__(self,host,user,passwd,database):

        self._mydb = mysql.connector.connect(
            host=host,
            user=user,
            passwd=passwd,
            database=database
        )
        self._mycursor = self._mydb.cursor()

        self._tries = 0
        self._cache = {}
        self._minets = time.time()
        return


    def setEthAddress(self,userid,eth):
        updatesql = "INSERT INTO eth (uid,eth) VALUES (%s,%s) ON DUPLICATE KEY UPDATE eth=%s"
        self._mycursor.execute(updatesql,(userid,eth,eth))
        self._mydb.commit()

    def setApiKey(self,userid,apikey,apisecret):
        updatesql = "INSERT INTO apikey (uid,apikey,apisecret) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE apikey=%s,apisecret=%s"
        self._mycursor.execute(updatesql,(userid,apikey,apisecret,apikey,apisecret))
        self._mydb.commit()
        
    def signCheque(self,userid,number):
        self._mycursor.execute("SELECT * FROM `cheque` WHERE `sid` = '{}' AND `did` = 0".format(userid))
        res = self._mycursor.fetchall()
        if len(res) > 0:
            return "ERROR: only one cheque at same time"

        balance = self.getBalance(userid)
        if balance < number:
            return "ERROR: insufficient balance"

        code=""
        for i in range(8):
            code+="".join(random.sample(Koge48.SEQUENCE,4))

        self.changeBalance(userid,-number,"pay cheque "+code)
        newcheque = "INSERT INTO cheque (sid,number,code) VALUES (%s,%s,%s)"
        self._mycursor.execute(newcheque,(userid,number,code))
        self._mydb.commit()
        return code

    def claimCheque(self,userid,code):
        self._mycursor.execute("SELECT * FROM `cheque` WHERE `code` = '{}'".format(code))
        res = self._mycursor.fetchone()
        if res is None or len(res) == 0:
            return 0
        elif res[2] != 0:
            return -1
            #expired
        else:
            number = res[0]
            self.changeBalance(userid,number,"cheque "+res[4],res[1])
            updatesql = "UPDATE `cheque` SET `did` = %s WHERE `code` = %s";
            self._mycursor.execute(updatesql,(userid,code))
            self._mydb.commit()
            return number
        
    def changeBalance(self,userid,number,memo="",source=0):
        balance = self.getBalance(userid)
        assert balance + float(number) > -0.001
        newblocksql = "INSERT INTO changelog (uid,differ,memo,source) VALUES (%s,%s,%s,%s)"
        self._mycursor.execute(newblocksql,(userid,number,memo,source))
        self._mydb.commit()

        self._cache[userid]=balance + float(number)
        #logger.warning("update balance of %s from %s to %s",userid,balance,self._cache[userid])
        return self._cache[userid]

    def _getBalanceFromDb(self,userid):
        self._mycursor.execute("SELECT `bal` FROM `balance` WHERE `uid` = {}".format(userid))
        res = self._mycursor.fetchone()
        if res is None:
            return 0
        else:
            return res[0]
    def getAirDropStatus(self,userid):
        #get eth
        self._mycursor.execute("SELECT eth FROM `eth` WHERE `uid` = {}".format(userid))
        res = self._mycursor.fetchone()
        if not res is None:
            eth = res[0]
        else:
            eth=""
        #get api
        self._mycursor.execute("SELECT apikey,apisecret FROM `apikey` WHERE `uid` = {}".format(userid))
        api = self._mycursor.fetchone()
        if api is None:
            api = ["",""]
        #get bnb balance
        self._mycursor.execute("SELECT onchain,offchain FROM `bnb` WHERE `uid` = {}".format(userid))
        bnb = self._mycursor.fetchone()
        if bnb is None:
            bnb = [0,0]
        #get last 10 airdrop
        self._mycursor.execute("SELECT *,unix_timestamp(ts) AS timestamp FROM `changelog` WHERE  `memo` LIKE '%bnbairdrop%' AND `uid` = {} ORDER BY height DESC LIMIT 10".format(userid))
        airdrops=[]
        currentts = time.time()
        for each in self._mycursor.fetchall():
            airdrops.append({"before":str(datetime.timedelta(seconds=int(currentts - each[6]))),"diff":each[2]})
        return {"eth":eth,"api":api,"bnb":bnb,"airdrops":airdrops}
    def getRecentChanges(self,userid):       
        self._mycursor.execute("SELECT *,unix_timestamp(ts) AS timestamp FROM `changelog` WHERE `uid` = {} ORDER BY height DESC LIMIT 10".format(userid))
        changes=[]
        currentts = time.time()
        for each in self._mycursor.fetchall():
            changes.append({"before":str(datetime.timedelta(seconds=int(currentts - each[6]))),"diff":each[2],"memo":each[4]})
        return changes
        
    def getGroupMiningStatus(self,groupid): 
        sql = "SELECT uid,count(*) as amount FROM `changelog` WHERE source={} AND unix_timestamp(ts)>{} group by uid order by amount desc limit 10".format(groupid,(time.time()-(7*24*3600)))
        self._mycursor.execute(sql)
        #logger.warning(sql)
        top10 = self._mycursor.fetchall()
        #logger.warning(json.dumps(top10,indent=4))
        return top10
    def getTotal(self):
        sql = "SELECT sum(`bal`) FROM `balance` "
        self._mycursor.execute(sql)
        one = self._mycursor.fetchall()
        sql = "SELECT sum(`number`) FROM `cheque` WHERE `did` = 0"
        self._mycursor.execute(sql)
        two = self._mycursor.fetchall()
    
        return one[0][0]+two[0][0]
    def getTopCasino(self):
        betsql = "SELECT `uid`,-sum(`differ`) as `total` FROM `changelog` WHERE `memo` LIKE '%bet %on casino%' GROUP BY `uid` ORDER BY `total` DESC LIMIT 10"
        self._mycursor.execute(betsql)
        top10 = self._mycursor.fetchall()
        return top10
    def getTop(self,amount=10):
        sql = "SELECT `uid`,`bal` FROM `balance` ORDER BY `bal` DESC LIMIT {}".format(amount)
        self._mycursor.execute(sql)
        top10 = self._mycursor.fetchall()
        return top10
    def getBalance(self,userid):
        if userid in self._cache:
            return self._cache[userid]
        else:
            balance = self._getBalanceFromDb(userid)
            self._cache[userid]=balance
            return balance
    def mine(self,minerid,groupid):
        self._tries+=1;
        currentts = time.time()
        duration = currentts - self._minets
        prob = 1-(math.e**(-duration*Koge48.LAMDA))
        self._minets = currentts

        if random.random() < prob:
            self.changeBalance(minerid,Koge48.MINE_SIZE,"mining",groupid)
            self._tries = 0
            logger.warning("%s mined from %s on prob %s",minerid,groupid,prob)
            return Koge48.MINE_SIZE
        else:
            return 0
