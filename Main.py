import ftplib
import itertools
import json
import multiprocessing
import os
import shutil
import threading
import time

from NeuralNetwork.RNN import printNetwork, RNNinterface
from NeuralNetwork.drawGraph import drawGraphClass
from constructNetwork.addNeuron import addNeuron
from constructNetwork.json_network import json2network
from filestorage.utils import retMD5
from inputMain import inputMain

train_and_sync_mode='local'
Paths = {'jsonNetworkDump': 'NetworkDump.json',
         'pklNetworkDumo': 'NetworkDump.pkl',
         'pklTrainDataDump': 'TrainDataDump.pkl'}
server = 'ssmsynology.synology.me'
username = 'nickisverygood'
password = 'sbi8844848'
remote_path = "/homes/nickisverygood/DynamicMindMap/"

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


def getFileListFTP(ftp_connection):
    try:
        files = ftp_connection.nlst()
        return files
    except ftplib.error_perm as resp:
        if str(resp) == "550 No files found":
            print ("No files in this directory")
        else:
            raise
        return None



def train_and_sync(mode='local'):
    if mode=='local':
        f_NetworkDump_name = 'NetworkDump_'+retMD5.md5("NetworkDump.json")
        f_TrainDataDump_name = 'TrainDataDump_'+retMD5.md5("TrainDataDump.pkl")
        #update current
        latest_file_list = {'NetworkDump':'','TrainDataDump':'','mnetwork':''}
        latest_file_list['NetworkDump'] = f_NetworkDump_name
        latest_file_list['TrainDataDump'] = f_TrainDataDump_name
        latest_file_list['mnetwork'] = os.path.splitext(retMD5.md5('NetworkDump.json'))[0]+'_'+ os.path.splitext(retMD5.md5('TrainDataDump.pkl'))[0]+".pkl"
        latest_file_list_file = open('latest_file_list', 'wb')
        json.dump(latest_file_list,open("latest_file_json",'w'),indent=4)

        #ftp
        try:
            ftp_connection = ftplib.FTP(server, username, password)
            ftp_connection.cwd(remote_path)
            files = getFileListFTP(ftp_connection)
            ftp_connection.storbinary('STOR latest_file_json', open('latest_file_json', 'rb'))
            ftp_connection.storbinary('STOR '+f_NetworkDump_name,  open("NetworkDump.json", 'rb'))
            ftp_connection.storbinary('STOR '+f_TrainDataDump_name,  open("TrainDataDump.pkl",'rb'))
        except:
            print('FTP error!!')
        #local
        shutil.copy2("latest_file_json",'_History/'+"latest_file_json")
        shutil.copy2("NetworkDump.json",'_History/'+f_NetworkDump_name)
        shutil.copy2("TrainDataDump.pkl",'_History/'+f_TrainDataDump_name)

        #replace if upate exists - ftp
        if latest_file_list['mnetwork'] in files:
            fh = open("NetworkDump.pkl", 'rb')
            ftp_connection.retrbinary('RETR %s' % latest_file_list['mnetwork'], fh.write)
        #replace if update exists - local
            shutil.copy2('_History/'+latest_file_list['mnetwork'],"NetworkDump.pkl")

    elif mode=='server':
        #FTP stuff
        ftp_connection = ftplib.FTP(server, username, password)
        ftp_connection.cwd(remote_path)
        files = getFileListFTP(ftp_connection)

        ftp_connection.retrbinary('RETR %s' % 'latest_file_json', open('latest_file_json', 'wb').write)
        try:
            latest_file_list = json.load(open("latest_file_json",'r'))
            print(latest_file_list['mnetwork'])
            if latest_file_list['mnetwork'] not in files:
                RNNinterface([],[], json2network(), Mode='Train',
                             PLKnetwork_PATH='NetworkDump.pkl', train=True,maxEpochs=None)
                ftp_connection.storbinary('STOR '+str(latest_file_list['mnetwork']),open(Paths.get('pklNetworkDumo'),'rb'))
        except Exception as ex:
            print(ex)
    elif mode == 'localserver':
        try:
            latest_file_list = json.load(open("latest_file_json",'r'))
            print(latest_file_list['mnetwork'])

            if latest_file_list['mnetwork'] not in os.listdir('_History/'):
                RNNinterface([],[], json2network(), Mode='Train',
                             PLKnetwork_PATH='NetworkDump.pkl', train=True,maxEpochs=None)
                shutil.copy2("NetworkDump.pkl",'_History/'+latest_file_list['mnetwork'])
        except Exception as ex:
            print(ex)


#upload
class trainandsync_local(threading.Thread):
    def run(self):
        train_and_sync("local")
def trainandsync_servers(mode):
    train_and_sync(mode=mode)

if __name__ == "__main__":
    while train_and_sync_mode in ['localserver' , 'server']:
            time.sleep(1)
            try:
                p = multiprocessing.Process(target=trainandsync_servers, args=(train_and_sync_mode,))
                p.start()
                try:
                    curr = json.load(open("latest_file_json",'r'))['mnetwork']
                except:
                    print('latest_file_json ERROR')
                    continue

                while p.is_alive():
                    time.sleep(1)
                    print('testing...')

                    filelist =  os.listdir('_History/')
                    try:
                        latest_file_list = json.load(open('latest_file_json','r'))
                        print(curr)
                        print(latest_file_list['mnetwork'])
                        if curr!=latest_file_list['mnetwork']:
                            print("THERE IS NEW")
                            p.terminate()
                    except:
                        continue
            except Exception as ex:
                print(ex)
                continue

    while train_and_sync_mode == 'local':
        print('local')
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

        mtrainandsync_local = trainandsync_local()
        mtrainandsync_local.start()


