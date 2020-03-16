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
            "stats":{},
            "membersCount":0,
            "messages":{},#uid:count
            "newMembers":{},#newid:inviter
        }
        self._id = groupid
        self._load()
    def _pre_access(self):
        nowday = str(date.today())
        if not self._data["date"] == nowday:
            self._data["stats"][self._data["date"]] = {
                "membersCount":self._data["membersCount"],
                "newMembers":len(self._data["newMembers"]),
                "speakers":len(self._data["messages"]),
                "messages":sum(self._data["messages"].values())  
            }
            self._data["membersCount"]=0
            self._data["newMembers"]={}
            self._data["messages"]={}
            self._data["date"] = nowday

    def getId(self):
        return self._id
    def _getFile(self):
        return "_data/groupstat{}.json".format(self._id)
    def _save(self):
        saveJson(self._getFile(),self._data)
    def _load(self):
        self._data = loadJson(self._getFile(),self._defaultData.copy())
    def logMembersAcount(self,count):
        self._pre_access()
        self._data["membersCount"]=count
    def logNewMember(self,uid,inviter=0):
        self._pre_access()
        self._data["newMembers"][str(uid)]=inviter
        pass
    def logMessage(self,uid):
        self._pre_access()
        if not str(uid) in self._data["messages"]:
            self._data["messages"][str(uid)]=0
        self._data["messages"][str(uid)]+=1
        pass
    def logQuit(self,uid,kickerid=0):
        self._pre_access()
        pass
    def getReport(self,span=7):
        res="Date,MembersCount(Snapshot),NewMembers,Speakers,Messages\n"
        keys = list(self._data["stats"].keys())
        keys.sort(reverse=True)
        for eachday in keys[:span]:
            res += "{},{},{},{},{}\n".format(
                eachday,
                self._data["stats"][eachday]["membersCount"],
                self._data["stats"][eachday]["newMembers"],
                #len(self._data["stats"][eachday]["leftMembers"]),
                self._data["stats"][eachday]["speakers"],
                self._data["stats"][eachday]["messages"]
            )
        self._save()
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
    print(e.getReport(7))
