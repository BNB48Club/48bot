# -*- coding: utf-8 -*-
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
    LAMDA = 1/6000.0
    BNB48BOT = 571331274
    def KogeDecrease(self):
        userlist = []
        logger.warning("decreasing")
        cursor = self._mycursor()
        cursor.execute("SELECT unix_timestamp(ts) FROM `changelog` WHERE `memo` LIKE '%decreasing%' ORDER by height DESC LIMIT 1")
        try:
            lastts = cursor.fetchone()[0]
            secondsduration = time.time() - lastts
        except:
            secondsduration = 24*3600
        if secondsduration < 1000:
            logger.warning("skip")
            return
        multi_factor = Koge48.DAY_DECREASE**(secondsduration/(24*3600))
        cursor.execute("SELECT `uid`,sum(`differ`) AS `bal` FROM `changelog` GROUP BY `uid`")
        res = cursor.fetchall()
        for each in res:
            uid = each[0]
            userlist.append(uid)
            bal = each[1]
            if abs(bal) > 100:
                self.changeBalance(uid,bal*(multi_factor - 1),'decreasing')
            else:
                cursor.execute("DELETE FROM `changelog` WHERE `uid` = {}",(uid,))
        self._commit(cursor)
        logger.warning("decreased")
        self._close(cursor)
        return userlist
    def BNBAirDrop(self):
        logger.warning("airdroping")
        cursor = self._mycursor()
        cursor.execute("SELECT unix_timestamp(ts) FROM `changelog` WHERE `memo` LIKE '%bnbairdrop%' ORDER by height DESC LIMIT 1")
        try:
            lastts = cursor.fetchone()[0]
            secondsduration = time.time() - lastts
        except:
            secondsduration = 24*3600

        if secondsduration < 1000:
            logger.warning("skip")
            return


        cursor.execute("SELECT *,offchain+onchain as total FROM `bnb`")
        res = cursor.fetchall()

        for each in res:
            bnbamount = each[4]
            if bnbamount > 0:
                self.changeBalance(each[0],secondsduration*bnbamount/(24*3600),'bnbairdrop')
        logger.warning("airdroped")
        self._close(cursor)
        
    def __init__(self,host,user,passwd,database):

        self._host=host
        self._user=user
        self._passwd=passwd
        self._database=database
        self._minets = time.time()
        self._cursor_conn_map = {}
        return

    def _mycursor(self):
        theconn = mysql.connector.connect(
            host=self._host,
            user=self._user,
            passwd=self._passwd,
            database=self._database
        )
        thecursor = theconn.cursor()
        self._cursor_conn_map[thecursor]=theconn
        return thecursor
        
    def _commit(self,cursor):
        self._cursor_conn_map[cursor].commit()

    def _close(self,cursor):
        cursor.close()
        self._cursor_conn_map[cursor].close()
        del self._cursor_conn_map[cursor]

    def setEthAddress(self,userid,eth):
        updatesql = "INSERT INTO eth (uid,eth) VALUES (%s,%s) ON DUPLICATE KEY UPDATE eth=%s"
        cursor = self._mycursor()
        cursor.execute(updatesql,(userid,eth,eth))
        self._commit(cursor)
        self._close(cursor)

    def setApiKey(self,userid,apikey,apisecret):
        updatesql = "INSERT INTO apikey (uid,apikey,apisecret) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE apikey=%s,apisecret=%s"
        cursor = self._mycursor()
        cursor.execute(updatesql,(userid,apikey,apisecret,apikey,apisecret))
        self._commit(cursor)
        self._close(cursor)

    def changeBalance(self,userid,number,memo="",source=0):
        balance = self.getBalance(userid)
        assert userid == Koge48.BNB48BOT  or balance + number >= 0
        newblocksql = "INSERT INTO changelog (uid,differ,memo,source) VALUES (%s,%s,%s,%s)"
        cursor = self._mycursor()
        cursor.execute(newblocksql,(userid,number,memo,source))
        self._commit(cursor)
        self._close(cursor)
        return balance + number

    def changeChequeBalance(self,userid,number,memo="",source=0):
        balance = self._getChequeBalanceFromDb(userid)
        assert balance + number >= 0
        newblocksql = "INSERT INTO cheque (sid,number,memo,source) VALUES (%s,%s,%s,%s)"
        cursor = self._mycursor()
        cursor.execute(newblocksql,(userid,number,memo,source))
        self._commit(cursor)
        self._close(cursor)
        return balance + number

        
    def _getChequeBalanceFromDb(self,userid):
        cursor = self._mycursor()
        cursor.execute("SELECT sum(`number`) FROM `cheque` WHERE `sid` = {}".format(userid,userid))
        res = cursor.fetchone()
        self._close(cursor)
        if res[0] is None:
            return 0
        else:
            return res[0]
    def _getBalanceFromDb(self,userid):
        cursor = self._mycursor()
        cursor.execute("SELECT sum(`differ`) FROM `changelog` WHERE `uid` = {}".format(userid))
        res = cursor.fetchone()
        self._close(cursor)
        if res[0] is None:
            return 0
        else:
            return res[0]
    def getAirDropStatus(self,userid):
        cursor = self._mycursor()
        #get eth
        cursor.execute("SELECT eth FROM `eth` WHERE `uid` = {}".format(userid))
        res = cursor.fetchone()
        if not res is None:
            eth = res[0]
        else:
            eth=""
        #get api
        cursor.execute("SELECT apikey,apisecret FROM `apikey` WHERE `uid` = {}".format(userid))
        api = cursor.fetchone()
        if api is None:
            api = ["",""]
        #get bnb balance
        cursor.execute("SELECT onchain,offchain FROM `bnb` WHERE `uid` = {}".format(userid))
        bnb = cursor.fetchone()
        if bnb is None:
            bnb = [0,0]
        #get last 10 airdrop
        cursor.execute("SELECT *,unix_timestamp(ts) AS timestamp FROM `changelog` WHERE  `memo` LIKE '%bnbairdrop%' AND `uid` = {} ORDER BY height DESC LIMIT 10".format(userid))
        airdrops=[]
        currentts = time.time()
        for each in cursor.fetchall():
            airdrops.append({"before":str(datetime.timedelta(seconds=int(currentts - each[6]))),"diff":each[2]})
        self._close(cursor)
        return {"eth":eth,"api":api,"bnb":bnb,"airdrops":airdrops}
    def getRecentChanges(self,userid):       
        cursor = self._mycursor()
        cursor.execute("SELECT *,unix_timestamp(ts) AS timestamp FROM `changelog` WHERE `uid` = {} ORDER BY height DESC LIMIT 10".format(userid))
        changes=[]
        currentts = time.time()
        for each in cursor.fetchall():
            changes.append({"before":str(datetime.timedelta(seconds=int(currentts - each[6]))),"diff":each[2],"memo":each[4]})
        self._close(cursor)
        return changes
        
    def getGroupMiningStatus(self,groupid): 
        cursor = self._mycursor()
        sql = "SELECT uid,count(*) as amount FROM `changelog` WHERE source={} AND unix_timestamp(ts)>{} group by uid order by amount desc limit 10".format(groupid,(time.time()-(7*24*3600)))
        cursor.execute(sql)
        #logger.warning(sql)
        top10 = cursor.fetchall()
        self._close(cursor)
        return top10
    def getTotal(self):
        return self.getTotalFree()+self.getTotalFrozen()
    def getTotalFree(self):
        cursor = self._mycursor()
        sql = "SELECT sum(`differ`) FROM `changelog` "
        cursor.execute(sql)
        one = cursor.fetchall()
        self._close(cursor)
        return one[0][0]
    def getTotalFrozen(self):
        cursor = self._mycursor()
        sql = "SELECT sum(`number`) FROM `cheque`"
        cursor.execute(sql)
        two = cursor.fetchall()
        self._close(cursor)
        return two[0][0]
    def getTotalDonation(self):
        cursor = self._mycursor()
        sql = "SELECT sum(`number`) FROM `cheque` "
        cursor.execute(sql)
        one = cursor.fetchall()
        self._close(cursor)
        return one[0][0]
    def getTotalBNB(self):
        cursor = self._mycursor()
        sql = "SELECT sum(`offchain`) FROM `bnb` "
        cursor.execute(sql)
        one = cursor.fetchall()
        self._close(cursor)
        return one[0][0]
        
    def getTopProfiter(self):
        cursor = self._mycursor()
        betsql = "SELECT `uid`,sum(`differ`) as `total` FROM `changelog` WHERE `memo` LIKE '%casino%' AND `height` > 507406 GROUP BY `uid` ORDER BY `total` DESC LIMIT 10"
        cursor.execute(betsql)
        top10 = cursor.fetchall()
        self._close(cursor)
        return top10

    def getTopCasino(self):
        cursor = self._mycursor()
        betsql = "SELECT `uid`,-sum(`differ`) as `total` FROM `changelog` WHERE `memo` LIKE '%bet %on casino%' AND `height` > 507406 GROUP BY `uid` ORDER BY `total` DESC LIMIT 10"
        cursor.execute(betsql)
        top10 = cursor.fetchall()
        self._close(cursor)
        return top10
    def getTop(self,amount=10):
        cursor = self._mycursor()
        sql = "SELECT table1.uid, table1.active + COALESCE(table2.deactive,0) AS `total` from (SELECT SUM(`differ`) AS `active` , `uid` FROM `changelog` GROUP BY `uid`) AS `table1` LEFT JOIN (SELECT SUM(`number`) AS `deactive`, `sid` FROM `cheque` GROUP BY `sid`) AS `table2` ON table1.uid = table2.sid ORDER BY `total` DESC LIMIT {}".format(amount)
        cursor.execute(sql)
        top10 = cursor.fetchall()
        self._close(cursor)
        return top10
    def getTopFrozenDonator(self,amount=10):
        cursor = self._mycursor()
        sql = "SELECT `sid`,sum(`number`) AS `sum` FROM `cheque` GROUP BY `sid` ORDER BY `sum` DESC LIMIT {}".format(amount)
        cursor.execute(sql)
        top10 = cursor.fetchall()
        self._close(cursor)
        return top10
    def getTopDonator(self,amount=20):
        cursor = self._mycursor()
        sql = "SELECT `sid`,sum(`number`) AS `sum` FROM `cheque` GROUP BY `sid` ORDER BY `sum` DESC LIMIT {}".format(amount)
        cursor.execute(sql)
        top10 = cursor.fetchall()
        self._close(cursor)
        return top10
    def getBalance(self,userid):
        return self._getBalanceFromDb(userid)
    def getChequeBalance(self,userid):
        return self._getChequeBalanceFromDb(userid)
    def getTotalBalance(self,userid):
        return self._getBalanceFromDb(userid) + self._getChequeBalanceFromDb(userid)
    def mine(self,minerid,groupid):
        currentts = time.time()
        duration = currentts - self._minets
        prob = 1-(math.e**(-duration*Koge48.LAMDA))
        self._minets = currentts

        if random.random() < prob:
            self.changeBalance(minerid,Koge48.MINE_SIZE,"mining",groupid)
            logger.warning("%s mined from %s on prob %s",minerid,groupid,prob)
            return Koge48.MINE_SIZE
        else:
            return 0
