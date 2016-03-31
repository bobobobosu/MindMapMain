import multiprocessing
import time

from NeuralNetwork.RNN import RNNinterface
from constructNetwork.json_network import json2network


def func(msg):
    print (msg)
    RNNinterface([],[], json2network(), Mode='Train',
                             PLKnetwork_PATH='NetworkDump.pkl', train=True,maxEpochs=None)
if __name__ == "__main__":
    while True:
      p = multiprocessing.Process(target=func, args=("hello", ))
      p.start()
      c=0
      while p.is_alive():
          c=c+1
          print(p.is_alive())
          time.sleep(1)
          print("mmmmmmmm")
          #if c >9:
          #    p.terminate()
          #    break

      print ("Sub-process done.")