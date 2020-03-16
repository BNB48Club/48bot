#!/usr/bin/python
# -*- coding: utf-8 -*-
from hashrandom import HashRandom

class LonghuCasino:
    TARGET_TEXTS={"LONG":"🐲","HU":"🐯","HE":"🕊"}
    PAYRATES={"LONG":1.05,"HU":1.05,"HE":9}
    @staticmethod
    def getRule(key=None):
        if key == "FULL" or key is None:
            #return "[Please bet]\n🐲 🆚 🐯\nTwo cards from one decker,which is bigger?\n🐲/🐯 ✖️{}\n🕊 ✖️{}".format(LonghuCasino.PAYRATES['HU']+1,LonghuCasino.PAYRATES['HE']+1)
            return "[买定离手]\n🐲 🆚 🐯\n一副扑克牌 龙虎各抽一张牌比大小\n🐲/🐯 ✖️{}\n🕊 ✖️{}".format(LonghuCasino.PAYRATES['HU']+1,LonghuCasino.PAYRATES['HE']+1)
        return "✖️{}".format(LonghuCasino.PAYRATES[key])
            
    def __init__(self):
        self._bets={"LONG":{},"HU":{},"HE":{}}
        self._released = False
        self._needupdate = False
        self._random = None
    def needUpdate(self,value=None):
        if value is None:
            return self._needupdate
        else:
            self._needupdate = value
    
    def getLog(self):
        if self._released:
            text="币安链高度{}\nBlockHash: {}\n[开牌]{}\n".format(self._random.getHeight(),self._random.getHash(),self._result['win'])
        else:
            text=""
        for eachbet in self._bets:
            for eachuserid in self._bets[eachbet]:
                text += "{} {}{}".format(self._bets[eachbet][eachuserid][0],self._bets[eachbet][eachuserid][1],LonghuCasino.TARGET_TEXTS[eachbet])
                if self._released and eachbet == self._result['betresult'] and eachuserid in self._result['payroll']:
                    text += " 🏆 {}".format(self._result['payroll'][eachuserid])
                text += "\n"
        return text
    def bet(self,user,item,amount):
        assert item in ["LONG","HU","HE"]
        if user.id in self._bets[item]:
            self._bets[item][user.id][1]+=amount
        else:
            self._bets[item][user.id]=[user.full_name,amount]
        return self._bets[item][user.id][1]
    def release(self):
        self._random = HashRandom()
        longpai = self._random.randint(0,51)
        hupai = self._random.randint(0,51)
        while hupai == longpai:
            hupai = self._random.randint(0,51)

        huase=["♠️","♥️","♣️","♦️"]
        dianshu = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]

        longdianshu = longpai%13
        hudianshu = hupai%13
        longhuase = longpai//13
        huhuase = hupai//13

        if longdianshu>hudianshu and hudianshu != 0:
            result = "LONG"
            win="🐲"
        elif hudianshu>longdianshu and longdianshu != 0:
            result = "HU"
            win="🐯"
        elif longdianshu == hudianshu:
            result = "HE"
            win="🕊"
        elif longdianshu == 0:
            result = "LONG"
            win="🐲"
        else:
            result = "HU"
            win="🐯"

        times = LonghuCasino.PAYRATES[result]+1

        payroll={}
        for each in self._bets[result]:
            payroll[each]=round(self._bets[result][each][1]*times,1)

        self._released = True
        self._result =  {"result":[
                            "{}{}".format( huase[longpai//13], dianshu[longdianshu]),
                            "{}{}".format( huase[hupai//13], dianshu[hudianshu])
                        ],
                "payroll":payroll,
                "win":win,
                "betresult":result
                }
        return self._result
