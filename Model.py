from argparse import FileType
from pandas import read_csv, read_excel, HDFStore, read_hdf, ExcelFile, Series, DataFrame
import os
import configparser
import numpy as np
class Model:
    def __init__(self):
            self.loadedFiles = {}
            self.dataSets = {}
            self.config = self.defaultConfig()
            self.autoSaveInterval = 5
            self.maxAutoSaves = 5
            
    def defaultConfig(self):
        config = {}
        config["Mass"] = {}
        mass = config["Mass"]
        mass["g"] = 1
        mass["mg"] = 1/1000.0
        mass["ug"] = 1/1000000.0
        mass["ng"] = 1/1000000000.0
        mass["kg"] = 1000
        
        config["Volume"] = {}
        volume = config["Volume"]
        volume["L"] = 1
        volume["mL"] = 1/1000.0
        
        config["Concentration"] = {}
        concentration = config["Concentration"]
        concentration["M"] = 1
        concentration["mM"] = 1/1000.0

        config["Parts"] = {}
        parts = config["Parts"]
        parts["ppm"] = 1
        parts["ppb"] = 1/1000.0
        
        
        
        return config

def loadExcelSheet(path, sheetName):
    file_name = os.path.basename(path)
    file = {"file": None, "fileType": "Excel", "fileName": f'{file_name}({sheetName})'}
    file["file"] = read_excel(path, sheetName)
    return file

def loadFile(path):
    """
    The loadFile function loads a file from the specified path and returns it as a pandas dataframe.
    
    :param path: Used to pass the file path to the function.
    :return: a Pandas DataFrame object.
    :doc-author: Trelent
    """
    file_name = os.path.basename(path)
    file_extension = os.path.splitext(file_name)[1][1:]
    print(f'File_Extension = {file_extension}')
    file = {"file": None, "fileType": None, "fileName": file_name}
    if file_extension == "csv":
        file["file"] = read_csv(path)
        file["fileType"] = "csv"
    elif file_extension.find("xls") >= 0:
        file["file"] = read_excel(path, None)
        file["fileType"] = "Excel"
    else:
        raise TypeError()
    return file

def saveDFs(path, dataFrames, chemicalData, config):
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
        newHDF.put(key, dataFrames[key]["file"])
        newHDF.get_storer(key).attrs.fileType=dataFrames[key]["fileType"]
        newHDF.get_storer(key).attrs.fileName=dataFrames[key]["fileName"]
        newHDF.get_storer(key).attrs.isData=True
    keys = chemicalData.keys()
    for key in keys:
        newHDF.put(key, DataFrame(chemicalData[key]))
        newHDF.get_storer(key).attrs.isData=False
    
    #keys = config.keys()
    #items = [config[key] for key in keys]
    #newHDF.put("config", Series(data=items, index=keys, dtype="string"))
    newHDF.flush()
    newHDF.close()

def HDFtoDict(path):
    """
    The HDFtoDict function reads in an HDF file and returns a dictionary of the data contained within.
       The function takes one argument, path, which is the location of the HDF file to be read.
    
    :param path: Used to specify the path to the HDF file.
    :return: a dictionary with the keys being the group names and the values being a list of all.
    
    :doc-author: Trelent
    """
    keyFile = HDFStore(path=path)
    keys = keyFile.keys()
    DataDict = {}
    chemicalDict = {}
    #config = {}
    #if "config" in keys:
        #del keys["config"]
        #localConfig = keyFile["config"]
        #for key in localConfig.keys():
            #config[key] = localConfig[key]
    for key in keys:
        sheet = key[1:]
        if keyFile.get_storer(sheet).attrs.isData:
            DataDict[sheet] = {}
            DataDict[sheet]["file"] = keyFile[sheet]
            DataDict[sheet]["fileType"] = keyFile.get_storer(sheet).attrs.fileType
            DataDict[sheet]["fileName"] = keyFile.get_storer(sheet).attrs.fileName
        else:
            chemicalDict[sheet] = keyFile[sheet].to_dict()
            print(chemicalDict[sheet])
    keyFile.close()
    return [DataDict, chemicalDict]


def readConfig():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config._sections
        