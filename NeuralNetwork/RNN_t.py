import copy
import os
import pickle

from pybrain.datasets.supervised import SupervisedDataSet
from pybrain.structure import *
from pybrain.structure.connections.full import FullConnection
from pybrain.structure.modules.sigmoidlayer import SigmoidLayer
from pybrain.supervised.trainers.backprop import BackpropTrainer

from constructNetwork.json_network import json2network

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
    mnetwork = [RecurrentNetwork(),{}]
    for imFlatNetwork in mFlatNetwork:
        nowaBuildList.append(imFlatNetwork.encode('utf-8'))
    neuron2vecList = {}
    for index, neurons in enumerate(nowaBuildList):
        neuron2vecList.update({str(neurons.decode('utf-8')): index})
        currNeuron = SigmoidLayer(1, name=str(neurons.decode('utf-8')))
        thisin = LinearLayer(1,name=str(neurons.decode('utf-8')))
        thisout = LinearLayer(1,name=str(neurons.decode('utf-8')+'O'))
        mHiddenLayer.append([currNeuron,neurons.decode('utf-8')])
        mInLayer.append([thisin,neurons.decode('utf-8')])
        mOutLayer.append(thisout)

            #print('ADDED:')
            #print(neurons)
        mnetwork[0].addInputModule(thisin)
        mnetwork[0].addModule(currNeuron)
        mnetwork[0].addOutputModule(thisout)
        mnetwork[0].addConnection(FullConnection(thisin,currNeuron))
        #for direct
        mnetwork[0].addConnection(FullConnection(currNeuron,thisout))

    # multilayer
    '''
    for thisout in mOutLayer:
        for currNeuron in mHiddenLayer:
            mnetwork[0].addConnection(FullConnection(currNeuron[0],thisout))
        '''

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
                    parent = [i for i in mHiddenLayer if (i[1] == d["Neuron"])]
                    #child = [i for i in mHiddenLayer if i[1] == k["name"] and i[1] != d["Neuron"]]
                    child = [i for i in mInLayer if i[1] == k["name"] ]

                    #print("connections")
                    #print(d["Neuron"])
                    #print(k["name"])
                    #print(parent[0][0])
                    #print(child[0][0])

                    if parent and child:


                        #if (str(parent[0][1]) not in prevBuiltList) or (str(child[0][1]) not in prevBuiltList):
                        print('conn')
                        print( d["Neuron"]+' '+k["name"])
                        print(parent[0][0])
                        print(child[0][0])

                        mnetwork[0].addRecurrentConnection(FullConnection(parent[0][0], child[0][0]))

    mnetwork[0].sortModules()
    mnetwork[1] = neuron2vecList
    return mnetwork