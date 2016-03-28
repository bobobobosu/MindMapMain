# -*- coding: utf-8 -*-
import json
import operator
import pickle

import collections
from pybrain.datasets.supervised import SupervisedDataSet
from pybrain.structure import *
import pybrain.structure.networks
from pybrain.structure.connections.full import FullConnection
from pybrain.structure.modules.sigmoidlayer import SigmoidLayer
from pybrain.structure.networks.recurrent import RecurrentNetwork
import pybrain.tests
from pybrain.supervised.trainers.backprop import BackpropTrainer

import pybrain.supervised.trainers
import pybrain.supervised.trainers

import os
import copy

from pybrain.tools.shortcuts import buildNetwork

from constructNetwork.json_network import json2network


def make_unicode(input):
    if type(input) != 'unicode':
        input = input.decode('utf-8')
        return input
    else:
        return input


def syncNetwork(mnetwork, mFlatNetwork):
    neuronNameDict = {}

    if len(mFlatNetwork) > 0:
        for index in range(0,len(mnetwork[0].inmodules)):
            neuronNameDict.update({mFlatNetwork[index]: index})
        return [mnetwork[0], neuronNameDict]
    else:
        return [mnetwork[0],{}]


'''
def updateJsonWeight(mnetwork, param):
    for mod in mnetwork[0].modules:
        print "Module:", mod.name
        if mod.paramdim > 0:
            print "--parameters:", mod.params
        for conn in mnetwork[0].connections[mod]:
            print "-connection to", conn.outmod.name
            if conn.paramdim > 0:
                print "- parameters", conn.params
        if hasattr(mnetwork[0], "recurrentConns"):
            print "Recurrent connections"
            for conn in mnetwork[0].recurrentConns:
                print "-", conn.inmod.name, " to", conn.outmod.name
                if conn.paramdim > 0:
                    print "- parameters", conn.params
    return
'''


def buildNetworkfromFlat(mFlatNetwork):
    '''
    inoutdim = len(mFlatNetwork)
    if inoutdim == 0:
        inoutdim = 1
    hidlaynum = inoutdim
    mnetwork = [FeedForwardNetwork()]
    inLayer = LinearLayer(inoutdim)
    hiddenLayer = SigmoidLayer(hidlaynum)
    outLayer = LinearLayer(inoutdim)
    mnetwork[0].addInputModule(inLayer)
    mnetwork[0].addModule(hiddenLayer)
    mnetwork[0].addOutputModule(outLayer)
    in_to_hidden = pybrain.FullConnection(inLayer, hiddenLayer)
    hidden_to_out = pybrain.FullConnection(hiddenLayer, outLayer)
    mnetwork[0].addConnection(in_to_hidden)
    mnetwork[0].addConnection(hidden_to_out)
'''

    mHiddenLayer = []
    mInLayer = []
    mOutLayer = []
    nowaBuildList=[]

    listNetwork=json2network()
    mnetwork = [FeedForwardNetwork(),{}]
    for imFlatNetwork in mFlatNetwork:
        nowaBuildList.append(imFlatNetwork.encode('utf-8'))

    for index, neurons in enumerate(nowaBuildList):
        currNeuron = LinearLayer(1, name=str(neurons.decode('utf-8')))
        thisin = LinearLayer(1,name=str(neurons.decode('utf-8')))
        thisout = SigmoidLayer(1)
        mHiddenLayer.append([currNeuron,neurons.decode('utf-8')])
        mInLayer.append([thisin,neurons.decode('utf-8')])
        mOutLayer.append(thisout)

            #print('ADDED:')
            #print(neurons)
        mnetwork[0].addInputModule(thisin)
        mnetwork[0].addModule(currNeuron)
        mnetwork[0].addOutputModule(thisout)
        mnetwork[0].addConnection(FullConnection(thisin,currNeuron))

    for thisout in mOutLayer:
        for currNeuron in mHiddenLayer:
            mnetwork[0].addConnection(FullConnection(currNeuron[0],thisout))
            #mnetwork[0].addConnection(FullConnection(currNeuron,thisout))

    # 建立連接
    for d in listNetwork:
        if d["Neuron"]:
            for k in d["children"]:
                if k["name"]:
                    '''print("TYPE:")
                    print(type(d["Neuron"]))
                    print(type(k["name"]))
                    print(type(mInLayer[0][1]))'''
                    #print(str(d["Neuron"])+" "+str(k["name"]))
                    parent = [i for i in mInLayer if (i[1] == d["Neuron"])]
                    child = [i for i in mHiddenLayer if i[1] == k["name"] and i[1] != d["Neuron"]]
                    '''
                    print("connections")
                    print(d["Neuron"])
                    print(k["name"])'''
                    #print(parent[0][0])
                    #print(child[0][0])

                    if parent and child:


                        #if (str(parent[0][1]) not in prevBuiltList) or (str(child[0][1]) not in prevBuiltList):
                        #print('conn')
                        #print( d["Neuron"]+' '+k["name"])
                        #print(parent[0][0])
                        #print(child[0][0])
                        mnetwork[0].addConnection(FullConnection(parent[0][0], child[0][0]))

    mnetwork[0].sortModules()
    return mnetwork[0]


def NetworkBuild(listNetwork=json2network(), file='NetworkDump.pkl', new=False):
    listNetwork = json2network()
    # 匯入網路
    ##get all nerons
    mFlatNetwork = []
    mnetwork = [FeedForwardNetwork(),{}]
    for d in listNetwork:
         if d["Neuron"]:
             if d["Neuron"] not in mFlatNetwork:
                    mFlatNetwork.append(d["Neuron"])
                    for k in d["children"]:
                        if k["name"]:
                            if k["name"] not in mFlatNetwork:
                                mFlatNetwork.append(k["name"])

    if new == True:
        mnetwork[0] = buildNetworkfromFlat(mFlatNetwork)
        mnetwork = syncNetwork(mnetwork, mFlatNetwork)
    else:
        try:
            mnetwork = pickle.load(open(file, 'rb'))
            mnetwork[0].sortModules
        except:
            mnetwork[0] = buildNetworkfromFlat(mFlatNetwork)

    mnetwork[0].sortModules()
    pickle.dump(mnetwork, open(file, 'wb'))

    '''
    if len(listNetwork) != mnetwork[0].indim and len(listNetwork) != 0 and len(mFlatNetwork) != 0:
        try:
            print("thelens " + str(len(mFlatNetwork)) + " " + str(len(listNetwork)) + " " + str(
                mnetwork[0].indim))
            os.remove(file)
            NetworkBuild(new=True)
        except:
            print("thelens " + str(len(mFlatNetwork)) + " " + str(len(listNetwork)) + " " + str(
                mnetwork[0].indim))
            raise
    # updateJsonWeight(mnetwork,json2network())
    '''
    return mnetwork




def NetworkActivation(reactionList, mnetwork=NetworkBuild()):
    mnetwork = NetworkBuild()
    # activate
    activateVector = makeVector(reactionList, NetworkBuild())

    activeVector = mnetwork[0].activate(activateVector)
    #print(str(activeVector))
    resultDict = Vec2ActiveList(activeVector)
    resultList = sorted(resultDict.items(), key=lambda x: x[1], reverse=True)

    print('RESULTS:')
    # print(reactionList)

    print([[i[0], i[1]] for i in resultList])
    # 可以将其打印出来
    #return Vec2ActiveList(activeVector, mnetwork)
    return [[i[0], i[1]] for i in resultList]


def NetworkTrain(trainDataSet, mnetwork=NetworkBuild(), file='NetworkDump.pkl'):
    mnetwork = NetworkBuild(new=True)

    print('DEBUG')
    #print(trainDataSet)
    #print("lens " + str(len(trainDataSet[0][0])) + " " + str(len(mnetwork[0].inmodules)))
    # 定义数据集的格式
    DS = SupervisedDataSet(len(trainDataSet[0][0]), len(trainDataSet[0][1]))

    for itrainDataSet in trainDataSet:
        indata = itrainDataSet[0]
        outdata = itrainDataSet[1]

        DS.addSample(indata, outdata)

    # 如果要获得里面的输入／输出时，可以用
    # 如果要把数据集切分成训练集和测试集，可以用下面的语句，训练集：测试集＝8:2
    # 为了方便之后的调用，可以把输入和输出拎出来




    # 训练器采用BP算法
    # verbose = True即训练时会把Total error打印出来，库里默认训练集和验证集的比例为4:1，可以在括号里更改
    mnetwork[0].sortModules()
    trainer = BackpropTrainer(mnetwork[0], DS, verbose=True, learningrate=0.01)
    # 0.0575
    # maxEpochs即你需要的最大收敛迭代次数，这里采用的方法是训练至收敛，我一般设为1000
    trainer.trainUntilConvergence(maxEpochs=1000)
    '''
    for mod in mnetwork[0].modules:
        print "Module:", mod.name
        if mod.paramdim > 0:
            print "--parameters:", mod.params
        for conn in mnetwork[0].connections[mod]:
            print "-connection to", conn.outmod.name
            if conn.paramdim > 0:
                print "- parameters", conn.params
        if hasattr(mnetwork[0], "recurrentConns"):
            print "Recurrent connections"
            for conn in mnetwork[0].recurrentConns:
                print "-", conn.inmod.name, " to", conn.outmod.name
                if conn.paramdim > 0:
                    print "- parameters", conn.params
        '''
    pickle.dump(mnetwork, open(file, 'wb'))
    return mnetwork


def makeVector(inputList, mnetwork=NetworkBuild()):
    mnetwork = NetworkBuild()

    outVector = [0] * len(mnetwork[0].inmodules)


    if len(mnetwork[1]) > 0:
        for keys in mnetwork[1].keys():
            for iinputList in inputList:
                if str(keys) == str(iinputList):
                    outVector[mnetwork[1].get(keys)] = 1
    #print(outVector)
    return outVector


def Vec2ActiveList(inputVect, mnetwork=NetworkBuild()):
    mnetwork = NetworkBuild()
    #print("makeVector")
    assert len(mnetwork[0].inmodules) == len(mnetwork[1].keys())

    ActiveList = copy.copy(mnetwork[1])
    for i in range(0, len(inputVect)):
        try:
            key = list(mnetwork[1].keys())[list(mnetwork[1].values()).index(i)]
            # ActiveList.update({mNetwork[1].keys()[mNetwork[1].values().index(i)]: inputVect[i]})
            ActiveList.update({key: inputVect[i]})
        except:
            pass

    return ActiveList


def saveTrainData(subjectList, reactionList, PLKtraindata_PATH):
    if (len(subjectList) and len(reactionList)) != 0:
        trainDataRaw = []
        trainData = []

        try:
            trainDataRaw = pickle.load(open(PLKtraindata_PATH, 'rb'))
        except:
            trainDataRaw = []
        for i in range(0, 1):
            trainDataRaw.append([subjectList, reactionList])
        for trainDataRaws in trainDataRaw:
            trainData.append([makeVector(trainDataRaws[0], NetworkBuild(new=True)),
                              makeVector((trainDataRaws[1]), NetworkBuild(new=True))])

        pickle.dump(trainDataRaw, open(PLKtraindata_PATH, 'wb'))
        return trainData
    '''
    else:
        try:
            trainDataRaw = pickle.load(open(PLKtraindata_PATH, 'rb'))
            trainData = []
            for trainDataRaws in trainDataRaw:
                trainData.append([makeVector(trainDataRaws[0]), makeVector((trainDataRaws[1]))])

            print('TRAIN:')
            print(trainDataRaw)
            pickle.dump(trainDataRaw, open(PLKtraindata_PATH, 'wb'))
            return trainData
        except:
            print('No Train Data Exists')
            return []
    '''


def RNNinterface(subjectList, reactionList, JSONnetwork=json2network(), PLKnetwork_PATH='NetworkDump.pkl',
                 PLKtraindata_PATH='TrainDataDump.pkl', Mode='Init', train=False):
    NetworkBuild(listNetwork=JSONnetwork, file=PLKnetwork_PATH)

    if Mode == 'Activate':
        # try:
        NetworkBuild(listNetwork=JSONnetwork, file=PLKnetwork_PATH)
        result = NetworkActivation(subjectList)
        # except:
        #    os.remove(JSONnetwork_PATH)
        #    NetworkBuild(listNetwork=json2network(), file=PLKnetwork_PATH)
        return result
    if Mode == 'Train':
        trainData = saveTrainData(subjectList, reactionList, PLKtraindata_PATH=PLKtraindata_PATH)
        #print('Data to Train:')
        #print(trainData)
        if len(trainData) > 4 and train == True:
            NetworkTrain(trainData)
    if Mode == 'Build':
        NetworkBuild(listNetwork=JSONnetwork, file=PLKnetwork_PATH)
    if Mode == 'Clean':
        os.remove(PLKnetwork_PATH)
        os.remove(PLKtraindata_PATH)


def printNetwork(PLKnetwork_PATH='NetworkDump.pkl'):
    mnetwork = pickle.load(open(PLKnetwork_PATH, 'rb'))
    netList = []
    '''
    for imnetwork in mnetwork.modules:
        netList.append(str(imnetwork))'''
    return mnetwork[1]
