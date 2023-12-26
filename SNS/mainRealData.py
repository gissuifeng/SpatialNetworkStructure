import numpy as np
import SNS.config as conf
from SNS.ga import Ga
import matplotlib.pyplot as plt
import time

config = conf.get_config()
restEdge_num = config.point_num-config.zone_num
np.set_printoptions(suppress=True)
zone_num = config.zone_num
point_num = config.point_num
config = conf.get_config()

class Point:
    def __init__(self, id):
        self.id = id
        self.neighborSet = set()
        self.neighborIdSet = set()
        self.edge = []

    def getDisBetPoints(self, point2):
        return pointFlowMat[self.id, point2.id]

    def __str__(self):
        return "{}".format(self.id)
    def __eq__(self, other):
        if other == None:
            return False
        return self.id == other.id
    def __hash__(self):
        return self.id



class Edge:
    def __init__(self, point1: Point, point2: Point):
        self.point1 = point1
        self.point2 = point2
        self.points = [point1, point2]
        self.ids = [point1.id, point2.id]
        self.dis = point1.getDisBetPoints(point2)

    def __str__(self):
        return "{}---{}".format(self.point1.id,self.point2.id)

    def __eq__(self, other):
        if other == None:
            return False
        elif (isinstance(other, Edge)) == False:
            print(other)
            return False
        elif self.point1 == other.point1 and self.point2==other.point2 :
            return True
        else:
            return False

    def __hash__(self):
        return self.point1.id + self.point2.id + self.point1.id*self.point2.id


def readPointDataFile(city_IdFile):
    pointList = []
    with open(city_IdFile, 'r') as fr:
        fr.readline()
        for line in fr:
            lst = line.strip().split(",")
            id = int(lst[0])
            point = Point(id)
            if point not in pointList:
                pointList.insert(id,point)
    return pointList


def readNeighborFile(pointList,neiDataFile):
    with open(neiDataFile, 'r') as fr:
        fr.readline()
        for line in fr:
            lst = line.strip().split(",")
            id = int(lst[0])
            point:Point = pointList[id]
            for i in lst[1:]:
                point.neighborIdSet.add(int(i))
                point.neighborSet.add(pointList[int(i)])




def MST(pointList, pointFlowMat):
    startTime = time.time()
    pSet = set(pointList)
    edgeSet= set()
    visitiedPointSet = set()
    visitiedPointSet.add(pSet.pop())
    while len(pSet)>0:
        maxNum = -float("inf")
        maxPoint1 = None;        maxPoint2 = None
        for p1 in visitiedPointSet:
            for p2 in pSet :
                if p2.id in p1.neighborIdSet:
                    num = pointFlowMat[p1.id, p2.id]
                    if num > maxNum:
                        maxNum = num
                        maxPoint1 = p1
                        maxPoint2 = p2
        if maxPoint2 != None:
            visitiedPointSet.add(maxPoint2)
            edgeSet.add(Edge(maxPoint1, maxPoint2))
            pSet.remove(maxPoint2)
        else:
            return edgeSet
    return edgeSet




def readFlowData(flowDataFile):
    flowMat = np.zeros([point_num, point_num])
    with open(flowDataFile, 'r') as fr:
        fr.readline()
        for line in fr:
            lst = line.strip().split(",")
            id1 = int(lst[0]);            id2 = int(lst[1]);
            fnum = float(lst[2])
            flowMat[id1, id2] += fnum;            flowMat[id2, id1] += fnum
    return flowMat


def printMat(pointFlowMat):
    len = pointFlowMat.shape[0]
    for i in range(len):
        for j in range(len):
            print("{:^7}".format(pointFlowMat[i,j]),end="")
        print()


def calStrengthMat(pointFlowMat):
    strengthMat = np.zeros([point_num, point_num])
    pointDegree = []
    for i in range(pointFlowMat.shape[0]):
        sum = 0
        for j in range(pointFlowMat.shape[1]):
            sum += pointFlowMat[i,j]
        pointDegree.append(sum)
    for i in range(pointFlowMat.shape[0]):
        for j in range(pointFlowMat.shape[1]):
            if pointDegree[i] == 0 or pointDegree[j]==0:
                strengthMat[i, j] = 0
            else:
                strengthMat[i,j] = round((pointFlowMat[i][j]**2)*(10**5)/(pointDegree[i]*pointDegree[j]),3)
    return strengthMat

def printNoNeighborCity(edgeMSTSet):
    pointSet = set()
    for item in edgeMSTSet:
        pointSet.add(item.point1.id)
        pointSet.add(item.point2.id)
    plist = list(pointSet)
    plist.sort()
    print(plist)


def gaByFlowMat():
    edgeMSTSet = MST(pointList, pointFlowMat)
    ga = Ga(pointFlowMat, edgeMSTSet)
    resultbest, fitnessbest,fitness_list = ga.train()

    print("fitness by interaction volume: ",max(fitness_list))

    plt.rcParams['font.sans-serif'] = ['KaiTi']
    plt.rcParams['axes.unicode_minus'] = False

    fig = plt.figure()
    plt.plot(fitness_list)
    plt.title(u"Fitness curve")
    plt.legend()
    fig.show()
    plt.show()


def gaByStrengMat():
    edgeMSTSet = MST(pointList, pointStrengthMat)
    ga = Ga(pointStrengthMat, edgeMSTSet)
    resultbest, fitnessbest, fitness_list = ga.train()

    print("fitness by interaction strength: ", max(fitness_list))

    plt.rcParams['font.sans-serif'] = ['KaiTi']
    plt.rcParams['axes.unicode_minus'] = False

    fig = plt.figure()
    plt.plot(fitness_list)
    plt.title(u"Fitness curve")
    plt.legend()
    fig.show()
    plt.show()


if __name__ == "__main__":
    flowDataFile = r"./dataSet/realFlowData.csv"
    neiDataFile = r"./dataSet/real_Neighbors.csv"
    city_IdFile = r"./dataSet/real_city_id.csv"

    pointList = readPointDataFile(city_IdFile)
    readNeighborFile(pointList,neiDataFile)
    pointFlowMat = readFlowData(flowDataFile)
    pointStrengthMat = calStrengthMat(pointFlowMat)


    #by interaction strength
    gaByStrengMat()

    #by interaction vloume
    gaByFlowMat()



