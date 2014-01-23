import numpy

#poi is the list of the points. Each list contains 2 elements: x and y of the point
#sou is a list of 2 elements: x and y of the points whose nearest neighbor must be found
#the function returns the IP of the nearest neighbor of sou

def nns(poi, sou):
	points = numpy.array(poi)
	source = numpy.array(sou)
	return numpy.argmin(((points - source)*(points - source)).sum(1))
