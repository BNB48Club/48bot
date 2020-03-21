# -*- coding: utf-8 -*-
#!/bin/usr/python
import time
import re
import requests
from jsonfile import  *

class Lottery:
    def __init__(self,theid=None):
        if theid is None:
            self._id = str(int(time.time()))
        else:
            self._id = theid
        self._load()
    def getId(self):
        return self._id
    def _getFile(self):
        return "_data/lottery"+self._id+".json"
    def _save(self):
        saveJson(self._getFile(),self._data)
    def _load(self):
        self._data = loadJson(self._getFile(),{"ticketsup":{},"ticketsdown":{},"result":-1,"kline":[],"prize":1,"kogeup":0,"kogedown":0,"maxup":0,"maxdown":0,"winnerup":[],"winnerdown":[]})
    def msgId(self,themsgid=None):
        if themsgid is None:
            return self._data['msgId']
        else:
            self._data['msgId']=themsgid
            self._save()
    def count(self,uid=None):
        if uid is None:
            up = sum(self._data["ticketsup"].values())
            down = sum(self._data["ticketsdown"].values())
        else:
            if str(uid) in self._data["ticketsup"]:
                up = self._data["ticketsup"][str(uid)]
            else:
                up = 0
            if str(uid) in self._data["ticketsdown"]:
                down = self._data["ticketsdown"][str(uid)]
            else:
                down = 0
        return {"up":up,"down":down}
    def pool(self):
        return {"up":self._data["kogeup"],"down":self._data["kogedown"]}
    def max(self):
        return {"up":self._data["maxup"],"down":self._data["maxdown"]}
    def result(self):
        return self._data["result"]
    def kline(self):
        return self._data["kline"]
    def closed(self):
        return self._data["result"]!=-1
    def buyTicket(self,uid,price,amount,direction):
        if amount <=0 or not direction in ["up","down"]:
            return
        if not str(uid) in self._data["tickets"+direction]:
            self._data["tickets"+direction][str(uid)] = 0

        self._data["tickets"+direction][str(uid)]+= amount
        if self._data["max"+direction] < self._data["tickets"+direction][str(uid)]:
            self._data["max"+direction] = self._data["tickets"+direction][str(uid)]
            self._data["winner"+direction].clear()
            self._data["winner"+direction].append(uid)
        elif self._data["max"+direction] == self._data["tickets"+direction][str(uid)]:
            self._data["winner"+direction].append(uid)

        self._data["koge"+direction] += amount*price
        self._save()
        return self._data["tickets"+direction][str(uid)]

    def winners(self):
        if self.closed():
            return self._data["winner"+self._data["result"]]
        else:
            return []
    def secondWinners(self):
        if self.closed():
            alllist = list(self._data["tickets"+self._data["result"]].keys())
            res=[]
            winners = self.winners()
            for eachstr in alllist:
                if not int(eachstr) in winners:
                    res.append(int(eachstr))
            return res
        else:
            return []
    def reveal(self):
        self._data["kline"] = requests.get("https://api.binance.com/api/v1/klines?symbol=BNBBTC&interval=1d&limit=2").json()[0]
        if self._data["kline"][4] > self._data["kline"][1]:
            self._data["result"] = "up"
        else:
            self._data["result"] = "down"
        self._save()
        return self._data["result"]

if __name__== "__main__":
    e = Lottery()
    print(e.buyTicket(1001,1,101,"up"))
    print(e.buyTicket(1002,10,100,"up"))
    print(e.buyTicket(1003,10,100,"up"))
    print(e.buyTicket(1001,1,101,"down"))
    print(e.buyTicket(1002,10,100,"down"))
    print(e.buyTicket(1003,10,100,"down"))
    print(e._data)
    print(e.reveal())
    print(e._data)
    print(e.winners())
    print(e.secondWinners())
