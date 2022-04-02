
import Model
import os
from pandas import DataFrame
from threading import Timer
from datetime import datetime
from collections import defaultdict
import itertools 

AUTOSAVE_PATH = os.path.dirname(os.path.realpath(__file__)) + "/AutoSaves/"

AUTOSAVE_FILE_NAME = "auto"

def checkForExt(filePath, ext):
    """
    The checkForExt function checks to see if the file path ends with the specified extension. If it does not, then a new file path is returned with an appended extension.
    
    :param filePath: Used to Get the file path of the file that is being checked.
    :param ext: Used to Check if the file has the correct extension.
    :return: The filepath if the extension is already correct, or it returns the filepath with an added.
    
    :doc-author: Trelent
    """
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
        """
        The doAutoSave function saves the current file to a specified location.
        It also keeps track of the number of files in the directory and deletes them if they exceed a limit.
        
        :param self: Used to Access variables that belongs to the class.
        
        :doc-author: Trelent
        """
        if not os.path.exists(AUTOSAVE_PATH):
            print("Path does not exist")
            os.mkdir(AUTOSAVE_PATH)
        now = datetime.now()
        self.autoSaveFileLimit()
        if not os.path.exists(AUTOSAVE_PATH + AUTOSAVE_FILE_NAME + now.strftime("%m/%d/%Y, %H:%M:%S")):
            self.save(AUTOSAVE_PATH + AUTOSAVE_FILE_NAME + now.strftime("_%Y-%m-%d-(%H-%M-%S)"))
        self.autoSave()

    def autoSaveFileLimit(self):
        """
        The autoSaveFileLimit function checks the number of files in the autosave folder and deletes
        the oldest file if there are more than a set amount. The maxAutoSaves variable is set to 10, but can be changed
        in the model class.
        
        :param self: Used to Access the class attributes.
        :return: The number of files in the autosave directory.
        
        :doc-author: Trelent
        """
        numFiles = len([name for name in os.listdir(AUTOSAVE_PATH) if os.path.isfile(os.path.join(AUTOSAVE_PATH, name))])
        if numFiles >= self.model.maxAutoSaves:
            oldestFile = min([os.path.join(AUTOSAVE_PATH) + file for file in os.listdir(AUTOSAVE_PATH) if AUTOSAVE_FILE_NAME in file], key=os.path.getctime)
            os.remove(os.path.join(AUTOSAVE_PATH,oldestFile))
    
    def autoSave(self):
        """
        The autoSave function is a timer that runs every self.model.autoSaveInterval seconds and saves the model to disk.
        
        :param self: Used to Access the class attributes.
        :return: A timer object.
        
        :doc-author: Trelent
        """
        t = Timer(self.model.autoSaveInterval, self.doAutoSave)
        t.daemon = True
        t.start()
            
    def addDataSet(self, dataSet):
        """
        The addDataSet function adds a new dataset to the model. 
        It takes one argument, which is the name of the data set. 
        If this name already exists in either loadedFiles or dataSets, it will print an error message and return 0. Otherwise, it will add that dataset to the dataSets dictionary.
        
        :param self: Used to Access variables that belongs to the class.
        :param dataSet: Used to Specify the name of the dataset.
        :return: 0 if the dataset is already in the model, else return 1.
        
        :doc-author: Trelent
        """
        if dataSet in self.model.dataSets or dataSet in self.model.loadedFiles:
            print("A dataset species with this name already exists")
            return 0
        else:
            self.model.dataSets[dataSet] = {}
            return 1
    
    def loadFile(self, filePath, fileName):
        """
        The loadFile function loads a file into the model.
            Args:
                filePath (str): The path to the file to be loaded.
                fileName (str): The name of the new data set created from this function.
        
            Returns: 
                int: 1 if successful, 0 otherwise.
        
        :param self: Used to Access the attributes and methods of the class in python.
        :param filePath: Used to Specify the path to the file that is being loaded.
        :param fileName: Used to Save the file to a specific name.
        :return: A 1 if the file is loaded successfully and a 0 if it fails.
        
        :doc-author: Trelent
        """
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
        """
        The loadExcelSheet function loads a sheet from an Excel file into the model.
           The function takes three arguments: 
               1) filePath - the path to the Excel file
               2) sheetName - name of the worksheet in that Excel file
               3) FileName - what you want to call this dataset in your model.
        
           If successful, it returns 1. Otherwise it returns 0.
        
        :param self: Used to Access variables that belongs to the class.
        :param filePath: Used to Specify the location of the file.
        :param sheetName: Used to Specify the sheet in the excel file that is to be loaded.
        :param fileName: The index to Store the file in the loadedfiles dictionary.
        :return: 1 if successful, otherwise 0
        
        :doc-author: Trelent
        """
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
        """
        The getDataSets function returns a list of DataSet objects.
        
        The getDataSets function accepts no arguments and returns the DataSet dictionary.
        
        :param self: Used to Access variables that belongs to the class.
        :return: A dictionary of datasets that are available in the current project.
        
        :doc-author: Trelent
        """
        return self.model.dataSets

    def getLoadedDataFrame(self, name):
        """
        The getLoadedDataFrame function returns a loaded dataframe from the model. 
        If the name is not in the list of loaded dataframes, it prints an error message and returns None.
        
        :param self: Used to Access the class variables.
        :param name: Used to Check if the dataframe is already loaded.
        :return: A dataframe if the name is valid.
        
        :doc-author: Trelent
        """
        if name not in self.model.loadedFiles:
            print("Not a valid dataframe")
            return None
        return self.model.loadedFiles[name]["file"]
    
    def getLoadedFiles(self):
        return self.model.loadedFiles
    
    def save(self, filePath):
        """
        The save function saves the dataframes in the model to a specified HDF File.
        It takes one argument, which is a string containing the file path and name of 
        the desired save location. It returns 1 if successful, 0 otherwise.
        
        :param self: Used to Refer to the object itself.
        :param filePath: Used to Specify the path to which the data will be saved.
        :return: 1 if the save was successful and 0 otherwise.
        
        :doc-author: Trelent
        """
        filePath = checkForExt(filePath, "hdf")
        print(f'Attempting save at {filePath}')
        try:
            Model.saveDFs(filePath, self.model.loadedFiles, self.model.dataSets)
            return 1
        except IOError:
            return 0
        
    def loadProject(self, filePath):
        print(f'Trying to get HDF file at path {filePath}')
        try:
            newDataFrames = Model.HDFtoDict(filePath)
            self.model.loadedFiles = newDataFrames[0]
            self.model.dataSets = newDataFrames[1]
            #self.model.config = newDataFrames[2]
            return 1
        except AttributeError:
            return 0
    
    def getLoadedFile(self, fileName, files=True):
        """
        The getLoadedFile function returns the file object of a loaded file. If the file is not loaded, it returns None.
        
        :param self: Used to Access variables that belongs to the class.
        :param fileName: Used to Check if the file has already been loaded.
        :param files=True: Used to Determine if the function is being used to return a file or not.
        :return: The Dataframe if files is true, otherwise return the dictionary entry from the loadedfiles dictionary
        
        :doc-author: Trelent
        """
        if fileName in self.model.loadedFiles:
            if files:
                #print("Here I am")
                return self.model.loadedFiles[fileName]["file"]
            else:
                #print("There I go")
                return self.model.loadedFiles[fileName]
        return None
    
    def getConfigUnits(self):
        return self.model.config.keys()
    
    def getConfigSubUnits(self, unit):
        """
        The getConfigSubUnits function returns a list of all the subunits that are configured for a given unit.
        
        :param self: Used to Access the class's attributes and methods.
        :param unit: Used to Specify the unit for which we want to get the configuration.
        :return: The config of the unit passed in.
        
        :doc-author: Trelent
        """
        if unit in self.model.config:
            return self.model.config[unit]
        else:
            return None
    
    def deleteFile(self, fileName):
        """
        The deleteFile function removes a file from the loadedFiles dictionary.
           If the file is not in the dictionary, it returns 0. Otherwise, it returns 1.
        
        :param self: Used to Refer to the object that is calling the function.
        :param fileName: Used to Delete the file from the loadedfiles dictionary.
        :return: 1 if successful, otherwise 0.
        
        :doc-author: Trelent
        """
        if fileName in self.model.loadedFiles:
            del self.model.loadedFiles[fileName]
            return 1
        else:
            return 0

    def getDataGroup(self, dataSet, dataGroup):
        """
        The getDataGroup function returns a dataGroup from the model.
        
        :param self: Used to Access variables that belongs to the class.
        :param dataSet: Used to Specify which dataset to get the datagroup from.
        :param dataGroup: Used to Specify which datagroup to retrieve from the model.
        :return: The datagroup for a given dataset.
        
        :doc-author: Trelent
        """
        if dataSet not in self.model.dataSets or dataGroup not in self.model.dataSets[dataSet]:
            print("This datagroup/dataSet does not exist")
            return 0
        else:
            return self.model.dataSets[dataSet][dataGroup]

    def deleteDataGroup(self, dataSet, dataGroup):
        """
        The deleteDataGroup function deletes a dataGroup from the model.
        
        :param self: Used to Reference the class.
        :param dataSet: Used to Specify which dataset the datagroup is in.
        :param dataGroup: Used to Specify which datagroup to delete.
        :return: 1.
        
        :doc-author: Trelent
        """
        if dataSet not in self.model.dataSets:
            print("This dataSet does not exist")
            return 0
        if dataGroup in self.model.dataSets[dataSet]:
            del self.model.dataSets[dataSet][dataGroup]
            return 1
        print("This dataGroup is not in this dataSet")
        return 0

    def dataToGroup(self, dataSet, dataGroup, subUnit, fileName, measurements, dates):
        """
        Imports data from a loaded file into a datagroup
        
        :param self: Used to Reference the class instance.
        :param dataSet: Used to Specify which dataset the datagroup belongs to.
        :param dataGroup: Used to Specify which datagroup to store the data in
        :param subUnit: Used to Specify the subunit of the datagroup that is to be used.
        :param fileName: Used to Specify the name of the file the data came from.
        :param measurements: Used to Specify which measurements to include in the datagroup.
        :param dates: Used to Specify which dates to include in the datagroup.
        :return: 1 if successful, else 0
        
        :doc-author: Trelent
        """
        print(f'dates = {dates}, measurements= {measurements}')
        if dataSet not in self.model.dataSets:
            print("This dataSet does not exist")
            return 0
        else:
            if dataGroup not in self.model.dataSets[dataSet]:
                print("This datagroup does not exist for the dataset " + dataSet)
                return 0
            dataGroup = self.model.dataSets[dataSet][dataGroup]
            dataDict = defaultdict(list)
            for date, measurement in itertools.zip_longest(dates, measurements, fillvalue="N/A"):
                #print(f'Adding {date}')
                dataDict[date] = measurement
            dataDict = dict(dataDict)
            print(f'Imported data using dictionary {dataDict}')
            dataGroup["data"].append({"source": fileName, "measurements":  dataDict, "unit": subUnit})
            return 1

    def addDataGroup(self, dataSet, dataGroup, Unit):
        """
        The addDataGroup function adds a new dataGroup to the specified dataSet.
        If the specified dataSet does not exist, print an error message and return 0
        If the specified dataGroup already exists in that dataset, it will print an error message and return 0.
        
        :param self: Used to Refer to the object instance itself.
        :param dataSet: Used to Specify which dataset the new datagroup will be added to.
        :param dataGroup: Used to Create a new datagroup in the dataset.
        :param Unit: Used to Specify the unit of measurement for the data in this group.
        :return: 0 if the method fails, otherwise 1
        
        :doc-author: Trelent
        """
        if dataSet not in self.model.dataSets:
            print("This dataSet does not exist")
            return 0
        if dataGroup in self.model.dataSets[dataSet]:
            print("This dataGroup already exists")
            return 0
        self.model.dataSets[dataSet][dataGroup] = {}
        self.model.dataSets[dataSet][dataGroup]["data"] = []
        self.model.dataSets[dataSet][dataGroup]["unit"] = Unit
        return 1

    def getDataGroups(self, dataSet):
        """
        The getDataGroups function returns a list of the data groups in the specified dataset.
        
        :param self: Used to Access the variables and methods of the class in python.
        :param dataSet: Used to Specify which dataset to use.
        :return: A list of the data groups that are associated with a particular dataset.
        
        :doc-author: Trelent
        """
        if dataSet not in self.model.dataSets:
            print("This dataset does not exist")
            return None
        else:
            return self.model.dataSets[dataSet]

    def exportDataGroups(self, filePath, dataSet, dataGroups):
        """
        The exportDataGroups function exports a DataFrame of the data in the specified data groups.
        
        :param self: Used to Reference the class instance (the object) when calling a method.
        :param filePath: Used to Specify where the file should be saved.
        :param dataSet: Used to Specify which dataset to export.
        :param dataGroups: Used to Specify which data groups to export.
        :return: A dataframe of the specified datagroups from the specified dataset.
        
        :doc-author: Trelent
        """
        filePath = checkForExt(filePath, "xlsx")
        if dataSet not in self.model.dataSets:
            print("This is not a valid DataSet")
            return 0
        realDataGroups = self.getDataGroups(dataSet)
        dataGroupData = []
        for dataGroup in dataGroups:
            if dataGroup not in realDataGroups:
                print(f'{dataGroup} is not a datagroup in {dataSet}')
                return 0
            else:
                dataGroupData.append({"name":dataGroup, "dataGroup": self.getDataGroup(dataSet, dataGroup)})
        dates = []
        columns = ["Dates (YYYY-MM-DD)"]
        rows = []
        for dG in dataGroupData:  
            for i in range(len(dG["dataGroup"]["data"])):
                realDG = dG["dataGroup"]["data"][i]
                dates += realDG["measurements"].keys()
                columns.append(f'[{dG["name"]}] {realDG["source"]} ({dG["dataGroup"]["unit"]})')
        dates = list(set(dates))
        #Sort the dates using various formats
        try:
            dates.sort(key = lambda date: datetime.strptime(date, '%Y-%m-%d'))
        except:
            try:
                dates.sort(key = lambda date: datetime.strptime(date, '%Y%m%d'))
            except:
                try:
                    dates.sort(key = lambda date: datetime.strptime(date, '%-m%-d%y'))
                except:
                    pass
        for date in dates:
            newRow = []
            newRow.append(date)
            for dG in dataGroupData:
                for i in range(len(dG["dataGroup"]["data"])):
                    realDG = dG["dataGroup"]["data"][i]
                    if date in realDG["measurements"]:
                        newRow.append(f'{realDG["measurements"][date]} {realDG["unit"]}')
                    else:
                        newRow.append("N/A")
            rows.append(newRow)
        finalFile = DataFrame(rows, columns=columns)
        finalFile.to_excel(filePath, sheet_name=dataSet)
        return 1
        
        
        

        
    
    
def getFileType(filePath):
    file_name = os.path.basename(filePath)
    file_extension = os.path.splitext(file_name)[1][1:].lower()
    if file_extension == "csv":
        return "csv"
    elif file_extension.find("xls") >= 0:
        return "Excel"
    else:
        return "unsupported"