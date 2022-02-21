from argparse import FileType
from pandas import read_csv, read_excel, HDFStore, read_hdf
import os

def loadFile(path):
    """
    The loadFile function loads a file from the specified path and returns it as a pandas dataframe.
    
    :param path: Used to pass the file path to the function.
    :return: a Pandas DataFrame object.
    :doc-author: Trelent
    """
    file_name = os.path.basename(path)
    file_extension = os.path.splitext(file_name)[1][1:]
    file = None
    if file_extension == "csv":
        file = read_csv(path)
    elif file_extension.find("xls") >= 0:
        file = read_excel(path)
    else:
        raise TypeError()
    return file

def saveDFs(path, dataFrames):
    """
    The saveDFs function saves a dictionary of dataframes to an HDF5 file.
    
    :param path: Used to specify the path to the file where we want to store our data.
    :param dataFrames: Used to store the dataframes in a dictionary.
    :return: a dictionary of the dataframes and their keys.
    :doc-author: Trelent
    """
    keys = dataFrames.keys()
    newHDF = HDFStore(path, mode='w')
    for key in keys:
        newHDF.put(key, dataFrames[key])
    newHDF.close()

def HDFtoDict(path):
    """
    The HDFtoDict function reads in an HDF file and returns a dictionary of the data contained within.
       The function takes one argument, path, which is the location of the HDF file to be read.
    
    :param path: Used to specify the path to the HDF file.
    :return: a dictionary with the keys being the group names and the values being a list of all.
    
    :doc-author: Trelent
    """
    with HDFStore(path) as keyFile:
        keys = keyFile.keys()
        DataDict = {}
        for key in keys:
            DataDict[key] = read_hdf(path, key=key)
        return DataDict