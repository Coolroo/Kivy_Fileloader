
import fileLoading
import os
from pandas import DataFrame

dir_path = os.path.dirname(os.path.realpath(__file__)) + '\\'

def checkForExt(filePath, ext):
    if os.path.splitext(os.path.basename(filePath))[1][1:] != ext:
        return filePath + f'.{ext}'
    else:
        return filePath

class Controller:
    
    def __init__(self):
        self.loadedFiles = {}
        self.chemicalData = {}
        self.config = self.defaultConfig()
        print(dir_path)
        print(self.__dict__)
        
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
    
    def addChemicalData(self, chemicalName, xAxis, yAxis):
        if chemicalName in self.chemicalData or chemicalName in self.loadedFiles:
            print("A chemical species with this name already exists")
            return 0
        else:
            self.chemicalData[chemicalName] = {}
            self.chemicalData[chemicalName]["xAxis"] = xAxis
            self.chemicalData[chemicalName]["yAxis"] = yAxis
            self.chemicalData[chemicalName]["data"] = DataFrame({xAxis: [], yAxis: []})
            return 1
    
    
    def loadFile(self, filePath, fileName):
        if fileName in self.loadedFiles or fileName in self.chemicalData:
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
        if fileName in self.loadedFiles or fileName in self.chemicalData:
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
        self.chemicalData = {}
    
    def getChemicalData(self):
        return self.chemicalData
    
    def getLoadedFiles(self):
        return self.loadedFiles
    
    def save(self, filePath):
        filePath = checkForExt(filePath, "hdf")
        print(f'Attempting save at {filePath}')
        try:
            fileLoading.saveDFs(filePath, self.loadedFiles, self.chemicalData, self.config)
            return 1
        except IOError:
            return 0
        

    def loadProject(self, filePath):
        print(f'Trying to get HDF file at path {filePath}')
        try:
            newDataFrames = fileLoading.HDFtoDict(filePath)
            self.loadedFiles = newDataFrames[0]
            self.chemicalData = newDataFrames[1]
            self.config = newDataFrames[2]
            return 1
        except AttributeError:
            return 0
    
    def getLoadedFile(self, fileName):
        return self.loadedFiles[fileName]
    
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
    
    
def getFileType(filePath):
    file_name = os.path.basename(filePath)
    file_extension = os.path.splitext(file_name)[1][1:]
    if file_extension == "csv":
        return "csv"
    elif file_extension.find("xls") >= 0:
        return "Excel"
    else:
        return "unsupported"