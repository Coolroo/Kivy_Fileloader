from Controller import Controller

from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp

from kivymd.app import MDApp
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivy.app import App

from plyer import filechooser
import keyword

controller = Controller()
Builder.load_string(
    '''
#:import images_path kivymd.images_path

<ImportFile>
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "120dp"

    MDTextField:
        id: dialogTextBox
        hint_text: "File Name (No special characters, only numbers and letters)"


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
                    md_bg_color: self.theme_cls.accent_dark
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
                    md_bg_color: self.theme_cls.accent_color
                    type: "top"
                AnchorLayout:
                    id: "dataTableLayout"
                
'''
)

class ImportFile(BoxLayout):
    pass

class FileRow(OneLineIconListItem):
    icon = StringProperty()


class FileList(Screen):

    importDialog = None
    buttonDisabled=True

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
            #self.showImportDialog()
            self.showImportDialog(file[0])

    def saveFile(self):
        global controller
        file = filechooser.save_file(filters = [["HDF File", "*.hdf"]])
        if file:
            returnVal = controller.save(file[0])
            if returnVal:
                Snackbar(text="Successfully Saved File!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5).open()
                print("Successfully saved file!")
            else:
                Snackbar(text="Could not save file!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5).open()
                print("Could not save file!")

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
    
    def loadProject(self):
        global controller
        file = filechooser.open_file(filters = [["HDF File (*.hdf)", "*.hdf"]])
        if file:
            returnVal = controller.loadProject(file[0])
            if returnVal:
                Snackbar(text="Successfully Loaded Project!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5).open()
            else:
                Snackbar(text="Could not Load Project!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5).open()
        self.list_files()

    
    def showImportDialog(self, filePath):
        global controller

        def closeDialog(button):
            self.importDialog.dismiss()

        def finishLoad(button):
            fileName = self.importDialog.content_cls.ids.dialogTextBox.text
            returnVal = controller.loadFile(filePath, fileName)
            self.importDialog.dismiss()
            if returnVal > 0:
                if returnVal == 2:
                    pass
                Snackbar(text="Successfully Loaded File!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5).open()
                self.list_files()
                return
            Snackbar(text="Could Not Load File!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5).open()


        if not self.importDialog:
            self.importDialog = MDDialog(
            title="Please select a name for the imported file",
            type="custom",
            content_cls=ImportFile(),
            auto_dismiss=False,
            buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=App.get_running_app().theme_cls.primary_color,
                        on_press=closeDialog
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=App.get_running_app().theme_cls.primary_color,
                        on_release=finishLoad,
                    ),
                ],
            )
        self.importDialog.open()



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
        {
            "viewclass": "FileRow",
            "text": "Load Project",
            "icon": "folder-open",
            "height": dp(40),
            "on_press": lambda : self.screen.loadProject(),
            "on_release": lambda : self.closeMenu()
        },
        {
            "viewclass": "FileRow",
            "text": "Change Theme",
            "icon": "border-color",
            "height": dp(40),
            "on_press": lambda : self.screen.loadProject(),
            "on_release": lambda : self.closeMenu()
        },
        ]
        self.menu= MDDropdownMenu(
            items=menu_items,
            width_mult=3
        )
        self.importDialogDisabled=True
        return self.screen

    def on_start(self):
        self.screen.list_files()

    
    def loadMenu(self, button):
        self.menu.caller = button
        self.menu.open()

    def closeMenu(self):
        self.menu.dismiss()
        


MainApp().run()