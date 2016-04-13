import pickle

trainDataRaw = pickle.load(open('TrainDataDump.pkl', 'rb'))
for trainDataRaws in trainDataRaw:
    print(trainDataRaws)