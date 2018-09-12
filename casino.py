#!/usr/bin/python
# -*- coding: utf-8 -*-
import random

class LonghuCasino:
    TARGET_TEXTS={"LONG":u"龙","HU":u"虎","HE":u"和"}
    @staticmethod
    def getRule(key=None):
        if key == "FULL" or key is None:
            return "龙虎斗\n龙虎各发一张比大小 A最大\n押中龙虎拿回本金再得1倍奖励\n押中和拿回本金再得8倍奖励"
        elif key in ["LONG","HU"]:
            return "押中拿回本金再得1倍奖励"
        elif key == "HE":
            return "押中拿回本金再得8倍奖励"
            
    def __init__(self):
        self._bets={"LONG":{},"HU":{},"HE":{}}
        self._released = False
    
    def getLog(self):
        text="" 
        for eachbet in self._bets:
            for eachuserid in self._bets[eachbet]:
                text += "{}押{}{}".format(self._bets[eachbet][eachuserid][0],self._bets[eachbet][eachuserid][1],LonghuCasino.TARGET_TEXTS[eachbet])
                if self._released and eachbet == self._result['betresult'] and eachuserid in self._result['payroll']:
                    text += " 赢 {}".format(self._result['payroll'][eachuserid])
                text += "\n"
        return text
    def bet(self,user,item,amount):
        assert item == "LONG" or item == "HU" or item == "HE"
        if user.id in self._bets[item]:
            self._bets[item][user.id][1]+=amount
        else:
            self._bets[item][user.id]=[user.full_name,amount]
        return self._bets[item][user.id][1]
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
            payroll[each]=self._bets[result][each][1]*times

        self._released = True
        self._result =  {"result":[
                            "{}{}".format( huase[longpai/13], dianshu[longdianshu]),
                            "{}{}".format( huase[hupai/13], dianshu[hudianshu])
                        ],
                "payroll":payroll,
                "win":win,
                "betresult":result
                }
        return self._result
