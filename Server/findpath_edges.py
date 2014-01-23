finalList=[]
l=0
P=0
locl=0
locP=0
locList=[]
touchedEdge=[]
# l is the length of the path
# P is the pollution amount
# T is the "target length"

def function(edges,analizedEdge,endEdge,T,maxLength):
	global finalList
	global l
	global P
	global locl
	global locP
	global locList
	global touchedEdge
	# finalList's memorized list's update (the memorized list is updated when locList is better)
	if analizedEdge==endEdge and len(locList)>1:
		if (abs(locl-T)*locP<abs(l-T)*P) or P==0:
			l=locl
			P=locP
			finalList=locList[:]
	elif (locl<T or (abs(locl-T)*locP<abs(l-T)*P and (maxLength==-1 or locl<maxLength))):
		for adi in edges[analizedEdge][2]:
			if touchedEdge[adi]==0: # if not touched
				touchedEdge[adi]=1 # touched
				locList.append(adi) # new road in locList
				locl+=edges[adi][0] # longer path
				locP+=edges[adi][1] # more polluted path
				function(edges,adi,endEdge,T,maxLength)
				locList.pop()
				locl-=edges[adi][0]
				locP-=edges[adi][1]
				touchedEdge[adi]=0

#edges contains the list of the edges. Each edge is a list of three elements: the length, the pollution amount and the list of connected edges' ID
def findpath(edges,startEdge,endEdge,T,maxLength):
	global finalList
	global touchedEdge
	global locl
	global locP
	global locList
	for i in range(0,len(edges)):
		touchedEdge.append(0)
	locl=edges[startEdge][0]
	locP=edges[startEdge][1]
	locList.append(startEdge)
	function(edges,startEdge,endEdge,T,maxLength)
	return finalList
