import heapq

def rotate(l):
	ris = []
	for i in range(0, len(l)):
		ris.append(l[len(l)-i-1])
	return ris

def dijkstra(adilist,roads,startPoint,endPoint):
	dist = []
	NodeFather = []
	RoadFather = []
	pq = []
	finalList = []
	for i in range(0, len(adilist)):
		dist.append(-1)
		NodeFather.append(-1)
		RoadFather.append(-1)
	dist[startPoint] = 0
	heapq.heappush(pq, [0,startPoint])
	while (len(pq)>0):
		front = heapq.heappop(pq)
		d = front[0]
		u = front[1]
		if u == endPoint:
			while u!=startPoint:
				finalList.append(RoadFather[u])
				u = NodeFather[u]
			return rotate(finalList)
			
		if (d<=dist[u] or dist[u]==-1):
			for j in range(0,len(adilist[u])):
				if roads[adilist[u][j]][0]==u:
					v = roads[adilist[u][j]][1]
				else:
					v = roads[adilist[u][j]][0]
				if dist[u]+roads[adilist[u][j]][2]*roads[adilist[u][j]][3]<dist[v] or dist[v]==-1:
					dist[v] = dist[u] + roads[adilist[u][j]][2]*roads[adilist[u][j]][3]
					NodeFather[v] = u
					RoadFather[v] = adilist[u][j]
					heapq.heappush(pq,[dist[v],v])
		
