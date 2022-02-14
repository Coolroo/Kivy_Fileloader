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
    HDFFile = read_hdf(path)
    DataDict = {}
    for key in HDFFile.keys():
        DataDict[key] = HDFFile[key]
    return DataDict