# -*- coding: utf-8 -*-
import random
import json
import datetime
import time
import mysql.connector
import logging
import math
import ConfigParser

from binance.client import Client



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)

class Koge48:
    SEQUENCE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789o'
    DAY_DECREASE = 0.9
    MINE_MIN_SIZE = 1
    MINE_DIFFER_SIZE = 9
    BNB48BOT = 571331274
    BNB48LIST = []
    MININGWHITELIST = {}
    JACKPOT = 777000
    PRIZEPOOL = 888000
    #STATSTART = 430820
    STATSTART = 1
    LAMDA = 1.0/600
    '''
    def MINING_LAMDA(self):
        try:
            return 1.0/2000*len(Koge48.MININGWHITELIST)
        except:
            return 1.0/1200
    '''
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
            if bal > 100:
                self.changeBalance(uid,bal*(multi_factor - 1),'decreasing')
            elif bal > 1:
                self.changeBalance(uid,-bal,'decreasing')
        self._commit(cursor)
        logger.warning("decreased")
        self._close(cursor)
        return userlist

    def getTotalWager(self,last=True):
        cursor = self._mycursor()
        if last:
            cursor.execute("SELECT unix_timestamp(ts) FROM `cheque` WHERE `memo` LIKE '%deposit jackpot%' ORDER by id DESC LIMIT 1")
            try:
                lastts = cursor.fetchall()[0][0]
            except:
                lastts = long(time.time())

            betsql = "SELECT `sid`,-sum(`number`) as `total` FROM `cheque` WHERE `id` > %s AND `source` = %s AND `memo` LIKE '%bet %on casino%' AND `number` < 0 AND unix_timestamp(ts) > %s GROUP BY `sid` ORDER BY `total` DESC"
            cursor.execute(betsql,(Koge48.STATSTART,Koge48.BNB48BOT,lastts))
            res = cursor.fetchall()
            self._close(cursor)
            try:
                testfloat = res[0][1]
                return res
            except:
                return []
        else:
            betsql = "SELECT -sum(`number`) as `total` FROM `cheque` WHERE `id` > %s AND `source` = %s AND `memo` LIKE '%bet %on casino%' AND `number` < 0"
            cursor.execute(betsql,(Koge48.STATSTART,Koge48.BNB48BOT))

            res = cursor.fetchall()
            self._close(cursor)
            try:
                return float(res[0][0])
            except:
                return 0
        
    def getHisBetRecords(self,limit = 0):
        cursor = self._mycursor()

        betsql = "SELECT `sid`,-sum(`number`) as `total` FROM `cheque` WHERE `id` > %s AND `source` = %s AND `memo` LIKE '%bet %on casino%' AND `number` < 0 GROUP BY `sid` ORDER BY `total` DESC"
        if int(limit) > 0:
            betsql += " LIMIT {}".format(int(limit))
        cursor.execute(betsql,(Koge48.STATSTART,Koge48.BNB48BOT))
        res = cursor.fetchall()
        self._close(cursor)
        try:
            testfloat = res[0][0]
            return res
        except:
            return []

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
        self._startts = time.time()
        self._minets = {}
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

    def getJackpot(self,targetid,divideby=3):
        balance = self._getChequeBalanceFromDb(Koge48.JACKPOT)
        todivide = int(balance/divideby)
        if todivide > 0:
            self.transferChequeBalance(Koge48.JACKPOT,targetid,todivide,"extract jackpot")
        return todivide

    def transferChequeBalance(self,sourceid,targetid,number,memo=""):
        assert number > 0
        if sourceid != Koge48.BNB48BOT:
            sbalance = self._getChequeBalanceFromDb(sourceid)
            assert sourceid == Koge48.BNB48BOT or sbalance - number >= 0
        else:
            sbalance = number
        newblocksql = "INSERT INTO cheque (sid,number,memo,source) VALUES (%s,%s,%s,%s)"
        cursor = self._mycursor()
        cursor.execute(newblocksql,(sourceid,-number,memo,targetid))
        cursor.execute(newblocksql,(targetid,number,memo,sourceid))
        self._commit(cursor)
        self._close(cursor)
        return sbalance - number
        
    def signCheque(self,userid,number,memo="",source=0):
        assert number > 0
        return self._changeChequeBalance(userid,number,"signCheque",source)
    def burn(self,userid,number):
        assert number > 0
        return self._changeChequeBalance(userid,-number,"burn")
        
    def _changeChequeBalance(self,userid,number,memo="",source=0):
        balance = self._getChequeBalanceFromDb(userid)
        assert userid == Koge48.BNB48BOT or balance + number >= 0
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
        airdrops=[]
        '''
        cursor.execute("SELECT *,unix_timestamp(ts) AS timestamp FROM `changelog` WHERE  `memo` LIKE '%bnbairdrop%' AND `uid` = {} ORDER BY height DESC LIMIT 2".format(userid))
        currentts = time.time()
        for each in cursor.fetchall():
            airdrops.append({"before":str(datetime.timedelta(seconds=int(currentts - each[6]))),"diff":each[2]})
        '''
        self._close(cursor)
        return {"eth":eth,"api":api,"bnb":bnb,"airdrops":airdrops}
    def getChequeRecentChanges(self,userid):       
        cursor = self._mycursor()
        cursor.execute("SELECT *,unix_timestamp(ts) AS timestamp FROM `cheque` WHERE `sid` = {} ORDER BY id DESC LIMIT 10".format(userid))
        changes=[]
        currentts = time.time()
        for each in cursor.fetchall():
            changes.append({"before":str(datetime.timedelta(seconds=int(currentts - each[6]))),"number":each[1],"memo":each[4]})
        self._close(cursor)
        return changes
    def getRecentChanges(self,userid):       
        cursor = self._mycursor()
        cursor.execute("SELECT *,unix_timestamp(ts) AS timestamp FROM `changelog` WHERE `uid` = {} ORDER BY height DESC LIMIT 10".format(userid))
        changes=[]
        currentts = time.time()
        for each in cursor.fetchall():
            changes.append({"before":str(datetime.timedelta(seconds=int(currentts - each[6]))),"diff":each[2],"memo":each[4]})
        self._close(cursor)
        return changes
        
    def getGroupMiningStatus(self): 
        cursor = self._mycursor()
        sql = "SELECT source,count(*) as amount FROM `cheque` WHERE `memo`='mining' AND `number` > 0 AND unix_timestamp(ts)>{} group by source order by amount desc".format(time.time()-(24*3600))
        #print(sql)
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
        
    def getTopGainer(self):
        cursor = self._mycursor()
        betsql = "SELECT `sid`,sum(`number`) as `total` FROM `cheque` WHERE `sid` <> %s AND `memo` LIKE '%casino%' AND `id` > %s GROUP BY `sid` ORDER BY `total` DESC LIMIT 10"
        cursor.execute(betsql,(Koge48.BNB48BOT,Koge48.STATSTART))
        top10 = cursor.fetchall()
        self._close(cursor)
        return top10

    def getTop(self,amount=10):
        cursor = self._mycursor()
        sql = "SELECT table1.uid, table1.active + COALESCE(table2.deactive,0) AS `total` from (SELECT SUM(`differ`) AS `active` , `uid` FROM `changelog` GROUP BY `uid`) AS `table1` LEFT JOIN (SELECT SUM(`number`) AS `deactive`, `sid` FROM `cheque` GROUP BY `sid`) AS `table2` ON table1.uid = table2.sid OR table2.sid = table1.uid ORDER BY `total` DESC LIMIT {}".format(amount)
        cursor.execute(sql)
        top10 = cursor.fetchall()
        self._close(cursor)
        return top10
    def getTopDonator(self,amount=10):
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
        if groupid in self._minets:
            duration = currentts - self._minets[groupid]
        else:
            duration = currentts - self._startts
        self._minets[groupid] = currentts

        if str(minerid) in Koge48.BNB48LIST:
            duration *= 2

        prob = 1-(math.e**(-duration*Koge48.LAMDA))
        if random.random() < prob:
            value = round(Koge48.MINE_MIN_SIZE + Koge48.MINE_DIFFER_SIZE * random.random(),2)
            self._changeChequeBalance(minerid,value,"mining",groupid)
            self._changeChequeBalance(Koge48.BNB48BOT,-value,"mining",groupid)
            #logger.warning("%s mined from %s on prob %s",minerid,groupid,prob)
            return value
        else:
            return 0
if __name__ == '__main__':
    kogeconfig = ConfigParser.ConfigParser()
    kogeconfig.read("conf/koge48.conf")
    koge48core = Koge48(
      kogeconfig.get("mysql","host"),
      kogeconfig.get("mysql","user"),
      kogeconfig.get("mysql","passwd"),
      kogeconfig.get("mysql","database")
    )
    print(koge48core.getTotalWager(True))
    print(koge48core.getTotalWager(False))
