import codecs
import json
def loadJson(filename,default=[]):
    try:
        file=open(filename,"r")
        lastData = json.load(file)
        file.close()
        return lastData
    except:
        return default

def saveJson(filename,content):
    file = codecs.open(filename,"w","utf-8")
    file.write(json.dumps(content))
    file.flush()
    file.close()

