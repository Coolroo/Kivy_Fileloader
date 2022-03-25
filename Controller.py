
import fileLoading
import os
from pandas import DataFrame
from threading import Timer
from datetime import datetime


AUTOSAVE_PATH = os.path.dirname(os.path.realpath(__file__)) + "/AutoSaves/"

AUTOSAVE_FILE_NAME = "auto"

def checkForExt(filePath, ext):
    if os.path.splitext(os.path.basename(filePath))[1][1:] != ext:
        return filePath + f'.{ext}'
    else:
        return filePath

class Controller:
    
    def __init__(self):
        self.loadedFiles = {}
        self.dataSets = {}
        self.config = self.defaultConfig()
        self.autoSaveInterval = 300
        self.autoSave()
        
    def defaultConfig(self):
        config = {}
        config["Mass"] = {}
        mass = config["Mass"]
        mass["standard"] = "g"
        mass["g"] = 1
        mass["mg"] = 1/1000.0
        mass["ug"] = 1/1000000.0
        mass["ng"] = 1/1000000000.0
        mass["kg"] = 1000
        
        config["Volume"] = {}
        volume = config["Volume"]
        volume["standard"] = "L"
        volume["L"] = 1
        volume["mL"] = 1/1000.0
        
        config["Concentration"] = {}
        concentration = config["Concentration"]
        concentration["standard"] = "M"
        concentration["M"] = 1
        concentration["mM"] = 1/1000.0
        
        
        
        return config

    def __enter__(self):
        return self.loadedFiles

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __iter__(self):
        keys = self.loadedFiles.keys()
        for key in keys:
            yield self.loadedFiles[key]
    
    def __getitem__(self, key):
        return self.loadedFiles[key]
    
    def doAutoSave(self):
        if not os.path.exists(AUTOSAVE_PATH):
            print("Path does not exist")
            os.mkdir(AUTOSAVE_PATH)
        now = datetime.now()
        if not os.path.exists(AUTOSAVE_PATH + AUTOSAVE_FILE_NAME + now.strftime("%m/%d/%Y, %H:%M:%S")):
            self.save(AUTOSAVE_PATH + AUTOSAVE_FILE_NAME + now.strftime("_%Y-%m-%d-(%H-%M-%S)"))
        self.autoSave()
    
    def autoSave(self):
        t = Timer(self.autoSaveInterval, self.doAutoSave)
        t.daemon = True
        t.start()
        
    def loadAutosave(self):
        pass
            
    
    def addDataSet(self, dataSet, xAxis, yAxis, xStandard, yStandard):
        if dataSet in self.dataSets or dataSet in self.loadedFiles:
            print("A dataset species with this name already exists")
            return 0
        else:
            self.dataSets[dataSet] = {}
            self.dataSets[dataSet]["xAxis"] = xAxis
            self.dataSets[dataSet]["yAxis"] = yAxis
            self.dataSets[dataSet]["xStandard"] = xStandard
            self.dataSets[dataSet]["yStandard"] = yStandard
            self.dataSets[dataSet]["data"] = {}
            return 1
    
    def importDataSet(self, dataName, fileName, data):
        if dataName not in self.dataSets:
            print("This dataGroup does not exist")
            return 0
        else:
            dataGroup = self.dataSets[dataName]["data"]
            if fileName not in dataGroup["data"]:
                dataGroup[fileName] = []
            dataGroup[fileName].append(data)
            return 1
    
    def loadFile(self, filePath, fileName):
        if fileName in self.loadedFiles or fileName in self.dataSets:
            print("A file with this name already exists, please choose another name")
            return 0
        try:
            newFile = fileLoading.loadFile(filePath)
            self.loadedFiles[fileName] = newFile
            print(f'Successfully loaded file')
            return 1
        except IOError:
            print(f'Error loading file, IOError occured')
            return 0
        except TypeError:
            print(f'The type of file specified is not supported')
            return 0
        
    def loadExcelSheet(self, filePath, sheetName, fileName):
        if fileName in self.loadedFiles or fileName in self.dataSets:
            print("A file with this name already exists, please choose another name")
            return 0
        try:
            newFile = fileLoading.loadExcelSheet(filePath, sheetName)
            self.loadedFiles[fileName] = newFile
            return 1
        except:
            print("Loading Excel file Failed")
            return 0
    
    def clearProject(self):
        """
        The clearLoadedFiles function clears the loaded files list.
        
        :param self: Used to Refer to the object itself.
        
        :doc-author: Trelent
        """
        self.loadedFiles = {}
        self.dataSets = {}
    
    def getDataSets(self):
        return self.dataSets
    
    def getLoadedFiles(self):
        return self.loadedFiles
    
    def save(self, filePath):
        filePath = checkForExt(filePath, "hdf")
        print(f'Attempting save at {filePath}')
        try:
            fileLoading.saveDFs(filePath, self.loadedFiles, self.dataSets, self.config)
            return 1
        except IOError:
            return 0
        

    def loadProject(self, filePath):
        print(f'Trying to get HDF file at path {filePath}')
        try:
            newDataFrames = fileLoading.HDFtoDict(filePath)
            self.loadedFiles = newDataFrames[0]
            self.dataSets = newDataFrames[1]
            self.config = newDataFrames[2]
            return 1
        except AttributeError:
            return 0
    
    def getLoadedFile(self, fileName):
        if fileName in self.loadedFiles:
            return self.loadedFiles[fileName]
        return None
    
    def getConfigUnits(self):
        return self.config.keys()
    
    def getConfigSubUnits(self, unit):
        if unit in self.config:
            return self.config[unit]
        else:
            return None
    
    def deleteFile(self, fileName):
        if fileName in self.loadedFiles:
            del self.loadedFiles[fileName]
            return 1
        else:
            return 0
        
    def importData(self, dataSet, xAxis, yAxis):
        if dataSet in self.dataSets:
            thisData = self.dataSets[dataSet]
            thisData = 0
        else:
            return 0
    
    
def getFileType(filePath):
    file_name = os.path.basename(filePath)
    file_extension = os.path.splitext(file_name)[1][1:]
    if file_extension == "csv":
        return "csv"
    elif file_extension.find("xls") >= 0:
        return "Excel"
    else:
        return "unsupported"