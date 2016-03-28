import os

import itertools

from NeuralNetwork.RNN import printNetwork, RNNinterface
from NeuralNetwork.drawGraph import drawGraphClass
from constructNetwork import json_network
from inputMain import inputMain
from constructNetwork.json_network import json2network
from constructNetwork.addNeuron import addNeuron

Paths = {'jsonNetworkDump': 'NetworkDump.json',
         'pklNetworkDumo': 'NetworkDump.pkl',
         'pklTrainDataDump': 'TrainDataDump.pkl'}


def Delete(Paths, deljsonDump=False, delpklDump=False, delTrainData=False):
    if deljsonDump == True:
        try:
            os.remove(Paths.get('jsonNetworkDump'))
        except:
            print('Delete Failed:  ' + str(Paths.get('jsonNetworkDump')))

    if delpklDump == True:
        try:
            os.remove(Paths.get('pklNetworkDumo'))
        except:
            print('Delete Failed:  ' + str(Paths.get('pklNetworkDumo')))
    if delTrainData == True:
        try:
            os.remove(Paths.get('pklTrainDataDump'))
        except:
            print('Delete Failed:  ' + str(Paths.get('pklTrainDataDump')))


def detectException(inputList):
    exceptions = ['--reset all', '--reset data/trained', '--reset trained', '--reset data', '']
    inputString = None
    for iexceptions in exceptions:
        if iexceptions in inputList:
            inputString = iexceptions
    if inputString == '--reset all':
        Delete(Paths, delTrainData=True, deljsonDump=True, delpklDump=True)
        try:
            os.remove('weighted_graph.png')
        except:
            print('Delete Failed:  ' + 'weighted_graph.png')
        return True
    if inputString == '--reset data/trained':
        Delete(Paths, delpklDump=True, delTrainData=True)
        return True
    if inputString == '--reset trained':
        Delete(Paths, delpklDump=True)
        return True
    if inputString == '--reset data':
        Delete(Paths, delTrainData=True)
        return True
    if inputString == '':
        print(
            '||||||||||||||Compare json:pickle ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||')
        print(json2network())
        print(printNetwork())
        print(
            '|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||')
        draw()
        return True
    return False


def draw():
    # [node,edge]
    k = [[], []]
    print(json2network())

    k[0] = k[0] + [i["Neuron"] for i in json2network()] + list(set([j["name"] for j in list(
        itertools.chain.from_iterable(i['children'] for i in json2network() if i['children'] != []))]) - set(
        [i["Neuron"] for i in json2network()]))
    print(k[0])
    for neuron in json2network():
        for child in neuron['children']:
            k[1].append([neuron['Neuron'], child['name'], 0.6])
    print('k')
    print(k[0])
    print(k[1])
    mDraw = drawGraphClass()
    mDraw.drawGraph(k)


while True:
    newInputs = []
    mnewinput = None

    # get input
    mnewinput = inputMain()
    mnewinput.rawinput()
    newInputs.append(mnewinput)
    # add autoGen
    #newInputs = newInputs + autoGenList(mnewinput).getminputLists()

    if (detectException(mnewinput.getinputList()) == True):
        continue



    # if Train Mode
    if mnewinput.trainORactivate_sta == 1:
        for newInput in newInputs:
            addNeuron(newInput.getinputList(), newInput.getsubjectList(), newInput.getreactionList())
            print("MODE: Training")

            # add Neuron

            # train
            print(newInput.getTrainConfig())
            # train pics

            # train others
            RNNinterface(newInput.subjectList, newInput.getreactionList(), json2network(), Mode='Activate')
            RNNinterface(newInput.getsubjectList(), newInput.getreactionList(), json2network(), Mode='Train',
                         PLKnetwork_PATH=Paths.get('pklNetworkDumo'), train=newInput.getTrainConfig())

    # if Activation Mode
    else:
        print("MODE: Activation")
        addNeuron(mnewinput.getinputList(), mnewinput.getsubjectList(), mnewinput.getreactionList())
        RNNinterface(mnewinput.subjectList, mnewinput.getsubjectList(), json2network(), Mode='Activate')
        #RNNinterface(mnewinput.getsubjectList(), mnewinput.getsubjectList(), json2network(), Mode='Train',
        #                 PLKnetwork_PATH=Paths.get('pklNetworkDumo'), trainpend=False)

        # mtree = json_network.geneJson2Tree('a').getTree()
        # print(mtree)
        # draw()


        # Activate
