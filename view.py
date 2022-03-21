from Controller import Controller, getFileType

from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
from kivy.app import App


from kivymd.app import MDApp
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget, OneLineAvatarIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.textfield import MDTextField

import usefulFunctions
from plyer import filechooser
import pandas as pd

controller = Controller()
Builder.load_string(
    '''
#:import images_path kivymd.images_path
<TooltipIconLeftWidget@IconLeftWidget+MDTooltip>

<PreferencesMenu>
    MDBoxLayout:
        orientation: 'horizontal'
        

<ChemicalAddDialog>
    orientation: 'vertical'
    spacing: dp(12)
    size_hint_y: None
    height: dp(120)
    
    MDTextField:
        id: chemicalName
        hint_text: "Name of the chemical species"
        on_text: root.validate()
    
    MDBoxLayout:
        orientation: "horizontal"
        
        MDLabel:
            text: "X-Axis Units"
            
        MDTextField:
            id: XAxis
            hint_text: "Units for the X-Axis"
            on_text: root.validate()
            
    MDBoxLayout:
        orientation: "horizontal"
        
        MDLabel:
            text: "Y-Axis Units"
            
        MDTextField:
            hint_text: "Units for the Y-Axis"
            id: YAxis
            on_text: root.validate()
    
    
<ImportExcelFile>
    orientation: "horizontal"
    on_release: root.setStatus(check, sheetName)
    
    CheckboxLeftWidget:
        id: check
        group: "check"
        textbox: sheetName
    
    MDTextField:
        id: sheetName
        hint_text: "Sheet Name"
        size_hint_x: None
        width: root.width/3
        pos_hint: {'right': 1}
        pos: root.pos
        on_text: root.checkValidity(check)

<ImportFile>
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "120dp"
    
    MDLabel:
        id: fileLabel
        text: 'Importing file'

    MDTextField:
        id: dialogTextBox
        hint_text: "File Name (No special characters, only numbers and letters)"


<OptionRow>
    IconLeftWidget:
        icon: root.icon
        
<ChemicalData>
    TooltipIconLeftWidget:
        icon: root.icon
        pos_hint: {"center_x": .5, "center_y": .5}

<FileRow>
    on_release: self.createDropDown()
    TooltipIconLeftWidget:
        icon: root.icon
        tooltip_text: root.originalPath
        pos_hint: {"center_x": .5, "center_y": .5}

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
                    left_action_items: [["plus-thick", lambda x: root.loadFile(), "Load a new file"]]

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
                    title: "Data"
                    md_bg_color: self.theme_cls.accent_color
                    type: "top"
                    anchor_title: "center"
                    left_action_items: [["plus-thick", lambda x: root.showChemicalDialog(), "Add Chemical Species"]]
                
                RecycleView:
                    id: chemicalList
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

class ChemicalAddDialog(BoxLayout):
    button = ObjectProperty()
        
    def validate(self):
        self.button.disabled = (self.ids.XAxis.text == "" or 
                                self.ids.YAxis.text == "" or 
                                self.ids.chemicalName.text == "" or 
                                self.ids.chemicalName.text in controller.getChemicalData() or 
                                self.ids.chemicalName.text in controller.getLoadedFiles() or 
                                not usefulFunctions.isIdentifier(self.ids.chemicalName.text))
    
        
class ImportExcelFile(OneLineAvatarIconListItem):
    sheet = StringProperty()
    confirmButton = ObjectProperty(None)
    textbox = ObjectProperty(None)
    
    def setStatus(self, check, textBox):
        check.active = not check.active
        
        self.checkValidity(check)
        
    def checkValidity(self, check):
        validOption = False
        check_list = check.get_widgets(check.group)
        for ch in check_list:
            if ch.active:
                validOption = validOption or usefulFunctions.isIdentifier(ch.textbox.text)
        
        self.confirmButton.disabled = not validOption
        

class TooltipLeftIconWidget(IconLeftWidget, MDTooltip):
    pass

class ImportFile(BoxLayout):
    Path = StringProperty()

class OptionRow(OneLineIconListItem):
    icon = StringProperty()

class ChemicalData(OneLineIconListItem):
    icon = StringProperty()

class FileRow(OneLineIconListItem):
    icon = StringProperty()
    originalPath = StringProperty()
    menu = None
    
    def createDropDown(self):
        if not self.menu:
            menu_items = [{
                "viewclass": "OptionRow",
                "text": "New Project",
                "icon": "file",
                "height": dp(40),
                "on_press": lambda : self.screen.loadFile(),
                "on_release": lambda : self.closeMenu()
            },
            {
                "viewclass": "OptionRow",
                "text": "Save Project",
                "icon": "content-save",
                "height": dp(40),
                "on_press": lambda : self.screen.saveFile(),
                "on_release": lambda : self.closeMenu()
            },
            ]
            self.menu = MDDropdownMenu(
                items=menu_items,
                width_mult=3,
            )    
        self.menu.caller = self
        self.menu.open()

    def closeMenu(self):
        self.menu.dismiss()


class FileList(Screen):

    importDialog = None
    importDialogExcel = None
    chemicalDialog = None
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
            filetype = getFileType(file[0])
            if filetype == "csv":
                self.showImportDialog(file[0])
            elif filetype == "Excel":
                sheets = pd.ExcelFile(file[0]).sheet_names
                self.showImportDialogExcel(file[0], sheets)
            else:
                Snackbar(text="Could not load an unsupported file type!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()

    def saveFile(self):
        global controller
        file = filechooser.save_file(filters = [["HDF File", "*.hdf"]])
        if file:
            returnVal = controller.save(file[0])
            if returnVal:
                Snackbar(text="Successfully Saved File!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
                print("Successfully saved file!")
            else:
                Snackbar(text="Could not save file!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
                print("Could not save file!")

    def list_files(self):
        global controller
        '''Builds a list of icons for the screen MDIcons.'''
        fileAssociation = {"Excel": "file-excel", "csv": "file"}
        def add_file(file, filePath):
            self.ids.rv.data.append(
                {
                    "viewclass": "FileRow",
                    "text": filePath,
                    "icon": fileAssociation[file["fileType"]],
                    "originalPath": file["fileName"],
                }
            )

        self.ids.rv.data = []
        files = controller.getLoadedFiles()
        fileKeys = files.keys()
        for file in fileKeys:
            add_file(files[file], file)
        self.list_chemicals()
                
    def list_chemicals(self):
        global controller
        
        def add_file(chemicalData):
            self.ids.chemicalList.data.append(
                {
                    "viewclass": "ChemicalData",
                    "text": chemicalData,
                    "icon": "atom"
                })
        self.ids.chemicalList.data = []
        keys = controller.chemicalData.keys()
        for key in keys:
            add_file(key)
    
    def loadProject(self):
        global controller
        file = filechooser.open_file(filters = [["HDF File (*.hdf)", "*.hdf"]])
        if file:
            returnVal = controller.loadProject(file[0])
            if returnVal:
                Snackbar(text="Successfully Loaded Project!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
            else:
                Snackbar(text="Could not Load Project!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
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
                Snackbar(text="Successfully Loaded File!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
                self.list_files()
                return
            Snackbar(text="Could Not Load File!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()


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
        self.importDialog.content_cls.ids.fileLabel.text = f'Importing file {filePath}'
        self.importDialog.open()
    
    def showChemicalDialog(self):
        global controller

        def closeDialog(button):
            self.chemicalDialog.dismiss()

        def finishLoad(button):
           content = self.chemicalDialog.content_cls
           chemicalName = content.ids.chemicalName.text
           yAxis = content.ids.YAxis.text
           xAxis = content.ids.XAxis.text
           
           controller.addChemicalData(chemicalName, xAxis, yAxis)
           self.list_files()
           closeDialog(button)
           

        textInput = MDTextField()
        button = MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_release=finishLoad,
                    disabled=True,
                )
        self.chemicalDialog = MDDialog(
        title="Please select a name for the chemical species",
        type="custom",
        content_cls=ChemicalAddDialog(button=button),
        auto_dismiss=False,
        buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_press=closeDialog,
                ),
                button,
            ],
        )
        self.chemicalDialog.open()
        
        


    def showImportDialogExcel(self, filePath, sheets):
        global controller

        def closeDialog(button):
            self.importDialogExcel.dismiss()

        def finishLoad(button):
            items = self.importDialogExcel.items
            successfulLoads = 0
            numSheets = 0
            for sheet in items:
                if sheet.ids.check.active:
                    text = sheet.ids.sheetName.text
                    if text == "":
                        continue
                    numSheets+=1
                    returnVal = controller.loadExcelSheet(filePath, sheet.sheet, text)
                    if returnVal == 1:
                        successfulLoads+=1
            Snackbar(text=f'Successfully loaded {successfulLoads}/{numSheets} sheets', snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
            self.importDialogExcel.dismiss()
            self.list_files()

        button = MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_release=finishLoad,
                    disabled=True,
                )
        self.importDialogExcel = MDDialog(
        title="Please select the sheets you would like to import, and then give them a name",
        type="confirmation",
        auto_dismiss=False,
        items = [ImportExcelFile(text=sheetName, sheet=sheetName, confirmButton=button) for sheetName in sheets],
        buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_press=closeDialog,
                ),
                button,
            ],
        )
        self.importDialogExcel.open()



class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = FileList()

    def build(self):
        menu_items = [{
            "viewclass": "OptionRow",
            "text": "New Project",
            "icon": "file",
            "height": dp(40),
            "on_press": lambda : self.clearProject(),
            "on_release": lambda : self.closeMenu()
        },
        {
            "viewclass": "OptionRow",
            "text": "Save Project",
            "icon": "content-save",
            "height": dp(40),
            "on_press": lambda : self.screen.saveFile(),
            "on_release": lambda : self.closeMenu()
        },
        {
            "viewclass": "OptionRow",
            "text": "Load Project",
            "icon": "folder-open",
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
        
    def clearProject(self):
        self.confirmationDialog()
    
    def confirmationDialog(self):
        global controller

        def closeDialog(button):
            self.confirmDialog.dismiss()

        def confirm(button):
            controller.clearProject()
            self.screen.list_files()
            closeDialog(button)
        
        
        
        self.confirmDialog = MDDialog(
        title="WARNING!",
        text="Warning! This will clear all the data loaded into the app, are you sure you wish to proceed?",
        auto_dismiss=False,
        buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_press=closeDialog,
                ),
                MDFlatButton(
                    text="CONFIRM",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_press=confirm,
                ),
            ],
        )
        self.confirmDialog.open()
    
        


MainApp().run()