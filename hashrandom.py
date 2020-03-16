import requests

class HashRandom():
    def __init__(self):
        block = requests.get("https://dex.binance.org/api/v1/node-info").json()["sync_info"]
        self._height=block["latest_block_height"]
        self._hash=block["latest_block_hash"]
        self._link = "https://explorer.binance.org/block/{}".format(self._height)
        self._index = 0
    def getLink(self):
        return self._link
    def getHash(self):
        return self._hash
    def getHeight(self):
        return self._height
    def getInt(self,bytes_=1):
        digits = bytes_*2
        str = self._hash[self._index:self._index+digits]
        self._index += digits
        self._index = self._index%len(self._hash)
        return int(str,16)
    def random(self,bytes_=1):
        return self.getInt(bytes_)/float(pow(2,bytes_*8))
    def randint(self,start,end,bytes_=1):
        startint = int(start)
        endint = int(end+1)
        return int(start + (endint - startint)*self.random(bytes_=1))

if __name__== "__main__":

    therandom = HashRandom()
    i=0
    while i<51:
        print(therandom.randint(0,51))
        i+=1
    try:
        i=0
        while i<51:
            print(therandom.randint(0,51))
            i+=1
    except:
        print("thisis :")
        print(i)

