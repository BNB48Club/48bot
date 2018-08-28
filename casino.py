#!/usr/bin/python
# -*- coding: utf-8 -*-
import random

class Casino:
    def __init__(self,casinoid):
        self._id = casinoid
        self._active = True
        self._totalbet = 0
        self._something=""
    def setSomething(self,something):
        self._something=something
    def appendSomething(self,something):
        self._something+=something
        return self._something
    def getSomething(self):
        return self._something
    def getId(self):
        return self._id
    def getCreator(self):
        return self._creator
    def deActive(self):
        self._active = False
    def isActive(self):
        return self._active

class LonghuCasino(Casino):
    def __init__(self,id):
        Casino.__init__(self,id)
        self._bets={"LONG":{},"HU":{},"HE":{}}
    def get(self,userid,item):
        return self._bets[item][str(userid)]
    def bet(self,userid,item,amount):
        assert item == "LONG" or item == "HU" or item == "HE"
        strid=str(userid)
        if strid in self._bets[item]:
            self._bets[item][strid]+=amount
        else:
            self._bets[item][strid]=amount
        return self._bets[item][strid]
    def release(self):

        longpai = random.randint(0,51)
        hupai = random.randint(0,51)
        while hupai == longpai:
            hupai = random.randint(0,51)

        huase=[u"♠️",u"♥️",u"♣️",u"♦️"]
        dianshu = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]

        longdianshu = longpai%13
        hudianshu = hupai%13
        longhuase = longpai/13
        huhuase = hupai/13

        if longdianshu>hudianshu and hudianshu != 0:
            result = "LONG"
        elif hudianshu>longdianshu and longdianshu != 0:
            result = "HU"
        elif longdianshu == hudianshu:
            result = "HE"
        elif longdianshu == 0:
            result = "LONG"
        else:
            result = "HU"

        times = 2
        if result == "HE":
            times = 9

        payroll={}
        for each in self._bets[result]:
            payroll[each]=self._bets[result][each]*times

        self.deActive()

        return {"result":u"龙:{}{},虎:{}{}".format(
                        huase[longpai/13],
                        dianshu[longdianshu],
                        huase[hupai/13],
                        dianshu[hudianshu]
                        ),"payroll":payroll}
