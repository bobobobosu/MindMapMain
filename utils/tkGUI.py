"""
tkentrycomplete.py

A tkinter widget that features autocompletion.

Created by Mitja Martini on 2008-11-29.
Updated by Russell Adams, 2011/01/24 to support Python 3 and Combobox.
   Licensed same as original (not specified?), or public domain, whichever is less restrictive.
"""
import ast
import copy
import datetime
import os
import pickle
import shutil
import tkinter
import tkinter.ttk
import urllib.parse
import urllib.request
import urllib.response
import win32clipboard
from os import listdir
from subprocess import call
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from NeuralNetwork.RNN import RNNinterface
from autoGenList import autoGenList
from constructNetwork.json_network import json2network, listofNeurons
from filestorage.utils import retMD5
from filestorage.utils.colortransform import val_to_hex

__version__ = "1.1"

# I may have broken the unicode...
RAW2PRO_dict_path = "RAW2PRO_dict.pkl"
pdfDATA_PATH = "_pdfDATA"
_pdfDATAraw_PATH = "_pdfDATAraw"
_tmp_PATH ="_tmp"
tkinter_umlauts=['']
columns = 60
global TrainConfig
global inputList
global var_subject_activateRdio
global var_reaction_activateRdio
global var_subject_clearRdio






class AutocompleteEntry(tkinter.Entry):
        """
        Subclass of Tkinter.Entry that features autocompletion.

        To enable autocompletion use set_completion_list(list) to define
        a list of possible strings to hit.
        To cycle through hits use down and up arrow keys.
        """
        def set_completion_list(self, completion_list):
                self._completion_list = sorted(completion_list, key=str.lower) # Work with a sorted list
                self._hits = []
                self._hit_index = 0
                self.position = 0
                self.bind('<KeyRelease>', self.handle_keyrelease)

        def autocomplete(self, delta=0):
                """autocomplete the Entry, delta may be 0/1/-1 to cycle through possible hits"""
                if delta: # need to delete selection otherwise we would fix the current position
                        self.delete(self.position, tkinter.END)
                else: # set position to end so selection starts where textentry ended
                        self.position = len(self.get())
                # collect hits
                _hits = []
                for element in self._completion_list:
                        if element.lower().startswith(self.get().lower()):  # Match case-insensitively
                                _hits.append(element)
                # if we have a new hit list, keep this in mind
                if _hits != self._hits:
                        self._hit_index = 0
                        self._hits=_hits
                # only allow cycling if we are in a known hit list
                if _hits == self._hits and self._hits:
                        self._hit_index = (self._hit_index + delta) % len(self._hits)
                # now finally perform the auto completion
                if self._hits:
                        self.delete(0,tkinter.END)
                        self.insert(0,self._hits[self._hit_index])
                        self.select_range(self.position,tkinter.END)

        def handle_keyrelease(self, event):
                """event handler for the keyrelease event on this widget"""
                if event.keysym == "BackSpace":
                        self.delete(self.index(tkinter.INSERT), tkinter.END)
                        self.position = self.index(tkinter.END)
                if event.keysym == "Left":
                        if self.position < self.index(tkinter.END): # delete the selection
                                self.delete(self.position, tkinter.END)
                        else:
                                self.position = self.position-1 # delete one character
                                self.delete(self.position, tkinter.END)
                if event.keysym == "Right":
                        self.position = self.index(tkinter.END) # go to end (no selection)
                if event.keysym == "Down":
                        self.autocomplete(1) # cycle to next hit
                if event.keysym == "Up":
                        self.autocomplete(-1) # cycle to previous hit
                if len(event.keysym) == 1 or event.keysym in tkinter_umlauts:
                        self.autocomplete()

class AutocompleteCombobox(ttk.Combobox):

        def set_completion_list(self, completion_list):
                """Use our completion list as our drop down selection menu, arrows move through menu."""
                self._completion_list = sorted(completion_list, key=str.lower) # Work with a sorted list
                self._hits = []
                self._hit_index = 0
                self.position = 0
                self.bind('<KeyRelease>', self.handle_keyrelease)
                self['values'] = self._completion_list  # Setup our popup menu

        def autocomplete(self, delta=0):

                """autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
                if delta: # need to delete selection otherwise we would fix the current position
                        self.delete(self.position, tkinter.END)
                else: # set position to end so selection starts where textentry ended
                        self.position = len(self.get())
                # collect hits
                _hits = []
                for element in self._completion_list:
                        if element.lower().startswith(self.get().lower()): # Match case insensitively
                                _hits.append(element)
                # if we have a new hit list, keep this in mind
                if _hits != self._hits:
                        self._hit_index = 0
                        self._hits=_hits
                # only allow cycling if we are in a known hit list
                if _hits == self._hits and self._hits:
                        self._hit_index = (self._hit_index + delta) % len(self._hits)
                # now finally perform the auto completion
                self.position_copy = copy.copy(self.position)
                if self._hits:
                        self.delete(0,tkinter.END)
                        self.insert(0,self._hits[self._hit_index])
                        self.select_range(self.position_copy,tkinter.END)
                self.position = self.position_copy

        def handle_keyrelease(self, event):
                """event handler for the keyrelease event on this widget""" '''
                if event.keysym == "BackSpace":
                        self.delete(self.index(tkinter.INSERT), tkinter.END)
                        self.position = self.index(tkinter.END)

                if event.keysym == "Left":
                        if self.position < self.index(tkinter.END): # delete the selection
                                self.delete(self.position, tkinter.END)
                        else:
                                self.position = self.position-1 # delete one character
                                self.delete(self.position, tkinter.END)
                if event.keysym == "Right":
                        self.position = self.index(tkinter.END) # go to end (no selection)
                if len(event.keysym) == 1:
                        self.autocomplete()
                # No need for up/down, we'll jump to the popup
                # list at the position of the autocompletion
'''

def gen_RAW2PRO_dict(RAW,PRO,path):
    try:
        RAW2PRO_dict = pickle.load(open(path, 'rb'))
    except:
        RAW2PRO_dict = []
    RAW2PRO_dict.append({"RAW":RAW,"PRO":PRO})
    pickle.dump(RAW2PRO_dict, open(path, 'wb'))
def chk_RAW2PRO_dict(RAW,path):
    try:
        RAW2PRO_dict = pickle.load(open(path, 'rb'))
        if RAW in [i["RAW"] for i in RAW2PRO_dict] or RAW in [j["PRO"] for j in RAW2PRO_dict]:
            return True
        else:
            return False
    except:
        RAW2PRO_dict=[]
        pickle.dump(RAW2PRO_dict, open(path, 'wb'))
        return False

def tkGUI(test_list):
        """Run a mini application to test the AutocompleteEntry Widget."""
        root = tkinter.Tk(className='Dynamic MindMap')
        inputList = {"subjectList":[],"reactionList":[]}
        var_subject_activateRdio = []
        var_reaction_activateRdio=[]
        rec_rdiotoadd = []
        sub_rdiotoadd = []
        try:
            previnputList = pickle.load(open('searchHistory', 'rb'))
            print('thus prev')
            print(previnputList)
        except:
            previnputList=[]

        #specify window position
        w = 1350 # width for the Tk root
        h = 200 # height for the Tk root

        # get screen width and height
        ws = root.winfo_screenwidth() # width of the screen
        hs = root.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk root window
        #x = (ws/2) - (w/2)
        #y = (hs/2) - (h/2)
        x = ws-w
        y = hs-h-100

        # set the dimensions of the screen
        # and where it is placed
        root.geometry('%dx%d+%d+%d' % (w, h, x, y))

        #always on top
        root.wm_attributes('-topmost', 1)


        for i in range(0,columns-3):
            var_subject_activateRdio.append(StringVar())
            var_subject_activateRdio[i].set("")
            var_reaction_activateRdio.append(StringVar())
            var_reaction_activateRdio[i].set("")

        def choosefile_oncick(event=None,mode=""):
            filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
            _pdfDATA_PATH = "_pdfDATA"
            _pdfDATAraw_PATH = "_pdfDATAraw"
            _tmp_PATH ="_tmp"

            _pdfDATA_file = ""
            _pdfDATA_filenameext = ""
            _pdfDATAraw_file = os.path.join(_pdfDATAraw_PATH,retMD5.md5(filename))
            _pdfDATAraw_filenameext = os.path.basename(_pdfDATAraw_file)
            _pdfDATAraw_file_hash = os.path.splitext(retMD5.md5(filename))[0]
            _pdfDATAraw_filename = ""
            _pdfDATAraw_filext = ""
            _tmp_file = ""
            _tmp_file_woext = ""
            _tmp_filenameext = ""
            _tmp_filename = ""
            _tmp_filext = ""
            if chk_RAW2PRO_dict(_pdfDATAraw_file_hash,RAW2PRO_dict_path) == False:
                print("This is new")
                try:
                    shutil.copy2(filename,os.path.join(_pdfDATAraw_PATH,retMD5.md5(filename)))
                    _pdfDATAraw_file = os.path.join(_pdfDATAraw_PATH,retMD5.md5(filename))
                    _pdfDATAraw_filenameext = os.path.basename(_pdfDATAraw_file)
                    _pdfDATAraw_filename = os.path.splitext(os.path.basename(_pdfDATAraw_file))[0]
                    _pdfDATAraw_filext = os.path.splitext(os.path.basename(_pdfDATAraw_file))[1]
                    _tmp_file =  os.path.join(_tmp_PATH,_pdfDATAraw_filenameext)
                    _tmp_filenameext = _pdfDATAraw_filenameext
                    _tmp_file_woext = os.path.join(_tmp_PATH,_pdfDATAraw_filename)
                except:
                    raise


                OCR = False

                FineCMD_PATH = "\""+"C:\\Program Files (x86)\\ABBYY FineReader 12\\FineCmd.exe"+"\""
                OfficeToPDF_PATH = "\""+"exe\OfficeToPDF.exe"+"\""


                if OCR == False and os.path.splitext(_pdfDATAraw_file)[1] in [".pdf"]:
                    shutil.copy2(_pdfDATAraw_file,os.path.join(_tmp_PATH,os.path.basename(_pdfDATAraw_file)))
                    _tmp_file =_tmp_file_woext+".pdf"
                elif OCR == False and os.path.splitext(_pdfDATAraw_file)[1] in [".doc", ".dot",  ".docx", ".dotx", ".docm", ".dotm", ".rtf", ".wpd"
                                                       ".xls", ".xlsx", ".xlsm", ".xlsb", ".xlt", ".xltx", ".xltm", ".csv"
                                                       ".ppt", ".pptx", ".pptm", ".pps", ".ppsx", ".ppsm", ".pot", ".potx", ".potm"
                                                       ".vsd", ".vsdx", ".vsdm", ".svg",".pub",".msg", ".vcf", ".ics",".mpp"
                                                       ".odt", ".odp", ".ods",".txt"]:
                    print(str(OfficeToPDF_PATH+" "+_pdfDATAraw_file+" "+_tmp_file_woext+".pdf"))
                    call(str(OfficeToPDF_PATH+" "+_pdfDATAraw_file+" "+_tmp_file_woext+".pdf"),shell=True)
                    _tmp_file = _tmp_file_woext+".pdf"
                else:
                    shutil.copy2(_pdfDATAraw_file,_tmp_file)
                    tmp_file =_tmp_file
                    OCR = True

                if OCR == True:
                    modified_tmp_filenameext = "old_"+_tmp_filenameext
                    modified_tmp_file = os.path.join(os.path.dirname(_tmp_file),modified_tmp_filenameext)
                    os.rename(_tmp_file,modified_tmp_file)
                    print(str(FineCMD_PATH+" "+str(modified_tmp_file)+" /lang Mixed /out "+_tmp_file_woext+".pdf"+" /quit"))
                    call(str(FineCMD_PATH+" "+str(modified_tmp_file)+" /lang Mixed /out "+_tmp_file_woext+".pdf"+" /quit"),shell=True)
                    os.remove(modified_tmp_file)
                    _tmp_file=_tmp_file_woext+".pdf"

                print(filename)
                #copy&rename using MD5
                _pdfDATA_file = os.path.join(_pdfDATA_PATH,retMD5.md5(_tmp_file))
                _pdfDATA_filenameext = os.path.basename(_pdfDATA_file)
                _pdfDATA_file_hash = os.path.splitext(os.path.basename(_pdfDATA_file))[0]
                shutil.copy2(_tmp_file,_pdfDATA_file)
                #clean tmp
                os.remove(_tmp_file)
                gen_RAW2PRO_dict(_pdfDATAraw_file_hash,_pdfDATA_file_hash,RAW2PRO_dict_path)

            if mode == "Subject":
                if _pdfDATAraw_file_hash not in inputList["subjectList"]:
                    inputList["subjectList"].append(os.path.basename(_pdfDATA_file_hash))
                appendInput()

            elif mode == "Reaction":
                if _pdfDATAraw_file_hash not in inputList["reactionList"]:
                    inputList["reactionList"].append(os.path.basename(_pdfDATA_file_hash))
                appendInput()
            os.system('start '+_pdfDATA_file)

        #previnputList = [{"subjectList":[],"reactionList":[]}]


        def updateinputListHistory():
            tmp = {"subjectList":inputList.copy()["subjectList"],"reactionList":inputList.copy()["reactionList"]}
            if len(previnputList)<1000:
                if len(previnputList)>0:
                    if previnputList[len(previnputList)-1] != copy.deepcopy(tmp):
                        #if previnputList[len(previnputList)-1] != inputList
                        previnputList.append(copy.deepcopy(tmp))
                else:
                    previnputList.append(copy.deepcopy(tmp))


            else:
                if previnputList[len(previnputList)-1] != copy.deepcopy(tmp):
                    previnputList.pop(0)
                    previnputList.append(copy.deepcopy(tmp))
            return previnputList


        def setprev_inputListHistory():
            if len(previnputList) >1:
                nonlocal inputList
                inputList = copy.deepcopy(previnputList[len(previnputList)-2])

                previnputList.pop(len(previnputList)-1)
                previnputList.pop(len(previnputList)-1)

                appendInput(historymode = False)
            return inputList


        def appendInput(target="",historymode=False,mode='append'):
            #data from combo
            if str(comboSubject.get()) != "" and str(comboSubject.get()) not in inputList["subjectList"]:
                for toappend in macro_expand([comboSubject.get()]):
                    inputList["subjectList"].append(toappend)
            if str(comboReaction.get()) != "" and str(comboReaction.get()) not in inputList["reactionList"] :
                for toappend in macro_expand([comboReaction.get()]):
                    inputList["reactionList"].append(toappend)
            #data from clipboard
            if target in ["subjectList","reactionList"]:
                win32clipboard.OpenClipboard()
                data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                if target == "subjectList" and str(data) != "" and str(data) not in inputList["subjectList"]:
                    for toappend in macro_expand([data]):
                        inputList["subjectList"].append(toappend)
                if target == "reactionList" and str(data) != "" and str(data) not in inputList["reactionList"] :
                    for toappend in macro_expand([data]):
                        inputList["reactionList"].append(toappend)
            #data from radiobtn
            appendupdateSticky_subject()
            appendupdateSticky_reaction()

            #mode= replaewithTextbox
            if mode=='replaewithTextbox':
                inputList["subjectList"]=list( str(subjectT.get("1.0",END)).strip('\n').split(','))
                inputList["reactionList"]= list(str(reactionT.get("1.0",END)).strip('\n').split(','))

            #clean
            inputList["subjectList"] = list(set(inputList["subjectList"]))
            inputList["reactionList"] = list(set(inputList["reactionList"]))
            inputList["subjectList"] = [i for i in inputList["subjectList"] if i != ""]
            inputList["reactionList"] = [i for i in inputList["reactionList"] if i != ""]

            subjectT.delete(1.0,END)
            reactionT.delete(1.0,END)
            for subject in inputList["subjectList"]:
                subjectT.insert(1.0, subject+",")
            for reaction in inputList["reactionList"]:
                reactionT.insert(1.0, reaction+",")

            if historymode == False:
                updateinputListHistory()
                #previnputList.pop(len(previnputList)-1)

            comboSubject.delete(0, 'end')
            comboReaction.delete(0, 'end')

            #if toclear
            if  var_subject_clearRdio.get() ==True:
                inputList["subjectList"] = []
                inputList["reactionList"] = []

            nonlocal rec_rdiotoadd
            rec_rdiotoadd = []
            nonlocal sub_rdiotoadd
            sub_rdiotoadd = []
            for var in var_subject_activateRdio:
                var.set("")
            for var in var_reaction_activateRdio:
                var.set("")




        def returnInput():
            appendInput()
            '''
            if len(inputList["subjectList"])>0 and len(inputList["reactionList"])>0:

                messagebox.showinfo(
                    title="TRAIN",
                    message="Subject: "+str(inputList["subjectList"])+ "\nReaction: "+str(inputList["reactionList"])
                )
            elif len(inputList["subjectList"])>0 and len(inputList["reactionList"])==0:

                messagebox.showinfo(
                    title="ACTIVATE",
                    message="Subject: "+str(inputList["subjectList"])
                )
            else:
                messagebox.showinfo(
                    title="ERROR",
                    message="Invalid input"
                )
                 '''
            root.destroy()

        def onclick(event=None,Train=False):
            global TrainConfig
            TrainConfig=Train
            returnInput()


        def appendupdateSticky_subject(addition=[]):
            #append
            for i in range(0,columns-3):
                if var_subject_activateRdio[i].get() != "" and var_subject_activateRdio[i].get() not in inputList["subjectList"]:
                    inputList["subjectList"].append(var_subject_activateRdio[i].get())
                var_subject_activateRdio[i].set("")
            #update
            activateList = RNNinterface(inputList["subjectList"]+addition+[i.get() for i in var_subject_activateRdio if i.get() != ""],[], json2network(), Mode='Activate')
            pre_activateList =[]
            try:
                if len([i for i in activateList if i[1] != 0.5]) == 0:
                    pre_activateList = [[i["subjectList"][0],0.5] for i in previnputList if i["subjectList"]!=[]][::-1]+pre_activateList+activateList
                else:
                    pre_activateList=pre_activateList+activateList
            except:
                pre_activateList=pre_activateList+activateList

            activateList=[]
            for toappend in pre_activateList:
                if toappend not in activateList:
                    activateList.append(toappend)
            for i in range(0,columns-3):
                var_subject_activateRdio[i].set('')

            for i in range(0,columns-3):
                if i<len(activateList):

                    if len(activateList[i][0]) >20:
                        disp = activateList[i][0][:5]+"..."
                    else:
                        disp = activateList[i][0]
                    subject_activateRdio[i].config(text =disp, relief=FLAT,onvalue=activateList[i][0],offvalue="",background = val_to_hex(activateList[i][1]),
                                                   command=lambda i=i,var_subject_activateRdio=var_subject_activateRdio,val=activateList[i][0]:whenPressed(val,activateList,btn=var_subject_activateRdio[i],mode='subject') if True else False)


                    if activateList[i][0] in sub_rdiotoadd:
                        var_subject_activateRdio[i].set(activateList[i][0])
        def appendupdateSticky_reaction(addition=[]):
            print("NOTIFY")
            #append
            for i in range(0,columns-3):
                if var_reaction_activateRdio[i].get() != "" and var_reaction_activateRdio[i].get() not in inputList["reactionList"]:
                    toappend = [var_reaction_activateRdio[i].get()]
                    toappend=macro_expand(toappend)
                    for mtoappend in toappend:
                        inputList["reactionList"].append(mtoappend)
                #var_reaction_activateRdio[i].set("")
            #update
            activateList = RNNinterface(list(set(inputList["reactionList"]+inputList["subjectList"]
                                                 +[i.get() for i in var_subject_activateRdio if i.get() != '']+[i.get() for i in var_reaction_activateRdio if i.get() != '']
                                                 +addition)),[], json2network(), Mode='Activate')
            #add basic neurons to reaction
            #add rank
            autogened = autoGenList([i.get() for i in var_subject_activateRdio if i.get() != ""]).getminputLists()
            ranked_autogened = []
            for mautogened in autogened:
                ranked_autogened.append(mautogened)
            pre_activateList =  [["@Date&Time"]]+ranked_autogened

            try:
                if len([i for i in activateList if i[1] != 0.5]) == 0:
                    pre_activateList = pre_activateList+[[i["subjectList"][0],0.5] for i in previnputList if i["subjectList"]!=[]][::-1]+activateList
                else:
                    pre_activateList=pre_activateList+activateList
            except:
                pre_activateList=pre_activateList+activateList

            activateList=[]
            for toappend in pre_activateList:
                if toappend[0] not in [i[0] for i in activateList]:
                    activateList.append(toappend)
            for i in range(0,columns-3):
                var_reaction_activateRdio[i].set('')
            for i in range(0,columns-3):
                if i<len(activateList):
                    color = val_to_hex(0)
                    if len(activateList[i])>1:
                        color = val_to_hex(activateList[i][1])
                    else:
                        color = val_to_hex(0)
                    #trim if too long
                    if len(activateList[i][0]) >20:
                        disp = activateList[i][0][:5]+"..."
                    else:
                        disp = activateList[i][0]
                    reaction_activateRdio[i].config(text =disp, relief=FLAT,onvalue=activateList[i][0],offvalue="",background =color,
                                                    command=lambda i=i,activateList=activateList,var_reaction_activateRdio=var_reaction_activateRdio,val=activateList[i][0]:whenPressed(val,activateList,btn=var_reaction_activateRdio[i],mode='reaction') if True else False)

                    if activateList[i][0] in rec_rdiotoadd:
                        var_reaction_activateRdio[i].set(activateList[i][0])

        def whenPressed(mhash,activateList,btn='',mode=''):
            #updaterdio
            if mode == 'reaction':
                nonlocal rec_rdiotoadd
                for index, var in enumerate(var_reaction_activateRdio):
                    if index < len(activateList):
                        if var.get() != "":
                            rec_rdiotoadd.append(var.get())
                        else:
                            rec_rdiotoadd=[i for i in rec_rdiotoadd if i != activateList[index][0]]
                rec_rdiotoadd = list(set(rec_rdiotoadd))
                appendupdateSticky_reaction(addition=rec_rdiotoadd)
            if mode=='subject':
                nonlocal sub_rdiotoadd
                for index, var in enumerate(var_subject_activateRdio):
                    if index < len(activateList):
                        if var.get() != "":
                            sub_rdiotoadd.append(var.get())
                        else:
                            sub_rdiotoadd=[i for i in sub_rdiotoadd if i != activateList[index][0]]
                sub_rdiotoadd = list(set(sub_rdiotoadd))
                appendupdateSticky_subject(addition=sub_rdiotoadd)
                appendupdateSticky_reaction(addition=rec_rdiotoadd)

            if btn.get() != '':
                #display text
                textViewer.delete(1.0,END)
                textViewer.insert(1.0, mhash)
                #for openapp
                for filename_woext in [os.path.splitext(os.path.basename(i))[0] for i in listdir(pdfDATA_PATH)]:
                    if filename_woext == mhash:
                        os.system('start '+os.path.join(pdfDATA_PATH,mhash+".pdf"))

        def backspace(mode=""):
            if(mode == "Subject"):
                inputList["subjectList"].pop()
            elif (mode == "Reaction"):
                inputList["reactionList"].pop()
            appendInput()

        def input_Textbox(to=""):
            text = str(textViewer.get("1.0",END)).strip('\n')
            if to=='subject':
                inputList['subjectList'].append(text)
            elif to == 'reaction':
                inputList['reactionList'].append(text)
            appendInput()
            appendInput()


        #frame
        rootF1 = Frame(root,  width = 20, height = 500)
        rootF2 = Frame(root,  width = 20, height = 500)

        f1 = Frame(rootF1,  width = 180, height = 500)
        f2 = Frame(rootF1,  width = 180, height = 500)
        f3 = Frame(rootF1,  width = 180, height = 500)
        f4 = Frame(rootF1,  width = 180, height = 500)
        f5 = Frame(rootF1,  width = 180, height = 500)
        backspace_sub = tkinter.Button(f1, text ="←", command =lambda: backspace(mode = "Subject"))
        backspace_rec = tkinter.Button(f3, text ="←", command =lambda: backspace(mode = "Reaction"))

        updateinputListHistory()
        previousStat = tkinter.Button(f3, text ="H", command =lambda :setprev_inputListHistory())


        def updatePrediction(mode=""):
            #comboSubject.set_completion_list(test_list+inputList["subjectList"])
            #searchterm = repr(comboSubject.get().decode("UTF8").encode("GBK")).replace("\\x","%")
            if mode == "subjectList":
                tosend="http://suggestqueries.google.com/complete/search?client=firefox&q="+urllib.parse.quote(comboSubject.get())
            elif mode == "reactionList":
                tosend="http://suggestqueries.google.com/complete/search?client=firefox&q="+urllib.parse.quote(comboReaction.get())
            try:
                #prevList = []
                content = urllib.request.urlopen(tosend).read()
                #print(content)
                getStr = content.decode("utf-8")
                newlist = ast.literal_eval(getStr)[1]
                finalliat = [i for i in list(set(newlist+listofNeurons())) ]
                finalliat = sorted(finalliat)
                if mode == "subjectList":
                    #wikipedia.search(urllib.parse.quote(comboSubject.get())
                    comboSubject.set_completion_list(finalliat)
                elif mode == "reactionList":
                    comboReaction.set_completion_list(finalliat)
            except:
                print("http error")

        def edittools(mode=''):
            if mode=='spaceX':
                str = copy.deepcopy(textViewer.get(1.0,END).strip('\n').replace(' ',''))
                textViewer.delete(1.0,END)
                textViewer.insert(1.0,str)
        #combobox,file
        comboSubject = AutocompleteCombobox(f2)
        #comboSubject = ComboBox(autocomplete=True)
        var_comboSub = StringVar()
        var_comboSub.trace('w',lambda name, index, mode: updatePrediction(mode="subjectList"))
        comboSubject.config(textvariable=var_comboSub)
        comboSubject.set_completion_list(test_list)
        filesub = tkinter.Button(f2, text ="file", command =lambda: choosefile_oncick(mode = "Subject"))

        comboReaction = AutocompleteCombobox(f4)
        var_comboRec = StringVar()
        var_comboRec.trace('w',lambda name, index, mode: updatePrediction(mode="reactionList"))
        comboReaction.config(textvariable=var_comboRec)
        comboReaction.set_completion_list(test_list)
        filerec = tkinter.Button(f4, text ="file", command =lambda:  choosefile_oncick(mode = "Reaction"))

        #append textbox but
        append_subbut = tkinter.Button(f2, text ="→", command =lambda :input_Textbox(to='subject'))
        append_recbut = tkinter.Button(f4, text ="→", command =lambda :input_Textbox(to='reaction'))

        #append button
        appendButn = tkinter.Button(f5, text ="append", command =lambda :appendInput())

        #OK button
        OKbut = tkinter.Button(f5, text ="OK", command =lambda :onclick(Train=False))

        #OK&Train
        OKTrainbut = tkinter.Button(f5, text ="OK&Train", command =lambda :onclick(Train=True))

        #view TextBox
        textViewer = tkinter.Text(rootF2, height=12, width=25)
        #spaceXfuncbtn
        spaceXfuncbtn =tkinter.Button(rootF2, text ="spaceX", command =lambda :edittools(mode='spaceX'))


        #Subject TextBox
        subjectT = tkinter.Text(f1, height=2, width=150)
        subjectT.bind("<Return>",lambda event=None:appendInput(mode="replaewithTextbox"))
        subjectT.bind("<Double-Button-1>",lambda event=None:appendInput(target="subjectList"))

        #Reaction TextBox
        reactionT = tkinter.Text(f3, height=2, width=150)
        reactionT.bind("<Return>",lambda event=None:appendInput(mode="replaewithTextbox"))
        reactionT.bind("<Double-Button-1>",lambda event=None:appendInput(target="reactionList"))

        #Activate RadioBut
        subject_activateRdio = [0 for x in range(columns-1)]
        reaction_activateRdio = [0 for x in range(columns-1)]

        #clear button
        var_subject_clearRdio = BooleanVar()
        #var_subject_clearRdio.trace('w',lambda name, index, mode: clear_inputList(var_subject_clearRdio.get()))
        subject_clearRdio = Checkbutton(f1, text="X", variable=var_subject_clearRdio,onvalue=True,offvalue=False,activeforeground = val_to_hex(0.5), indicatoron=0)
        def printy():
            print("NOTI")
        for i in range(0,columns-3):
            radios=Checkbutton(f2, text="--------", variable=var_subject_activateRdio[i],onvalue="",background = val_to_hex(0),offvalue="", indicatoron=0)
            #radios.bind('Button-1',lambda :printy())
            subject_activateRdio[i]=(radios)
        for i in range(0,columns-3):
            radior=Checkbutton(f4, text="--------", variable=var_reaction_activateRdio[i],onvalue="",background = val_to_hex(0),offvalue="", indicatoron=0)
            #radior.bind('Button-1',lambda :appendupdateSticky_reaction(rec_rdiotoadd))
            reaction_activateRdio[i]=(radior)

        S1 = Scrollbar(f1,command=subjectT.yview)
        subjectT.config(yscrollcommand=S1.set)
        S2 = Scrollbar(f3,command=subjectT.yview)
        reactionT.config(yscrollcommand=S2.set)

        SV = Scrollbar(rootF2,command=textViewer.yview)

        rootF1.grid(row=0,column=1)
        rootF2.grid(row=0,column=0)

        f2.grid(row=1,column=0,columnspan=1,sticky=W+N+S)
        comboSubject.grid(row=0,column=2)
        filesub.grid(row=0,column=1)
        for i in range(0,columns-3):
            subject_activateRdio[i].grid(row=0,column=i+3)
        append_subbut.grid(row=0,column=0)

        f4.grid(row=3,column=0,columnspan=1,sticky=W+N+S)
        comboReaction.grid(row=0,column=2)
        filerec.grid(row=0,column=1)
        for i in range(0,columns-3):
            reaction_activateRdio[i].grid(row=0,column=i+3)
        append_recbut.grid(row=0,column=0,sticky=E+N+S)

        f1.grid(row=0,column=0,sticky=W+N+S)
        S1.grid(row=0,column=2,sticky=W+N+S)
        backspace_sub.grid(row=0,column=1,sticky=W+N+S)
        subject_clearRdio.grid(row=0,column=3,sticky=W+N+S)
        subjectT.grid(row=0,column=0 ,sticky=W+N+S)

        f3.grid(row=2,column=0,sticky=W+N+S)
        S2.grid(row=0,column=2,sticky=W+N+S)
        backspace_rec.grid(row=0,column=1,sticky=W+N+S)
        reactionT.grid(row=0,column=0,sticky=W+N+S )
        previousStat.grid(row=0,column=3,sticky=E+N+S)

        f5.grid(row=4,column=0,sticky=W+N+S)

        textViewer.grid(row=0,column=0)
        SV.grid(row=0,column=1,sticky=N+S)
        spaceXfuncbtn.grid(row=1,column=0)

        appendInput()

        appendButn.grid(row=0,column=0,padx=480)
        OKbut.grid(row=0,column=1,padx=10)
        OKTrainbut.grid(row=0,column=2)

        comboSubject.focus_force()
        # I used a tiling WM with no controls, added a shortcut to quit
        comboSubject.bind("<F1>",lambda event=None:comboReaction.focus_force())
        comboReaction.bind("<F1>",lambda event=None:onclick(Train=False))
        root.bind('<Return>', lambda event=None:appendInput())
        root.mainloop()
        pickle.dump(previnputList, open('searchHistory', 'wb'))
        return [inputList,TrainConfig]

def macro_expand(toappendList):
    if "@Date&Time" in [i for i in toappendList ]:
            toappendList.insert(0,datetime.datetime.now().strftime("%a"))
            toappendList.insert(0,datetime.datetime.now().strftime("%A"))
            #toappendList.insert(0,datetime.datetime.now().strftime("%b"))
            #toappendList.insert(0,datetime.datetime.now().strftime("%B"))
            #toappendList.insert(0,datetime.datetime.now().strftime("%F"))
            toappendList.insert(0,datetime.datetime.now().strftime("%h"))
            toappendList.insert(0,datetime.datetime.now().strftime("%R"))
            toappendList.insert(0,datetime.datetime.now().strftime("%Y/%m/%d"))
            #toappendList.insert(0,datetime.datetime.now().strftime("%T"))
            toappendList.insert(0,datetime.datetime.now().strftime("%x"))
            toappendList.insert(0,datetime.datetime.now().strftime("%X"))

    if "@name" in [i for i in toappendList ]:
        toappendList.insert(0,"蘇柏穎")
        toappendList.insert(0,"Nick")
        toappendList.insert(0,"nickisverygood")
    if "@add" in [i for i in toappendList ]:
        toappendList.insert(0,"臺北市松山區八德路二段399號10樓之11")
    #print([i for i in toappendList if i not in  ["@Date&Time","@name" ,"@add"]])
    toappendList = [i for i in toappendList if i not in  ["@Date&Time","@name" ,"@add"]]
    return toappendList
