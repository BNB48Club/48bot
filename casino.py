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
    @staticmethod
    def getRule(key):
        return u""

class LonghuCasino(Casino):
    TARGET_TEXTS={"LONG":u"龙","HU":u"虎","HE":u"和"}
    @staticmethod
    def getRule(key=None):
        if key == "FULL" or key is None:
            return "龙虎斗\n龙虎各发一张比大小 A最大\n押中拿回本金再得1倍奖励\n押中拿回本金再得8倍奖励"
        elif key in ["LONG","HU"]:
            return "押中拿回本金再得1倍奖励"
        elif key == "HE":
            return "押中拿回本金再得8倍奖励"
            
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
            win="龙"
        elif hudianshu>longdianshu and longdianshu != 0:
            result = "HU"
            win="虎"
        elif longdianshu == hudianshu:
            result = "HE"
            win="和"
        elif longdianshu == 0:
            result = "LONG"
            win="龙"
        else:
            result = "HU"
            win="虎"

        times = 2
        if result == "HE":
            times = 9

        payroll={}
        for each in self._bets[result]:
            payroll[each]=self._bets[result][each]*times

        self.deActive()

        return {"result":[
                            "{}{}".format( huase[longpai/13], dianshu[longdianshu]),
                            "{}{}".format( huase[hupai/13], dianshu[hudianshu])
                        ],
                "payroll":payroll,
                "win":win
                }
