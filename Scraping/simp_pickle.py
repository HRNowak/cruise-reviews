import pickle

def save_pickle(element,file,loc = ''):
    #saves pickles with a single line of code.
    with open(loc+file, 'wb') as handle:
        pickle.dump(element, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_pickle(file,loc = ''):
    #loads pickles with a single line of code
    with open(loc+file, 'rb') as handle:
        return pickle.load(handle)