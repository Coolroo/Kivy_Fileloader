from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

from kivymd.icon_definitions import md_icons
from kivymd.app import MDApp
from kivymd.uix.list import OneLineIconListItem

from plyer import filechooser
import fileLoading
import os

files = {}
Builder.load_string(
    '''
#:import images_path kivymd.images_path


<FileRow>


<FileList>

    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(20)

        Button:
            text: "Load File"
            font_size: 32
            on_press: root.loadFile()

        RecycleView:
            id: rv
            key_viewclass: 'viewclass'
            key_size: 'height'

            RecycleBoxLayout:
                padding: dp(10)
                default_size: None, dp(48)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
'''
)


class FileRow(OneLineIconListItem):
    pass


class FileList(Screen):
    def loadFile(self):
        """
        The loadFile function is used to load a file into the program.
        
        :param self: Used to access the class attributes.
        :param args: Used to pass arguments to the function.
        :return: the dataframe of the file that was loaded.
        :doc-author: Trelent
        """
        global files
        print("in LoadFile")
        try:
            file = filechooser.open_file(filters = [["Data Files (csv, xls, xlsx)", "*.xls", "*.csv", "*.xlsx"]]) 
            literalFile = fileLoading.loadFile(file[0])
            files[os.path.splitext(os.path.basename(file[0]))[0]] = literalFile
        except:
            pass
        self.list_files()

    def list_files(self, text=""):
        '''Builds a list of icons for the screen MDIcons.'''
        global files

        def add_file(filePath):
            self.ids.rv.data.append(
                {
                    "viewclass": "FileRow",
                    "text": filePath,
                    "callback": lambda x: x,
                }
            )

        self.ids.rv.data = []
        for fileName in files.keys():
            add_file(fileName)


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = FileList()

    def build(self):
        return self.screen

    def on_start(self):
        self.screen.list_files()


MainApp().run()