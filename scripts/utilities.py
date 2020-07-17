#!/usr/bin/python3

import re
import sys
from time import sleep
from argparse import ArgumentTypeError

def Clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def ParseNumList(string):
    
    idsRange = re.match(r'^(\d+)-(\d+)$', string)
    idsList = re.match(r'^(\d+,)*(\d+)$', string)
    
    if idsRange is not None:
        rstartId = Clamp(int(idsRange.group(1), 10), 0, 65535)
        rendId = Clamp(int(idsRange.group(2), 10), 0, 65535)

        startId = min(rstartId, rendId)
        endId = max(rstartId, rendId)

        return range(startId, endId+1)

    elif idsList is not None:
        idsStrList = idsList.string.split(",")
        unorderedIds = set([Clamp(int(i, 10), 0, 65535) for i in idsStrList])
        return list(unorderedIds)

    else:
        raise ArgumentTypeError("'" + string + "' is not a range or list of numbers. Expected forms are '2', '0-5' or '0,1,2,3'.")

class ProgressBar:

    def __init__(self, total):
        
        self.total = total
        self.current = 0

    def IncrementProgress(self, amount=1):
        self.current = self.current + amount

    def ResetProgress(self):
        
        self.current = 0
        sys.stdout.write('\n')

    def DisplayProgressBar(self):
        
        sys.stdout.write('\r')
        sys.stdout.write("Progress: [%-50s] %d%%" % ('='*int((self.current/float(self.total))*50.0), (self.current/self.total)*100.0))
        sys.stdout.flush()


