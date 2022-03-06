
import fileLoading

class Controller:
    
    def __init__(self):
        self.loadedFiles = {}


    def getLoadedFiles(self):
        return self.loadedFiles
    
    def loadFile(self, filePath):
        """
        The loadFile function loads a file from the specified path and places it into the loadedFiles dictionary
        It returns True if it succeeds and False if it fails.
        
        :param self: Used to Refer to the object itself.
        :param filePath: Used to Specify the path to the file that is being loaded.
        :return: True if the file was loaded successfully.
        
        :doc-author: Trelent
        """
        try:
            newFile = fileLoading.loadFile(filePath)
            self.loadedFiles[filePath] = newFile
            print(f'Successfully loaded file at path {filePath}')
            return True
        except IOError:
            print(f'Error loading file at path {filePath}, IOError occured')
            return False
        except TypeError:
            print(f'The type of file specified at the path {filePath} is not supported')
            return False
    
    def clearLoadedFiles(self):
        """
        The clearLoadedFiles function clears the loaded files list.
        
        :param self: Used to Refer to the object itself.
        
        :doc-author: Trelent
        """
        self.loadedFiles = {}