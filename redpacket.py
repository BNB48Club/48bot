# -*- coding: utf-8 -*-
#!/bin/usr/python
import random
import time
import re

def has_hanzi(line):    
    #uline = unicode(line, 'utf-8')
    pattern = '[\u4e00-\u9fa5]+'
    search = re.search(pattern, line)
    if search:
        return True
    else:
        return False

class RedPacket:
    SINGLE_AVG = 1
    def __init__(self,fromuser,balance,amount,title,currency="KOGE"):
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
        self._id = "-1"
        self._currency = currency
        if has_hanzi(self._title):
            self._lang = "CN"
        else:
            self._lang = "EN"
    def export(self):
        res = {}
        res["map"]=self._drawed
        res["id"]=self._id
        res["currency"]=self._currency
        res["title"]=self._title
        res["sender"]=self._fromuser.id
        res["prop"]="BinanceEmail"
        return res
    def getResult():
        return self._drawed
    def currency(self):
        return self._currency
    def sender(self):
        return self._fromuser
    def id(self,nid=None):
        if nid is None:
            return self._id
        else:
            self._id = nid
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
        text = "🧧*[{}]\n{}*\n*{}/{} ({}/{} {})*\n".format(self._title,self._fromuser.full_name,self._amount,self._origamount,round(self._balance,2),self._origbalance,self._currency)
        if "KOGE" != self._currency:
            if "CN"==self._lang:
                text += "📝[填写领奖信息]"
            else:
                text += "📝[Claim {}]".format(self._currency)
            text += "(https://t.me/bnb48_bot?start=fill{})\n".format(self._id)
        text += "---\n"
        for each in self._sequence:
            if 0 == self._amount and each == self._maxid:
                text += "[{}](tg://user?id={}) *{} [🍀]*\n".format(self._drawed[each][0],each,self._drawed[each][1])
            else:
                text += "`{}` {}\n".format(self._drawed[each][0],self._drawed[each][1])
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
            res = round(self._balance,2)
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
        return round(self._balance,2)
