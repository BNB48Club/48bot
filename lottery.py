# -*- coding: utf-8 -*-
#!/bin/usr/python
import random
import time
import re
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
        self._data = loadJson(self._getFile(),{"tickets":[],"result":-1,"prize":1})
    def msgId(self,themsgid=None):
        if themsgid is None:
            return self._data['msgId']
        else:
            self._data['msgId']=themsgid
            self._save()
    def count(self):
        return len(self._data["tickets"])
    def getSet(self):
        return set(self._data["tickets"])
    def result(self):
        return self._data["result"]
    def age(self):
        return time.time() - int(self._id)
    def closed(self):
        return self._data["result"]>-1
    def buyTicket(self,uid,amount=1):
        self._data["tickets"] += ([uid] * amount)
        self._save()
        return [i for i, x in enumerate(self._data["tickets"]) if x == uid][-amount:]
    def query(self,uid):
        return [i for i, x in enumerate(self._data["tickets"]) if x == uid]
    def who(self,index):
        if index > -1:
            return self._data["tickets"][index]
        else:
            return -1

    def reveal(self):
        index = self._data["result"]
        if not self.closed() and self.count()>0:
            index = int(random.random()*len(self._data["tickets"]))
            self._data["result"]=index
            self._save()
        return index

if __name__== "__main__":
    e = Lottery()
    print(e.buyTicket(1,10))
    print(e.buyTicket(2,10))
    print(e._data)
    print(e.getWinner())
    print(e._data)
