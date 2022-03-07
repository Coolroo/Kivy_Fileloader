from Controller import Controller

from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp

from kivymd.app import MDApp
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar

from plyer import filechooser

controller = Controller()
Builder.load_string(
    '''
#:import images_path kivymd.images_path

<FileRow>
    IconLeftWidget:
        icon: root.icon


<FileList>

    MDBoxLayout:
        orientation: 'vertical'

        MDToolbar:
            title: "Chemistry App"
            left_action_items: [["menu", lambda x: app.loadMenu(x)]]

        MDBoxLayout:
            orientation: 'horizontal'

            MDBoxLayout:
                orientation: 'vertical'
                size_hint_x: None
                width: root.width/3
                
                MDToolbar:
                    title: "Loaded Files"
                    md_bg_color: 1, 0, 0, 1
                    on_action_button: lambda x: root.loadFile()
                    type: "top"
                    type_height: "small"
                    mode: "free-center"
                    round: dp(80)
                    anchor_title: "center"
                    font_size: 16

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
            
            MDBoxLayout:
                orientation: 'vertical'

                MDToolbar:
                    title: "Load Data"
                    md_bg_color: 0, 1, 0, 1
                    type: "top"
                AnchorLayout:
                    id: "dataTableLayout"
                
'''
)


class FileRow(OneLineIconListItem):
    icon = StringProperty()


class FileList(Screen):
    def loadFile(self):
        global controller
        """
        The loadFile function is used to load a file into the program.
        
        :param self: Used to access the class attributes.
        :param args: Used to pass arguments to the function.
        :return: the dataframe of the file that was loaded.
        :doc-author: Trelent
        """
        file = filechooser.open_file(filters = [["Data Files (csv, xls, xlsx)", "*.xls", "*.csv", "*.xlsx"]])
        if file:
            returnVal = controller.loadFile(file[0])
            if returnVal > 0:
                if returnVal == 2:
                    pass
                Snackbar(text="Successfully Loaded File!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5).open()
                self.list_files()
                return
        Snackbar(text="Could Not Load File!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5).open()
    
    def saveFile(self):
        global controller
        file = filechooser.save_file(filters = [["HDF File", "*.hdf"]])
        if file:
            returnVal = controller.save()
            if returnVal:
                Snackbar(text="Successfully Saved File!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5).open()
            else:
                Snackbar(text="Could not save file!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5).open()

    def list_files(self, text=""):
        global controller
        '''Builds a list of icons for the screen MDIcons.'''
        fileAssociation = {"Excel": "file-excel", "csv": "file"}
        def add_file(file, filePath):
            self.ids.rv.data.append(
                {
                    "viewclass": "FileRow",
                    "text": filePath,
                    "icon": fileAssociation[file["fileType"]],
                    "callback": lambda x : x
                }
            )

        self.ids.rv.data = []
        with controller as files:
            fileKeys = files.keys()
            for file in fileKeys:
                add_file(files[file], file)



class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = FileList()

    def build(self):
        menu_items = [{
            "viewclass": "FileRow",
            "text": "Load File",
            "icon": "folder",
            "height": dp(40),
            "on_press": lambda : self.screen.loadFile(),
            "on_release": lambda : self.closeMenu()
        },
        {
            "viewclass": "FileRow",
            "text": "Save Project",
            "icon": "content-save",
            "height": dp(40),
            "on_press": lambda : self.screen.saveFile(),
            "on_release": lambda : self.closeMenu()
        },
        ]
        self.menu= MDDropdownMenu(
            items=menu_items,
            width_mult=3
        )

        file_menu_items = [
            {
                "viewclass": "OneLineListItem"
            }]
        return self.screen

    def on_start(self):
        self.screen.list_files()

    
    def loadMenu(self, button):
        self.menu.caller = button
        self.menu.open()

    def closeMenu(self):
        self.menu.dismiss()
        


MainApp().run()