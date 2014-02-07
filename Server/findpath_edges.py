import time

class Vars(object):
    def __init__(self):
        self.finalList = []
        self.l = 0
        self.P = 0
        self.locl = 0
        self.locP = 0
        self.locList = []
        self.touchedEdge = []
        self.timestamp_start = time.time()
        self.timeout = 60 * 2  # in seconds
        # l is the length of the path
        # P is the pollution amount
        # T is the "target length"

    def timed_out(self):
        return (time.time() - self.timestamp_start) > self.timeout

def function(v, edges, analizedEdge, endEdge, T, maxLength):
    # finalList's memorized list's update (the memorized list is updated when locList is better)
    # print 'locl: {0}, T: {1}, locP: {2}, P: {3}'.format(locl, T, locP, P)
    if v.timed_out():
        return
    if analizedEdge == endEdge and len(v.locList) > 1:
        print 'lpath: {locl}\npollution: {poll}\nedges: {list}\n'.format(locl=v.locl,poll=v.locP,list=v.locList)
        if (abs(v.locl - T) * v.locP < abs(v.l - T) * v.P) or v.P == 0:
            v.l = v.locl
            v.P = v.locP
            v.finalList = v.locList[:]
    elif (v.locl < T or (abs(v.locl - T) * v.locP < abs(v.l - T) * v.P and (
            maxLength == -1 or v.locl < maxLength))):
        for adi in edges[analizedEdge][2]:
            if v.touchedEdge[adi] == 0: # if not touched
                v.touchedEdge[adi] = 1 # touched
                v.locList.append(adi) # new road in locList
                v.locl += edges[adi][0] # longer path
                v.locP += edges[adi][1] # more polluted path
                function(v, edges, adi, endEdge, T, maxLength)
                v.locList.pop()
                v.locl -= edges[adi][0]
                v.locP -= edges[adi][1]
                v.touchedEdge[adi] = 0

#edges contains the list of the edges. Each edge is a list of three elements: the length, the pollution amount and the list of connected edges' ID
def findpath(edges, startEdge, endEdge, T, maxLength):
    v = Vars()

    for i in range(0, len(edges)):
        v.touchedEdge.append(0)
    v.locl = edges[startEdge][0]
    v.locP = edges[startEdge][1]
    v.locList.append(startEdge)
    function(v, edges, startEdge, endEdge, T, maxLength)
    return v.finalList

