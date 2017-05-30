import math
from collections import defaultdict
import copy
import json

class Point(object):
	def __init__(self, x, y, cluster=None):
		self.x = float(x)
		self.y = float(y)
		self.cluster = cluster

	def __repr__(self):
		return 'Point({},{})|Cluster({})'.format(self.x, self.y, self.cluster)

# def ManhattanDistance(A, B):
# 	'''A and B are two Point objects containing x and y coordinates'''
# 	return float(abs(B.y - A.y) + abs(B.x - A.x))

#====MANHATTAN DISTANCE

# A = Point(1, 2)
# B = Point(9, 8)
# print ManhattanDistance(A, B)


def euclideanDistance(A, B):
	'''A and B are two Point objects containing x and y coordinates'''
	return math.sqrt(math.pow((B.y - A.y), 2) + math.pow((B.x - A.x), 2))

def closestCentroid(point, centroid_list):
	closest = {'point':centroid_list[0], 'dist':euclideanDistance(point, centroid_list[0])}
	for p in centroid_list:
		dis = euclideanDistance(point, p)
		if dis < closest['dist']:
			closest['point'] = p
			closest['dist'] = dis
	return closest['point']

def newCentroid(cluster):
	x = 0
	y = 0
	n = len(cluster)
	c = cluster[0].cluster
	for p in cluster:
		x+=p.x
		y+=p.y
	return Point(x/n, y/n, cluster=c)


def cluster_iteration(points, centroids):
	'''points and centroids as lists of Point objects'''
	segregated = defaultdict(list)
	for p in points:
		p.cluster = closestCentroid(p, centroids).cluster
		segregated[p.cluster].append(p)
	new_centroids = []
	for c in centroids:
		new_centroids.append(newCentroid(segregated[c.cluster]) if segregated[c.cluster] else c)
	return segregated, new_centroids

def hasMoved(old_centroids, new_centroids):
	status = False

	for i in xrange(len(new_centroids)):
		try:
			if old_centroids[i].x != new_centroids[i].x or old_centroids[i].y != new_centroids[i].y:
				status = True
		except Exception as e:
			print e
	return status

def kmeansCluster(points, initial_centroids, iterations=100):
	old_centroids = copy.copy(initial_centroids)
	i = 0
	while i < iterations:
		clusters, new_centroids = cluster_iteration(points, old_centroids)
		# print new_centroids, clusters
		moved = hasMoved(old_centroids, new_centroids)
		print 'Iteration',i+1
		print 'Clusters =', clusters
		print 'Centroids =', new_centroids
		print 'Centroid has moved =', moved,'\n'
		if not moved:
			print 'Termination reason = Ideal clusters achieved\n' 
			break
		old_centroids = copy.copy(new_centroids)
		i += 1
	if i==iterations: print 'Termination reason = Maximum iteration limit reached\n'
	return clusters, new_centroids


if __name__ == '__main__':
	data = [(1,1), (1,2), (2,1), (2,2), (3,3), (8,8), (8,9), (9,8), (9,9)]
	points = [Point(x,y) for x,y in data]
	print 'Points =',points

	initial_centroids = [Point(-1,-3,cluster=0), Point(10,10,cluster=1)]#, Point(8,8,cluster=2)]
	print 'initial_centroids =',initial_centroids,'\n'

	clusters, centroids = kmeansCluster(points, initial_centroids, 3)
	print 'Final clustered points ='
	for k,v in clusters.iteritems():
		for i in v:
			print i
	print 'Centroids =',centroids




