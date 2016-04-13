import os
from shutil import copyfile
from tkinter.filedialog import askopenfilename

from utils.tkGUI import tkGUI


class inputMain:
    trainORactivate_sta =0
    spl_inputSubjectString = []
    spl_inputReactionString = []
    inputList = []
    subjectList = []
    reactionList = []
    TrainConfig = False
    trainQueue = []

    def gettrainQueue(self):
        return self.trainQueue


    def rawinput(self):
        got = tkGUI([''])
        print("trainconfig")
        print(bool(got[1]))
        self.TrainConfig = bool(got[1])
        self.spl_inputSubjectString = got[0]["subjectList"]
        self.spl_inputReactionString = got[0]["reactionList"]
        self.trainORactivate(self.spl_inputSubjectString,self.spl_inputReactionString)
        #classify
        self.inputList = list(set(self.spl_inputSubjectString+self.spl_inputReactionString))
        self.subjectList = self.spl_inputSubjectString
        self.reactionList =self.spl_inputReactionString

        self.trainORactivate(self.spl_inputSubjectString,self.spl_inputReactionString)


    def trainORactivate(self,spl_inputSubjectString,spl_inputReactionString):
        '''print('LENS')
        print(len(spl_inputSubjectString))
        print(len(spl_inputReactionString))'''
        # 0 train: <sub>+<blank><blank>+<react1><blank><react1><blank><react2>...
        # 1 activate: <activate1><blank><activate1><blank><activate2>...
        if len(spl_inputReactionString)==0 and len(spl_inputSubjectString)!=0:
            self.trainORactivate_sta = 0
        else:
            self.trainORactivate_sta = 1


    def getinput(self):
        return self.inputString
    def getsubjectList(self):
        return self.subjectList
    def getreactionList(self):
        return self.reactionList
    def getinputList(self):
        return self.inputList
    def setsubjectList(self,subjectList):
        self.subjectList = subjectList
    def setreactionList(self,reactionList):
        self.reactionList = reactionList
    def setinputList(self,inputList):
        self.inputList = inputList
    def getTrainConfig(self):
        return self.TrainConfig

    def addobj(self,name):
        test_list = ('')
        print(type(tkGUI(test_list)))
        inputSubjectString =input('\nPlz input '+name+':')
        inputSubjectString = inputSubjectString.rstrip()
        inputSubjectString = inputSubjectString.lstrip()
        spl_inputSubjectString= list(set(inputSubjectString.split('/')))

        #add additional
        if '_f' in spl_inputSubjectString:
            spl_inputSubjectString.remove('_f')
            while True:
                try:
                    addfile = askopenfilename()
                    if not os.path.exists(os.path.join(os.getcwd(),'/files')):
                        os.makedirs(os.path.join(os.getcwd(),'/files'))

                    if addfile != '':
                        newpath = os.path.join(os.getcwd(),'/files',os.path.basename(addfile))
                        copyfile(addfile, newpath)
                        print(addfile)
                        self.filesProcessTrain(newpath)
                        spl_inputSubjectString.append(newpath)
                    else:
                        break

                except:
                    break


        for segments in spl_inputSubjectString:
            #seg_list = jieba.cut_for_search(segments)
            #seg_list = seg_list + list(set([i[0] for i in nltk.pos_tag(word_tokenize(segments))])-seg_list)
            #spl_inputSubjectString = spl_inputSubjectString+list(set(seg_list)-set(spl_inputSubjectString))
            spl_inputSubjectString = [i for i in spl_inputSubjectString if i not in ['',' ','   ,'   '','     ']]
            #self.reactionList = list(itertools.chain(self.reactionList ,seg_list))

        spl_inputSubjectString = list(set(filter(lambda name: name.strip(), spl_inputSubjectString)))
        print(spl_inputSubjectString)
        return spl_inputSubjectString

    def filesProcessTrain(self,file):
        print('')



'''
from tkinter.filedialog import askopenfilename
filename = askopenfilename()
print(filename)
'''
