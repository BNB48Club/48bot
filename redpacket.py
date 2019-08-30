# -*- coding: utf-8 -*-
#!/bin/usr/python
import random
import time
class RedPacket:
    SINGLE_AVG = 1
    def __init__(self,fromuser,balance,amount,title):
        self._fromuser = fromuser
        self._origbalance = balance
        self._balance = balance
        self._origamount = amount
        self._amount = amount
        self._title = title
        self._drawed = {}
        self._sequence = []
        self._needupdate = False
        self._maxvalue=0
        self._maxid=-1
        self._groupid = -1
        self._messageid = -1
        self._id = -1
    def sender(self):
        return self._fromuser
    def messageId(self,mid=None):
        if mid is None:
            return self._messageid
        else:
            self._messageid = mid
    def groupId(self,gid = None):
        if gid is None:
            return self._groupid
        else:
            self._groupid = gid
    def needUpdate(self,value=None):
        if value is None:
            return self._needupdate
        else:
            self._needupdate = value
    def getLog(self):
        text = "🧧*[{}] by {}*\n*{}/{} shares ({}/{} Koge)*\n---\n".format(self._title,self._fromuser.full_name,self._amount,self._origamount,self._balance,self._origbalance)
        for each in self._sequence:
            if 0 == self._amount and each == self._maxid:
                text += "[{}](tg://user?id={}) {} Koge *[🍀]*\n".format(self._drawed[each][0],each,self._drawed[each][1])
            else:
                text += "{} {} Koge\n".format(self._drawed[each][0],self._drawed[each][1])
        return text
    def left(self):
        return self._amount
    def clear(self):
        if self._amount < 1:
            return -1
        self._amount = 0
        self._drawed[0]=["Refund",self._balance]
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
        else:
            average = self._balance/float(self._amount)
            res = max(round(random.uniform(0,2*average),2),0.01)
            self._balance -= res
            self._amount -= 1
            self._drawed[user.id]=[user.full_name,res]
            self._sequence.append(user.id)

        if res > self._maxvalue:
            self._maxvalue = res
            self._maxid = user.id
        return res
    def balance(self):
        return self._balance
