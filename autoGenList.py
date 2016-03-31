
import jieba
import jieba.analyse
import nltk

from nltk import word_tokenize


class autoGenList:
    minputLists = []
    seg_list = []
    inputs = []
    def __init__(self,inputList):
        self.inputs = inputList
        for input in self.inputs:
            print(input)
            #self.seg_list = self.seg_list+[[i,1] for i in jieba.cut_for_search(input,HMM=True)]
            self.seg_list = self.seg_list+ [[i[0],i[1]] for i in jieba.analyse.extract_tags(input, topK=False ,withWeight=True)]
            self.seg_list =  list([[i[0],1] for i in nltk.pos_tag(word_tokenize(input))]+self.seg_list)
            self.minputLists = list(self.minputLists+self.seg_list)

    def getminputLists(self):
        self.activateList=[]
        for toappend in  self.minputLists:
            if toappend not in self.activateList and toappend[0] not in self.inputs:
                self.activateList.append(toappend)
        return self.activateList

