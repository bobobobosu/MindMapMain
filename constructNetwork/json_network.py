import json
import ast
from pprint import pprint
import pybrain
import os
#jsonfile = "sample.json"
jsonfile = "NetworkDump.json"

def json2network(jsonfile = "NetworkDump.json"):
    try:
        with open(jsonfile) as json_file:
            json_data = json.load(json_file)
    except:
        with open(jsonfile, 'w') as outfile:
            json.dump([], outfile,indent=4)
        with open(jsonfile) as json_file:
            json_data = json.load(json_file)
    return json_data

def listofNeurons():
    listNetwork = json2network()
    mFlatList = []
    #create flat neurons list
    for d in listNetwork:
        if d["Neuron"]:
            if d["Neuron"] not in mFlatList:
                mFlatList.append(d["Neuron"])
            for k in d["children"]:
                if k["name"]:
                    if k["name"] not in mFlatList:
                        mFlatList.append(k["name"])
    return mFlatList

def makeNeuron(neuron, layer, prevList):
    d = {"Neuron": neuron,
         "children": [{'name': key, "weight": value} for key, value in layer.items()]}
    #if(neuron == 'a'):
        #print("jj")
    #clear duplicates
    for dups in prevList:
        if d["Neuron"] == dups["Neuron"]:
            d = mergeNeuron(d,dups)
            prevList.remove(dups)
    prevList.append(d)

    #generate full map
    with open(jsonfile, 'w') as outfile:
        json.dump(prevList, outfile,indent=4)


def mergeNeuron(net1, net2):
    #preserve net2 value
    mergeNet = net1.copy()
    mergeNet.update(net2)
    net1L = net1["children"]
    net2L = net2["children"]
    result = []
    net1L.extend(net2L)
    for myDict in net1L:
        if myDict not in result:
            result.append(myDict)
    mergeNet["children"] = result
    return mergeNet


def make_unicode(input):
    if type(input) != 'unicode':
        input =  input.decode('utf-8')
        return input
    else:
        return input

def json2googlechart(root = [0,'root',-1,1,'black'],jsonfile = json2network()):
    listNetwork=json2network()
    mFlatList = []
    mFlatListwithnum = []
    mFlatDictwithnum = {}
    par_chilDict = {}
    #create flat neurons list
    for d in listNetwork:
        if d["Neuron"]:
            if d["Neuron"] not in mFlatList:
                mFlatList.append(d["Neuron"])
            for k in d["children"]:
                if k["name"]:
                    if k["name"] not in mFlatList:
                        mFlatList.append(k["name"])
    for index,imFlatList in enumerate(mFlatList):
        mFlatListwithnum.append([index+1,imFlatList])
        mFlatDictwithnum.update({imFlatList:index+1})
    print(mFlatDictwithnum)
    #create parent:child dict
    for d in listNetwork:
        if d["Neuron"]:
            for k in d["children"]:
                if k["name"]:
                    par_chilDict.update({k["name"]:d['Neuron']})
                    #print('-----')
                    #print(d['Neuron'])
                    #print(k["name"])
    print(par_chilDict)
    #update list
    finalList = []
    for neu in mFlatListwithnum:
        parentnum = mFlatDictwithnum.get(par_chilDict.get(neu[1]))
        neu.append(0 if parentnum is None else parentnum)
        neu.append(1)
        neu.append('black')
        print(neu)
        finalList.append(neu)
    finalList.append(root)

    print(finalList)
    #print(jsonfile)


class geneJson2Tree:
    iteratenum = 0
    mFlatList = []
    rroot = ''
    ftreeDict = {'name':rroot,'children':[]}
    def __init__(self,root):
        self.rroot = root
        self.json2tree(self.rroot)

    def json2tree(self,root):
        treeDict = {'name':root,'children':[]}
        listNetwork=json2network()
        for d in listNetwork:
            if d["Neuron"]:
                if d["Neuron"] == root:
                    for k in d["children"]:
                        if k["name"]:
                            if self.iteratenum <100 and k["name"]!=root :

                                self.iteratenum = self.iteratenum+  1
                                treeDict['children'].append(self.json2tree(k["name"]))

                            else:
                                treeDict['children'].append({'name':k["name"],'children':[]})

        print(self.ftreeDict)
        self.ftreeDict=treeDict
        return treeDict

    def getTree(self):
        return self.ftreeDict




'''
root = 'a'
iteratenum=0
jsonfile = json2network()
treeDict = {'name':root,'children':[]}
listNetwork=json2network()
for d in listNetwork:
    if d["Neuron"]:
        if d["Neuron"] == root:
            for k in d["children"]:
                if k["name"]:
                    print(k["name"])


print(treeDict)
ftreeDict=treeDict



                            if iteratenum <20:
                                    iteratenum = iteratenum+  1
                                    #treeDict['children'].append(json2tree(k["name"]))
                                else:
                                    treeDict['children'].append({'name':k["name"],'children':[]})

'''