# -*- coding: utf-8 -*-
#!/bin/usr/python
import random
class RedPacket:
    SINGLE_AVG = 1
    def __init__(self,fromuser,balance,amount,title,groupid):
        self._fromuser = fromuser
        self._origbalance = balance
        self._balance = balance
        self._origamount = amount
        self._amount = amount
        self._title = title
        self._drawed = {}
        self._sequence = []
        self._needupdate = False
        self._groupid = groupid
    def needUpdate(self,value=None):
        if value is None:
            return self._needupdate
        else:
            self._needupdate = value
    def getLog(self):
        text = "[现金红包]{}\n{}发了{}个红包\n总计{} Koge\n".format(self._title,self._fromuser.full_name,self._origamount,self._origbalance)
        text += "剩余{}个红包{} Koge\n-------------\n".format(self._amount,self._balance)
        for each in self._sequence:
            text += "{} {} Koge\n".format(self._drawed[each][0],self._drawed[each][1])
        return text
    def left(self):
        return self._amount
    def clear(self):
        if self._amount < 1:
            return -1
        self._amount = 0
        self._drawed[0]=["退回",self._balance]
        self._balance = 0
        self._sequence.append(0)
        return
    def draw(self,user):
        if self._amount < 1:
            return -1
        if user.id in self._drawed:
            return 0
        elif self._amount == 1:
            self._amount = 0
            res = self._balance
            self._balance = 0
            self._drawed[user.id]=[user.full_name,res]
            self._sequence.append(user.id)
            return res
        else:
            average = self._balance/float(self._amount)
            res = max(round(random.uniform(0,2*average),2),0.01)
            self._balance -= res
            self._amount -= 1
            self._drawed[user.id]=[user.full_name,res]
            self._sequence.append(user.id)
            return res
    def balance(self):
        return self._balance
