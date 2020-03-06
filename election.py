# -*- coding: utf-8 -*-
#!/bin/usr/python
import random
import time
import re
from jsonfile import  *

class Election:
    def __init__(self,theid=None):
        if theid is None:
            self._id = str(int(time.time()))
        else:
            self._id = theid
        self._load()
    def getId(self):
        return self._id
    def _getFile(self):
        return "_data/election"+self._id+".json"
    def _save(self):
        saveJson(self._getFile(),self._data)
    def _load(self):
        self._data = loadJson(self._getFile(),{"votees":{},"voters":{}})
    def selfNomi(self,uid):
        theuid=str(uid)
        if theuid in self._data["votees"]:
            return False
        self._data["votees"][theuid]=[];
        self._save()
        return True
    def hasVoted(self,voter,votee):
        voterid = str(voter)
        voteeid = str(votee)
        if not voterid in self._data["voters"]:
            return False
        if not voteeid in self._data["voters"][voterid]:
            return False
        if not voteeid in self._data["votees"]:
            return False
        if not voterid in self._data["votees"][voteeid]:
            return False
        return True
    def _vote(self,voter,votee):
        voterid = str(voter)
        voteeid = str(votee)
        if not voteeid in self._data["votees"]:
            return False
        if not voterid in self._data["voters"]:
            self._data["voters"][voterid]=[]
        if len(self._data["voters"][voterid]) >= 7:
            return False
        if not voteeid in self._data["voters"][voterid]:
            self._data["voters"][voterid].append(voteeid)
        if not voterid in self._data["votees"][voteeid]:
            self._data["votees"][voteeid].append(voterid)
        self._save()

        return True
    def _unvote(self,voter,votee):
        voterid = str(voter)
        voteeid = str(votee)
        if not voteeid in self._data["votees"]:
            return False
        if not voterid in self._data["voters"]:
            self._data["voters"][voterid]=[]
        if voteeid in self._data["voters"][voterid]:
            self._data["voters"][voterid].remove(voteeid)
        if voterid in self._data["votees"][voteeid]:
            self._data["votees"][voteeid].remove(voterid)
        self._save()
        return True
        
    def toggleVote(self,voter,votee):
        voterid = str(voter)
        voteeid = str(votee)
        if self.hasVoted(voterid,voteeid):
            return self._unvote(voterid,voteeid)
        else:
            return self._vote(voterid,voteeid)
    def getVotees(self):
        votees={}
        for each in self._data["votees"]:
            votees[each]=len(self._data["votees"][each])
        ranked = sorted(votees.items(), key=lambda item: item[1],reverse=True)
        #print(ranked)
        results={}
        for eachpair in ranked:
            results[eachpair[0]]=self._data["votees"][eachpair[0]]
            #print(eachpair[0],self._data["votees"][eachpair[0]])
        #print(results)
        return results

if __name__== "__main__":
    e = Election()
    e.selfNomi(1)
    e.selfNomi(2)
    e.selfNomi(3)
    e.toggleVote(1,1)
    e.toggleVote(1,2)
    e.toggleVote(1,3)
    e.toggleVote(2,3)
    e.toggleVote(2,2)
    e.toggleVote(3,3)
    e.getVotees()
