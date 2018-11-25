# -*- coding: utf-8 -*-
#!/bin/usr/python
import random
class RedPacket:
    def __init__(self,fromuser,balance,amount,title):
        self._fromuser = fromuser
        self._origbalance = balance
        self._balance = balance
        self._origamount = amount
        self._amount = amount
        self._title = title
        self._drawed = {}
    def getLog(self):
        text = "`{}`\n`{}`发了{}个红包{} [Koge48积分](http://bnb48.club/koge48)\n".format(self._title,self._fromuser.full_name,self._origamount,self._origbalance)
        text += "剩余{}个红包{} [Koge48积分](http://bnb48.club/koge48)\n-------------\n".format(self._amount,self._balance)
        for each in self._drawed:
            text += "`{}`抽到{}\n".format(self._drawed[each][0],self._drawed[each][1])
        return text
    def draw(self,user):
        if self._amount < 1 or user.id in self._drawed:
            return -1
        if user.id in self._drawed:
            return 0
        elif self._amount == 1:
            self._amount = 0
            res = self._balance
            self._balance = 0
            self._drawed[user.id]=[user.full_name,res]
            return res
        else:
            average = self._balance/float(self._amount)
            res = round(random.uniform(0,2*average),2)
            self._balance -= res
            self._amount -= 1
            self._drawed[user.id]=[user.full_name,res]
            return res
