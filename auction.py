# -*- coding: utf-8 -*-
#!/bin/usr/python
class Auction:
    def __init__(self,fromuser,title):
        self._fromuser = fromuser
        self._bidder = fromuser
        self._price = 0
        self._title = title
    def getLog(self):
        text = "{}拍卖{} \n当前最高出价 {} By {}".format(self._fromuser.mention_markdown(),self._title,self._price,self._bidder.mention_markdown())
        return text
    def bid(self,user,increase):
        self._bidder = user
        self._price += increase
    def deal():
        res = self._price
        self._fromuser = None
        self._bidder = None
        self._price = 0
        self._title = ""
        return res
