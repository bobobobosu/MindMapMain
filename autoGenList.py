
import jieba
import nltk

from nltk import word_tokenize


class autoGenList:
    minputLists = []
    seg_list = []
    def __init__(self,inputList):
            self.inputs = inputList
            for input in self.inputs:
                self.seg_list = self.seg_list+list(jieba.cut_for_search(input))
                self.seg_list =  list(set([i[0] for i in nltk.pos_tag(word_tokenize(input))]+self.seg_list))
                self.minputLists = list(self.minputLists+self.seg_list)
    def getminputLists(self):
        self.minputLists = list(set(self.minputLists))
        return self.minputLists

