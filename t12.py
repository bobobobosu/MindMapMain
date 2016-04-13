import pickle

from utils.tkGUI import RAW2PRO_dict_path

RAW2PRO_dict = pickle.load(open(RAW2PRO_dict_path, 'rb'))
print(RAW2PRO_dict)