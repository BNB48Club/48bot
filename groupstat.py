# -*- coding: utf-8 -*-
#!/bin/usr/python
import random
import time
import re
from jsonfile import  *
from datetime import date

class GroupStat:
    def __init__(self,groupid=None):
        self._defaultData={
            "date":str(date.today()),
            "stats":{}
        }
        self._defaultDaily={
            "messages":{},#uid:count
            "membersCount":0,
            "newMembers":{},#newid:inviter
            "leftMembers":{}#leftid:kickerid
        }
        self._id = groupid
        self._load()
    def _pre_access(self):
        nowday = str(date.today())
        if not self._data["date"] == nowday:
            self._data["date"] = nowday
        if not nowday in self._data["stats"]:
            self._data["stats"][nowday]=self._defaultDaily
    def getId(self):
        return self._id
    def _getFile(self):
        return "_data/groupstat{}.json".format(self._id)
    def _save(self):
        saveJson(self._getFile(),self._data)
    def _load(self):
        self._data = loadJson(self._getFile(),self._defaultData)
    def logMembersAcount(self,count):
        self._pre_access()
        self._data["stats"][self._data["date"]]["membersCount"]=count
        self._save()
    def logNewMember(self,uid,inviter=0):
        self._pre_access()
        self._data["stats"][self._data["date"]]["newMembers"][str(uid)]=inviter
        self._save()
        pass
    def logMessage(self,uid):
        self._pre_access()
        if not str(uid) in self._data["stats"][self._data["date"]]["messages"]:
            self._data["stats"][self._data["date"]]["messages"][str(uid)]=0
        self._data["stats"][self._data["date"]]["messages"][str(uid)]+=1
        self._save()
        pass
    def logQuit(self,uid,kickerid=0):
        self._pre_access()
        self._data["stats"][self._data["date"]]["leftMembers"][str(uid)]=kickerid
        self._save()
        pass
    def getReport(self,span=1):
        res="Date,MembersCount(Snapshot),NewMembers,LeftMembers,Speakers,Messages\n"
        for eachday in list(self._data["stats"])[-span:]:
            res += "{},{},{},{},{},{}\n".format(
                eachday,
                self._data["stats"][eachday]["membersCount"],
                len(self._data["stats"][eachday]["newMembers"]),
                len(self._data["stats"][eachday]["leftMembers"]),
                len(self._data["stats"][eachday]["messages"]),
                sum(self._data["stats"][eachday]["messages"].values())
            )
        return res
            

if __name__== "__main__":
    e = GroupStat(111)
    e.logNewMember(1)
    e.logNewMember(2,1)
    e.logMessage(1)
    e.logMessage(1)
    e.logMessage(1)
    e.logMessage(2)
    e.logQuit(1)
    print(e.getReport(2))
