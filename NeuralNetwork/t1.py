import pickle

from pybrain import RecurrentNetwork

mnetwork = [RecurrentNetwork()]
pickle.dump(mnetwork[0], open('test', 'wb'))
