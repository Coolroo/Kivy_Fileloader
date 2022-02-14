from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivymd.uix.button import MDFillRoundFlatIconButton, MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDToolbar
from plyer import filechooser
import fileLoading
import os

class ConverterApp(MDApp):
    def loadFile(self, args):
        """
        The loadFile function is used to load a file into the program.
        
        :param self: Used to access the class attributes.
        :param args: Used to pass arguments to the function.
        :return: the dataframe of the file that was loaded.
        :doc-author: Trelent
        """
        try:
            file = filechooser.open_file(filters = [["Data Files (csv, xls, xlsx)", "*.xls", "*.csv", "*.xlsx"]]) 
            literalFile = fileLoading.loadFile(file[0])
            self.loadedFile.color = [0,0,0,1]
            self.loadedFile.text = "Loaded " + file[0]
            self.files[os.path.splitext(os.path.basename(file[0]))[0]] = literalFile
            self.numFiles.text = "Number of files loaded = " + str(len(self.files))
        except:
            self.loadedFile.text = "COULD NOT LOAD FILE"
            self.loadedFile.color = [1,0,0,1]

    def saveLoadedFiles(self, args):
        """
        The saveLoadedFiles function saves the loaded dataframes to a HDF file.
        
        :param self: Used to access the attributes and methods of the class in python.
        :param args: Used to pass any additional arguments to the function.
        :return: the path of the file that is being saved.
        :doc-author: Trelent
        """
        try:
            file = filechooser.save_file(filters = ["*.hdf"])
            print(file)
            filePath = os.path.splitext(file[0])[0] + ".hdf"
            fileLoading.saveDFs(filePath, self.files)
            self.loadedFile.text = "Successfully saved loaded dataframes to " + filePath
            self.loadedFile.color = [0,1,0,1]
        except IOError:
            self.loadedFile.text = "COULD NOT SAVE FILE"
            self.loadedFile.color = [1,0,0,1]
        

    def openHDF(self, args):
        """
        The openHDF function is used to open an HDF file and load it into the program.
        
        :param self: Used to access the class attributes.
        :param args: Used to pass arguments to the function.
        :return: the filePath, which we can use to call the HDFtoDict function.
        :doc-author: Trelent
        """
        try:
            filePath = filechooser.open_file(filters=["*.hdf"])
            self.files = fileLoading.HDFtoDict(filePath)
            self.loadedFile.color = [0,1,0,1]
            self.loadedFIle.text = 'Successfully loaded HDF file'
            self.numFiles.text = "Number of files loaded = " + str(len(self.files))
        except:
            self.loadedFile.text = "COULD NOT LOAD HDF FILE"
            self.loadedFile.color = [1,0,0,1]

    def build(self):
        self.files = {}
        screen = MDScreen()
        screen.add_widget(MDFillRoundFlatButton(
            text="LOAD FILE",
            font_size = 17,
            pos_hint = {"center_x": 0.25, "center_y":0.15},
            on_press = self.loadFile
        ))
        screen.add_widget(MDFillRoundFlatButton(
            text="SAVE LOADED FILES",
            font_size = 17,
            pos_hint = {"center_x": 0.75, "center_y":0.15},
            on_press = self.saveLoadedFiles
        ))
        screen.add_widget(MDFillRoundFlatButton(
            text="LOAD HDF",
            font_size = 17,
            pos_hint = {"center_x": 0.5, "center_y":0.15},
            on_press = self.openHDF
        ))
        self.numFiles = MDLabel(
            halign="center",
            pos_hint = {"center_x": 0.5, "center_y":0.35},
            theme_text_color = "Secondary"
        )
        self.loadedFile = MDLabel(
            halign="center",
            color=[0,0,0,1],
            pos_hint = {"center_x": 0.5, "top_y":0.05},
            theme_text_color = "Secondary"
        )
        screen.add_widget(self.loadedFile)
        screen.add_widget(self.numFiles)

        return screen

if __name__ == '__main__':
    ConverterApp().run()
