
import fileLoading
import os

def checkForExt(filePath, ext):
    if os.path.splitext(os.path.basename(filePath))[1][1:] != ext:
        return filePath + f'.{ext}'
    else:
        return filePath

class Controller:
    
    def __init__(self):
        self.loadedFiles = {}

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
    
    def loadFile(self, filePath):
        """
        The loadFile function loads a file into memory and returns the data in a dictionary.
            The function takes one argument, the path to the file to be loaded.
            It returns 1 if successful and 0 if not.
        
        :param self: Used to Access variables that belongs to the class.
        :param filePath: Used to Store the filepath of the file that is being loaded.
        :return: A 1 if the file was loaded successfully, a 2 if there are multiple sheets in an excel file and a 0 if it failed.
        
        :doc-author: Trelent
        """
        try:
            newFile = fileLoading.loadFile(filePath)
            print("test")
            self.loadedFiles[os.path.splitext(os.path.basename(filePath))[0]] = newFile
            if newFile["fileType"] == "Excel" and len(newFile["file"].keys()) > 1:
                return 2
            print(f'Successfully loaded file')
            return 1
        except IOError:
            print(f'Error loading file, IOError occured')
            return 0
        except TypeError:
            print(f'The type of file specified is not supported')
            return 0
    
    def clearLoadedFiles(self):
        """
        The clearLoadedFiles function clears the loaded files list.
        
        :param self: Used to Refer to the object itself.
        
        :doc-author: Trelent
        """
        self.loadedFiles = {}
    
    def save(self, filePath):
        filePath = checkForExt(filePath, "hdf")
        print(f'Attempting save at {filePath}')
        files = {}
        try:
            for file in self.loadedFiles.keys():
                files[file] = files[file]["file"]
            fileLoading.saveDFs(filePath, files)
            return 1
        except:
            return 0
        

    def loadProject(self, filePath):
        try:
            newDataFrames = fileLoading.HDFtoDict(filePath)
            self.loadedFiles = newDataFrames
            return 1
        except:
            return 0
    