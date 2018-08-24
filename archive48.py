import json
import codecs

class Archive48:
    def __init__(self, filepath=None):
        self._filepath=None
        self._data ={}
        self.setFilepath(filepath)
        self.load()

    def testKey(self,key):
        if key in self._data:
            return True
        else:
            return False

    def set(self,key,value):
        self._data[key]=value

    def get(self,key):
        if self.testKey(key):
            return self._data[key]
        else:
            return None
    def setFilepath(self,filepath):
        if isinstance(filepath,basestring):
            self._filepath = filepath

    def load(self,newfilepath=None):
        if newfilepath is None:
            newfilepath = self._filepath
        if not isinstance(newfilepath,basestring):
            self._data = {}
        else:
            file = codecs.open(newfilepath,"r","utf-8")
            self._data = json.load(file)
            file.close()
    def save(self,newfilepath=None):
        if newfilepath is None:
            newfilepath = self._filepath
        file = codecs.open(newfilepath,"w","utf-8")
        file.write(json.dumps(self._data))
        file.flush()
        file.close()
