
import Model
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
        self.model = Model.Model()
        self.autoSave()

    @property
    def dataSets(self):
        self.model.dataSets

    def __enter__(self):
        return self.model.loadedFiles

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __iter__(self):
        keys = self.model.loadedFiles.keys()
        for key in keys:
            yield self.model.loadedFiles[key]
    
    def __getitem__(self, key):
        return self.model.loadedFiles[key]
    
    def doAutoSave(self):
        if not os.path.exists(AUTOSAVE_PATH):
            print("Path does not exist")
            os.mkdir(AUTOSAVE_PATH)
        now = datetime.now()
        self.autoSaveFileLimit()
        if not os.path.exists(AUTOSAVE_PATH + AUTOSAVE_FILE_NAME + now.strftime("%m/%d/%Y, %H:%M:%S")):
            self.save(AUTOSAVE_PATH + AUTOSAVE_FILE_NAME + now.strftime("_%Y-%m-%d-(%H-%M-%S)"))
        self.autoSave()

    def autoSaveFileLimit(self):
        numFiles = len([name for name in os.listdir(AUTOSAVE_PATH) if os.path.isfile(os.path.join(AUTOSAVE_PATH, name))])
        if numFiles >= self.model.maxAutoSaves:
            oldestFile = min([os.path.join(AUTOSAVE_PATH) + file for file in os.listdir(AUTOSAVE_PATH)], key=os.path.getctime)
            os.remove(os.path.join(AUTOSAVE_PATH,oldestFile))
    
    def autoSave(self):
        t = Timer(self.model.autoSaveInterval, self.doAutoSave)
        t.daemon = True
        t.start()
        
    def loadAutosave(self):
        pass
            
    
    def addDataSet(self, dataSet, Unit, Standard):
        if dataSet in self.model.dataSets or dataSet in self.model.loadedFiles:
            print("A dataset species with this name already exists")
            return 0
        else:
            self.model.dataSets[dataSet] = {}
            self.model.dataSets[dataSet]["unit"] = Unit
            self.model.dataSets[dataSet]["standard"] = Standard
            self.model.dataSets[dataSet]["data"] = []
            return 1
    
    def importDataSet(self, dataName, fileName, data):
        if dataName not in self.model.dataSets:
            print("This dataGroup does not exist")
            return 0
        else:
            dataGroup = self.model.dataSets[dataName]["data"]
            if fileName not in dataGroup["data"]:
                dataGroup[fileName] = []
            dataGroup[fileName].append(data)
            return 1
    
    def loadFile(self, filePath, fileName):
        if fileName in self.model.loadedFiles or fileName in self.model.dataSets:
            print("A file with this name already exists, please choose another name")
            return 0
        try:
            newFile = Model.loadFile(filePath)
            self.model.loadedFiles[fileName] = newFile
            print(f'Successfully loaded file')
            return 1
        except IOError:
            print(f'Error loading file, IOError occured')
            return 0
        except TypeError:
            print(f'The type of file specified is not supported')
            return 0
        
    def loadExcelSheet(self, filePath, sheetName, fileName):
        if fileName in self.model.loadedFiles or fileName in self.model.dataSets:
            print("A file with this name already exists, please choose another name")
            return 0
        try:
            newFile = Model.loadExcelSheet(filePath, sheetName)
            self.model.loadedFiles[fileName] = newFile
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
        self.model.loadedFiles = {}
        self.model.dataSets = {}
    
    def getDataSets(self):
        return self.model.dataSets
    
    def getLoadedFiles(self):
        return self.model.loadedFiles
    
    def save(self, filePath):
        filePath = checkForExt(filePath, "hdf")
        print(f'Attempting save at {filePath}')
        try:
            Model.saveDFs(filePath, self.model.loadedFiles, self.model.dataSets, self.model.config)
            return 1
        except IOError:
            return 0
        

    def loadProject(self, filePath):
        print(f'Trying to get HDF file at path {filePath}')
        try:
            newDataFrames = Model.HDFtoDict(filePath)
            self.model.loadedFiles = newDataFrames[0]
            self.model.dataSets = newDataFrames[1]
            self.model.config = newDataFrames[2]
            return 1
        except AttributeError:
            return 0
    
    def getLoadedFile(self, fileName):
        if fileName in self.model.loadedFiles:
            return self.model.loadedFiles[fileName]
        return None
    
    def getConfigUnits(self):
        return self.model.config.keys()
    
    def getConfigSubUnits(self, unit):
        if unit in self.model.config:
            return self.model.config[unit]
        else:
            return None
    
    def deleteFile(self, fileName):
        if fileName in self.model.loadedFiles:
            del self.model.loadedFiles[fileName]
            return 1
        else:
            return 0
        
    def importData(self, dataSet, dataAxis, timeAxis, dataUnit):
        if dataSet not in self.model.dataSets or len(dataAxis) != len(timeAxis) or dataUnit not in self.model.config[self.model.dataSets[dataSet]["unit"]]:
            for i in range(len(dataAxis)):
                self.model.dataSets[dataSet]["data"].append({"measurement": dataAxis[i], "date": timeAxis[i], "unit": dataUnit})
            return 1
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