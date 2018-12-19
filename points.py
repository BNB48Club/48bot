import ConfigParser
import random
import json
import datetime
import time
import sqlite3
import logging



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)

class Points:
    def __init__(self,dbfile):

        self._mydb = sqlite3.connect(dbfile,check_same_thread=False)
        self._mycursor = self._mydb.cursor()
        self._mycursor.execute('CREATE TABLE IF NOT EXISTS points(uid INTEGER, name TEXT,groupid INTEGER,balance INTEGER, PRIMARY KEY (uid,groupid))')
        self._prob = 0.06
        return
    def clearUser(self,uid,groupid):
        clearsql = "DELETE FROM points WHERE uid = ? AND groupid = ?"
        self._mycursor.execute(clearsql,(uid,groupid))
        self._mydb.commit()
        return 
        
    def clearGroup(self,groupid):
        clearsql = "DELETE FROM points WHERE groupid = ?"
        self._mycursor.execute(clearsql,(groupid,))
        self._mydb.commit()
        return 

    def getBalance(self,uid,groupid):
        self._mycursor.execute("SELECT balance FROM points WHERE `uid` = {} and groupid = {}".format(uid,groupid))
        res = self._mycursor.fetchone()
        if res is None:
            return 0
        else:
            return res[0]
    '''
    def getRecentChanges(self,uid):       
        self._mycursor.execute("SELECT *,unix_timestamp(ts) AS timestamp FROM `changelog` WHERE `uid` = {} ORDER BY height DESC LIMIT 10".format(uid))
        changes=[]
        currentts = time.time()
        for each in self._mycursor.fetchall():
            changes.append({"before":str(datetime.timedelta(seconds=int(currentts - each[6]))),"diff":each[2],"memo":each[4]})
        return changes
    '''    
    def getRank(self,groupid,rank):
        sql = "SELECT * FROM `points` WHERE groupid = ? order by balance desc limit ?"
        self._mycursor.execute(sql,(groupid,rank))
        top = self._mycursor.fetchall()
        return top[-1]
        
    def getAbove(self,groupid,amount=10): 
        sql = "SELECT * FROM `points` WHERE groupid = ? AND balance >= ? order by balance desc"
        self._mycursor.execute(sql,(groupid,amount))
        toplist = self._mycursor.fetchall()
        return toplist
    def getBoard(self,groupid,top=10): 
        sql = "SELECT * FROM `points` WHERE groupid = ? order by balance desc limit ?"
        self._mycursor.execute(sql,(groupid,top))
        toplist = self._mycursor.fetchall()
        return toplist

    def changeBalance(self,uid,name,groupid,number):
        logger.warning("%s mined one from %s",uid,groupid)
        balance = self.getBalance(uid,groupid)
        res = balance+number
        assert res >= 0
        createsql = "INSERT OR IGNORE INTO points (uid,name,groupid,balance) VALUES (?,?,?,0)"
        self._mycursor.execute(createsql,(uid,name,groupid))
        self._mydb.commit()

        updatesql = "UPDATE points SET balance = ? WHERE uid = ? AND groupid = ?"
        self._mycursor.execute(updatesql,(res,uid,groupid))
        self._mydb.commit()
    def mine(self,user,groupid):
        if random.random()<(self._prob*10/self.getBalance(user.id,groupid)):
            self.changeBalance(user.id,user.full_name,groupid,1)
            return True
        else:
            return False
