import SNS.config as conf
import random
import numpy as np
import copy
import time


config = conf.get_config()
# parameters
gene_len = config.point_num-config.zone_num
usedEdge_num = config.point_num-config.zone_num
point_num = config.point_num
zone_num = config.zone_num

individual_num = config.individual_num
iter_num = config.iter_num
mutate_prob = config.mutate_prob

def my_compare(point1, point2):
    if point1.id > point2.id:
        return 1
    else:
        return 0


def clusterEdge(edeg_Set):
    pointCluster = []
    eSet = edeg_Set.copy()
    while len(eSet)>0:
        edgesSetTmp = set();
        pointResult = set()
        edge = eSet.pop()
        edgesSetTmp.add(edge);
        pointResult.add(edge.point1);pointResult.add(edge.point2)
        while len(edgesSetTmp)>0:
            e = edgesSetTmp.pop()
            point1,point2 = e.point1, e.point2
            for item in list(eSet):
                if point1 in item.points or point2 in item.points:
                    eSet.remove(item)
                    edgesSetTmp.add(item);
                    pointResult.add(item.point1); pointResult.add(item.point2)
        pointCluster.append(pointResult.copy())
    return pointCluster

def slectEdge():
    edgeMSTList = list(edgeMSTSet)
    random.shuffle(edgeMSTList)
    eSet = set()
    pointIdSet = set()
    cadidateEdgeSet = set()
    for edge in edgeMSTList:
        if edge.point1.id not in pointIdSet and edge.point2.id not in pointIdSet:
            pointIdSet.add(edge.point1.id);           pointIdSet.add(edge.point2.id)
            eSet.add(edge)
        else:
            cadidateEdgeSet.add(edge)

    for edge in list(cadidateEdgeSet)[:]:
        if edge.point1.id not in pointIdSet or edge.point2.id not in pointIdSet:
            pointIdSet.add(edge.point1.id);           pointIdSet.add(edge.point2.id)
            eSet.add(edge)
            cadidateEdgeSet.remove(edge)

    for i in range(usedEdge_num-len(eSet)):
        edge = cadidateEdgeSet.pop()
        eSet.add(edge)
    return eSet




class Individual:
    def __init__(self, genes=None):
        if genes is None:
            genes = slectEdge()
        self.genes = genes
        self.pointCluster = clusterEdge(genes)
        self.fitness = self.evaluate_fitness()



    def evaluate_fitness(self):
        fitness = 0.0
        m_2 = 0
        for p1_id in range(pointFlowMat.shape[0]):
            for p2_id in range(pointFlowMat.shape[0]):
                m_2 += pointFlowMat[p1_id, p2_id]

        for item in self.pointCluster:
            fitness += self.getOneModularity(item, m_2)
        return fitness

    def getOneModularity(self, pList, m_2):
        Qin = 0
        for p1 in pList:
            for p2 in pList:
                if p1!=p2:
                    Qin += pointFlowMat[p1.id, p2.id]
        Qin = Qin/m_2
        Qtot = 0
        for p1 in pList:
            for p2_id in range(pointFlowMat.shape[0]):
                Qtot += pointFlowMat[p1.id,p2_id]
        Qtot = (Qtot/m_2)**2
        return Qin - Qtot


def getBestResult(edgeSet):
    pSetList = []
    eSet = set()
    pSet = set()
    pfw = open(r"./dataSet/分区点.csv", 'w')
    efw = open(r"./dataSet/分区线.csv", 'w')
    groupInfw = open(r"./dataSet/组内流量和.csv", 'w')
    groupBetweenfw = open(r"./dataSet/组间流量和.csv", 'w')
    i = 1#表示分区编号
    while len(edgeSet)>0:
        e = edgeSet.pop()
        eSet.add(e)
        pSet.add(e.point1);pSet.add(e.point2)
        flag = True
        while flag==True:
            flag = False
            for edge in list(edgeSet)[:]:
                p1 = edge.point1
                p2 = edge.point2
                if p1 in pSet or p2 in pSet:
                    eSet.add(edge)
                    edgeSet.remove(edge)
                    pSet.add(p1)
                    pSet.add(p2)
                    flag =True

        pSetList.append(pSet.copy())
        wirteNodeGroupEdgeGroup(i, pfw, efw, pSet, eSet)
        eSet.clear()
        pSet.clear()
        i += 1
    writeInFlow(pSetList, groupInfw)
    writeGroupFlow(pSetList, groupBetweenfw)
    efw.close()
    pfw.close()
    groupInfw.close()
    groupBetweenfw.close()


def wirteNodeGroupEdgeGroup(i, pfw, efw, pSet, eSet):
    for item in pSet:
        pfw.write(str(i) + "," + str(item.id) + "\n")
    for item in eSet:
        p1, p2 = item.point1, item.point2
        efw.write(str(i) + "," + str(p1.id) + "," + str(p2.id) + "\n")


def writeInFlow(pSetList, groupInfw):
    i = 0
    for pSet in pSetList:
        i += 1
        inSum = 0
        for p1 in pSet:
            for p2 in pSet:
                if p1.id<p2.id:
                    a = pointFlowMat[p1.id, p2.id]
                    inSum += pointFlowMat[p1.id, p2.id]
        if inSum>0:
            groupInfw.write(str(i) + "," + str(inSum)+"\n")


def writeGroupFlow(pSetList, groupBetweenfw):
    for i in range(len(pSetList)):
        for j in range(len(pSetList)):
            if i < j:
                flowNum = 0
                for p1 in pSetList[i]:
                    for p2 in pSetList[j]:
                        flowNum += pointFlowMat[p1.id, p2.id]
                if flowNum != 0:
                    groupBetweenfw.write(str(i+1)+","+str(j+1)+","+str(flowNum)+"\n")




class Ga:
    def __init__(self, input, edgeMSTSet2):
        global pointFlowMat
        pointFlowMat = input
        global edgeMSTSet
        edgeMSTSet = edgeMSTSet2
        self.individual_list= []
        self.best = None
        self.fitness_list = []


    def cross(self):
        startTime = time.time()
        new_gen = []
        random.shuffle(self.individual_list)
        for i in range(0, individual_num - 1, 2):
            genes1, genes2 = self.individual_list[i].genes, self.individual_list[i + 1].genes
            genesCopy1, genesCopy2 = genes1.copy(), genes2.copy()

            geneCopy11 = genesCopy1.copy();
            geneCopy22 = genesCopy2.copy()
            pointDict1 = {}
            for edge in geneCopy11:
                pointDict1[edge.point1.id] = pointDict1.get(edge.point1.id, 0) + 1
                pointDict1[edge.point2.id] = pointDict1.get(edge.point2.id, 0) + 1
            for edge in list(geneCopy11)[:]:
                if pointDict1[edge.point1.id] < 2 or pointDict1[edge.point2.id] < 2:
                    geneCopy11.remove(edge)

            pointDict2 = {}
            for edge in geneCopy22:
                pointDict2[edge.point1.id] = pointDict2.get(edge.point1.id, 0) + 1
                pointDict2[edge.point2.id] = pointDict2.get(edge.point2.id, 0) + 1
            for edge in list(geneCopy22)[:]:
                if pointDict2[edge.point1.id] < 2 or pointDict2[edge.point2.id] < 2:
                    geneCopy22.remove(edge)

            changeEdgeLst1 = list(set(geneCopy11) - set(genesCopy2))
            changeEdgeLst2 = list(set(geneCopy22) - set(genesCopy1))

            if len(changeEdgeLst1) > 0 and len(changeEdgeLst2) > 0:
                edge1 = random.choice(changeEdgeLst1)
                e11 = random.sample(geneCopy11,1)[0]
                genesCopy1.remove(e11);
                genesCopy2.add(edge1)

                edge2 = random.choice(changeEdgeLst2)
                e22 = random.sample(geneCopy22,1)[0]
                genesCopy2.remove(e22);
                genesCopy1.add(edge2)

            new_gen.append(Individual(genesCopy1))
            new_gen.append(Individual(genesCopy2))

        return new_gen
        # return new_gen

    # mutation
    def mutate(self, new_gen):
        startTime = time.time()
        for individual in new_gen:
            mutateSet = edgeMSTSet - individual.genes
            for me in mutateSet:
                if random.random() < mutate_prob:
                    geneCopy33 = individual.genes.copy()
                    pointDict3 = {}
                    for edge in individual.genes:
                        pointDict3[edge.point1.id] = pointDict3.get(edge.point1.id, 0)+1;
                        pointDict3[edge.point2.id] = pointDict3.get(edge.point2.id, 0)+1;
                    for edge in list(geneCopy33)[:]:
                        if pointDict3[edge.point1.id]<2 or pointDict3[edge.point2.id]<2:
                            geneCopy33.remove(edge)

                    se = geneCopy33.pop()
                    individual.genes.remove(se)
                    individual.genes.add(me)
            individual.pointCluster = clusterEdge(individual.genes)
            individual.fitness = individual.evaluate_fitness()
        self.individual_list += new_gen




    def select(self):
        winners = []
        random.shuffle(self.individual_list)
        for i in range(0, len(self.individual_list), 2):
            fitness1 = self.individual_list[i].fitness
            fitness2 = self.individual_list[i+1].fitness
            if fitness1 > fitness2:
                winners.append(self.individual_list[i])
            else:
                winners.append(self.individual_list[i+1])
        self.individual_list = winners

    @staticmethod
    def rank(group):
        for i in range(1, len(group)):
            for j in range(0, len(group) - i):
                if group[j].fitness < group[j + 1].fitness:
                    group[j], group[j + 1] = group[j + 1], group[j]


    def getNextGen(self):
        new_gen = self.cross()
        self.mutate(new_gen)
        self.select()
        for individual in self.individual_list:
            if individual.fitness > self.best.fitness:
                self.best = individual

    def train(self):
        self.individual_list = [Individual() for _ in range(individual_num)]
        self.best = self.individual_list[0]
        bestfitness = 0
        finalResult = None
        for i in range(iter_num):
            self.getNextGen()
            result = self.best.genes.copy()
            self.fitness_list.append(self.best.fitness)
            if bestfitness < round(self.best.fitness,8):
                bestfitness = self.best.fitness
                finalResult = result.copy()
        # getBestResult(finalResult.copy())
        return finalResult,bestfitness, self.fitness_list






