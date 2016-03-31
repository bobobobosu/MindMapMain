#from Main import Paths
import ftplib
import json

import Main
from filestorage.utils import retMD5


def train_and_sync(mode='local'):
    server = 'ssmsynology.synology.me'
    username = 'nickisverygood'
    password = 'sbi8844848'
    ftp_connection = ftplib.FTP(server, username, password)
    remote_path = "/homes/nickisverygood/DynamicMindMap/"
    ftp_connection.cwd(remote_path)
    try:
      files = ftp_connection.nlst()
    except ftplib.error_perm as resp:
        if str(resp) == "550 No files found":
            print ("No files in this directory")
        else:
            raise


    f_NetworkDump_name = 'NetworkDump_'+retMD5.md5("NetworkDump.json")

    f_TrainDataDump_name = 'TrainDataDump_'+retMD5.md5("TrainDataDump.pkl")



    if mode=='local':
        #update current
        latest_file_list = {'NetworkDump':'','TrainDataDump':'','mnetwork':''}
        latest_file_list['NetworkDump'] = f_NetworkDump_name
        latest_file_list['TrainDataDump'] = f_TrainDataDump_name
        latest_file_list['mnetwork'] = retMD5.md5('NetworkDump.json')+'_'+ retMD5.md5('TrainDataDump.pkl')
        latest_file_list_file = open('latest_file_list', 'wb')
        json.dump(latest_file_list,open("latest_file_json",'w'),indent=4)


        ftp_connection.storbinary('STOR latest_file_json', open('latest_file_json', 'rb'))
        ftp_connection.storbinary('STOR '+f_NetworkDump_name,  open("NetworkDump.json", 'rb'))
        ftp_connection.storbinary('STOR '+f_TrainDataDump_name,  open("TrainDataDump.pkl",'rb'))

        #replace if upate exists
        if latest_file_list['mnetwork'] in files:
            fh = open("NetworkDump.pkl", 'rb')
            ftp_connection.retrbinary('RETR %s' % latest_file_list['mnetwork'], fh.write)
    elif mode=='server':
        ftp_connection.retrbinary('RETR %s' % 'latest_file_json', open('latest_file_json', 'wb').write)
        try:
            latest_file_list = json.load(open("latest_file_json",'r'))
        except:
            print('error')
        if latest_file_list['mnetwork'] not in files:
            #RNNinterface([],[], json2network(), Mode='Train',
            #             PLKnetwork_PATH='NetworkDump.pkl', train=True)
            ftp_connection.storbinary('STOR '+latest_file_list['mnetwork'],Main.Paths.get('pklNetworkDumo'))
