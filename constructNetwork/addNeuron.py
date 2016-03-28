# encoding=utf-8

import json
import jieba
import itertools

from constructNetwork.json_network import makeNeuron, json2network


def addNeuron(inputList,subjectList,reactionList):

    #print("inputList")
    #print(inputList)
    print('subjectList')
    print(subjectList)
    #print('reactionList')
    #print(reactionList)






    #merge with file
    ##add if not exist


    for Names in (inputList):
        if Names not in json2network():
            makeNeuron(Names,{},json2network())

    if len(subjectList) == 1:
        dict = {}
        for ireactionList in inputList:
            #layerElement -- weight
            dict[ireactionList] = 0
            makeNeuron(ireactionList,{subjectList[0]:0},json2network())
        makeNeuron(subjectList[0],dict,json2network())




