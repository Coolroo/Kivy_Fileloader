from Controller import Controller, getFileType

from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
from kivy.app import App
from kivy.core.window import Window


from kivymd.app import MDApp
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget, OneLineAvatarIconListItem, OneLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.datatables import MDDataTable

import usefulFunctions
from plyer import filechooser
import pandas as pd
from threading import Thread
import tabloo

controller = Controller()
Builder.load_file('AppLayout.kv') 

class SelectDataGroup(OneLineAvatarIconListItem):
    divider = None

    def set_icon(self, instance):
        instance.active = not instance.active

class DataGroupList(BoxLayout):
    pass

class ImportDatasetData(BoxLayout):
    button = ObjectProperty()
    dataFrame = StringProperty()
    menu = None

    def validate(self):
        dataSet = self.ids.dataSet.current_item
        dataGroup = self.ids.dataGroup.current_item
        subUnit = self.ids.subUnit.current_item
        numRows = self.ids.numRows.text
        invalidID = self.ids.invalidID.text
        columnDates = self.ids.columnDates.text
        startRowDates = self.ids.startRowDates.text
        columnData = self.ids.columnData.text
        startRowData = self.ids.startRowData.text

        if dataGroup in controller.getDataGroups(dataSet):
            print(controller.getDataGroup(dataSet, dataGroup))

        validateDatasets = dataSet not in controller.getDataSets() or dataGroup not in controller.getDataGroups(dataSet) or subUnit not in controller.getConfigSubUnits(controller.getDataGroup(dataSet, dataGroup)["unit"])

        lenRows = len(controller.getLoadedDataFrame(self.dataFrame))
        validNumbers = numRows.isdigit() and startRowDates.isdigit() and startRowData.isdigit() and int(numRows) > 0 and int(startRowData) + int(numRows) <= lenRows and int(startRowDates) + int(numRows) <= lenRows

        numColumns = len(controller.getLoadedDataFrame(self.dataFrame).columns)
        columns = [usefulFunctions.column_string(i+1) for i in range(numColumns)]
        validColumns = columnDates in columns and columnData in columns 
        #print(f'columnData = {columnData}, "columnNames = {str(controller.getLoadedDataFrame(self.dataFrame).columns)}')
        print(f'validateDatasets = {validateDatasets}, validNumbers = {validNumbers}, validColumns = {validColumns}')
        self.button.disabled = validateDatasets or not validNumbers or not validColumns


    def setDropdownItem(self, dropdown, text):
        dropdown.set_item(text)
        self.menu.dismiss()
        self.menu = None
        self.validate()

    def showDataSetMenu(self, caller):
        global controller
        if self.menu:
            self.menu.dismiss()
        menu_items = []
        for dataCategory in controller.getDataSets():
            menu_items.append(
                {
                    "viewclass": "OneLineListItem",
                    "text": dataCategory,
                    "height": dp(40),
                    "width": dp(150),
                    "on_release": lambda x=f'{dataCategory}': self.setDropdownItem(self.ids.dataSet, x)
                    })
        self.menu= MDDropdownMenu(
            items=menu_items,
            width_mult=3
        )
        self.menu.caller = caller
        self.menu.open()

    def showDataGroupMenu(self, caller):
        global controller
        if self.ids.dataSet.current_item not in controller.getDataSets():
            return
        if self.menu:
            self.menu.dismiss()
        menu_items = []
        for dataCategory in controller.getDataGroups(self.ids.dataSet.current_item):
            menu_items.append(
                {
                    "viewclass": "OneLineListItem",
                    "text": dataCategory,
                    "height": dp(40),
                    "width": dp(150),
                    "on_release": lambda x=f'{dataCategory}': self.setDropdownItem(self.ids.dataGroup, x)
                    })
        self.menu= MDDropdownMenu(
            items=menu_items,
            width_mult=3
        )
        self.menu.caller = caller
        self.menu.open()


    def showUnitMenu(self, caller):
        if self.ids.dataSet.current_item not in controller.getDataSets() or self.ids.dataGroup.current_item not in controller.getDataGroups(self.ids.dataSet.current_item):
            return
        if self.menu:
            self.menu.dismiss()
            self.menu = None
        menu_items = []
        for Unit in controller.getConfigSubUnits(controller.getDataGroups(self.ids.dataSet.current_item)[self.ids.dataGroup.current_item]["unit"]):
            menu_items.append(
                {
                    "viewclass": "OneLineListItem",
                    "text": Unit,
                    "height": dp(40),
                    "width": dp(150),
                    "on_release": lambda x=f'{Unit}': self.setDropdownItem(self.ids.subUnit, x)
                    })
        self.menu= MDDropdownMenu(
            items=menu_items,
            width_mult=3
        )
        self.menu.caller = caller
        self.menu.open()

class AddDataGroup(BoxLayout):
    button = ObjectProperty()
    dataSet = StringProperty()
    menu = None

    def validate(self):
        self.button.disabled = not usefulFunctions.isIdentifier(self.ids.name.text) or  self.ids.name.text in controller.getDataSets()[self.dataSet]

    def setDropdownItem(self, dropdown, text):
        dropdown.set_item(text)
        self.menu.dismiss()
        self.menu = None
        self.validate()

    def showUnitMenu(self, caller):
        global controller
        if self.dataSet not in controller.getDataSets():
            return
        if self.menu:
            self.menu.dismiss()
            self.menu = None
        menu_items = []
        for Unit in controller.getConfigUnits():
            menu_items.append(
                {
                    "viewclass": "OneLineListItem",
                    "text": Unit,
                    "height": dp(40),
                    "width": dp(150),
                    "on_release": lambda x=f'{Unit}': self.setDropdownItem(self.ids.unit, x)
                    })
        self.menu= MDDropdownMenu(
            items=menu_items,
            width_mult=3
        )
        self.menu.caller = caller
        self.menu.open()
    
    pass

class DataTableDisplay(BoxLayout):
    pass

class SubunitDialog(BoxLayout):
    unit = ""
    confirmButton = ObjectProperty()
    
    def verify(self, name, ratio):
        nameCheck = name not in controller.getConfigSubUnits(self.unit) and usefulFunctions.isIdentifier(name)
        ratioCheck = ratio.isnumeric()
        self.confirmButton.disabled = nameCheck and ratioCheck     

class PreferencesLine(OneLineListItem):
    unit = StringProperty()
    dialog = ObjectProperty()
    
    def selectUnit(self):
        self.dialog.content_cls.selectUnit(self.unit)

class PreferencesMenu(BoxLayout):
    currUnit = ""
    subUnitDialog = None
    
    def addSubUnit(self):
        pass
    
    def selectUnit(self, unit):
        global controller
        subUnits = controller.getConfigSubUnits(unit)
        if subUnits is not None:
            self.currUnit = unit
            view = self.ids.subUnits
            self.ids.standardLabel.text = f'Standard: {subUnits["standard"]}'
            view.data = []
            for subUnit in subUnits:
                if subUnit != "standard":
                    view.data.append(
                        {
                            "viewclass": "OneLineListItem",
                            "text": subUnit
                        })

class DatasetAddDialog(BoxLayout):
    button = ObjectProperty()
    menu = None
    
    def closeMenu(self):
        self.menu.dismiss()

    def unitUpdate(self, button, unit):
        self.ids.measurementStandard.current_item = ""
        button.set_item(unit)
        self.validate()

    def validate(self):
        global controller
        self.button.disabled = (self.ids.datasetName.text == "" or 
                                self.ids.datasetName.text in controller.getDataSets() or 
                                not usefulFunctions.isIdentifier(self.ids.datasetName.text))
                                
    def buttonPress(self,button, buttonID):
        menu_items = []
        if buttonID == "measurementUnit":
            for Unit in controller.getConfigUnits():
                menu_items.append({
            "viewclass": "OneLineListItem",
            "text": Unit,
            "height": dp(40),
            "on_press": lambda x=f'{Unit}' : self.unitUpdate(button, x),
            "on_release": lambda : self.closeMenu()
        })
        elif buttonID == "measurementStandard" and self.ids.measurementUnit.current_item in controller.getConfigUnits():
            Unit = self.ids.measurementUnit.current_item
            if Unit in controller.getConfigUnits():
                for SubUnit in controller.getConfigSubUnits("%s" %Unit):
                    menu_items.append({
            "viewclass": "OneLineListItem",
            "text": SubUnit,
            "height": dp(40),
            "on_press": lambda x=f'{SubUnit}' : self.unitUpdate(button, x),
            "on_release": lambda : self.closeMenu()
        })
        else:
            return
        if self.menu:
            self.menu.dismiss()
        self.menu= MDDropdownMenu(
            items=menu_items,
            width_mult=3
        )
        self.menu.caller = button
        self.menu.open()
         
class ImportExcelFile(OneLineAvatarIconListItem):
    sheet = StringProperty()
    confirmButton = ObjectProperty(None)
    textbox = ObjectProperty(None)
    
    def setStatus(self, check):
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
    button = ObjectProperty()
    Path = StringProperty()
    
    def checkValidity(self, text):
        self.button.disabled = not (usefulFunctions.isIdentifier(text) or usefulFunctions.isIdentifier(text))

class OptionRow(OneLineIconListItem):
    icon = StringProperty()

class DatasetData(OneLineIconListItem):
    icon = StringProperty()
    menu = None
    dataGroupDialog = None
    dataGroupListDialog = None
    dataGroupExportDialog = None

    def exportDataGroups(self):
        global controller

        menu = None
        
        def closeDialog(button):
            self.dataGroupExportDialog.dismiss()
        
        def finishLoad(button):
            selectedDataGroups = []

            for item in self.dataGroupExportDialog.items:
                if item.ids.check.active:
                    selectedDataGroups.append(item.text)
            if(len(selectedDataGroups) > 0):
                file = filechooser.save_file(filters = [["Excel Spreadsheet", "*.xlsx"]])
                if file:
                    controller.exportDataGroups(file[0], self.text, selectedDataGroups)
            closeDialog(None)

        self.dataGroupExportDialog = MDDialog(
        title=f'Please select DataGroups to export from ({self.text})',
        type="confirmation",
        items = [SelectDataGroup(text=dataGroup) for dataGroup in controller.getDataGroups(self.text)],
        auto_dismiss=False,
        buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_press=closeDialog,
                ),
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_release=finishLoad,
                )
            ],
        )
        self.dataGroupExportDialog.open()

    def addDataGroup(self):
        global controller
        
        def closeDialog(button):
            self.dataGroupDialog.dismiss()

        def finishLoad(button):
            dataGroupName = self.dataGroupDialog.content_cls.ids.name.text
            Unit = self.dataGroupDialog.content_cls.ids.unit.current_item

            returnVal = controller.addDataGroup(self.text, dataGroupName, Unit)

            if returnVal > 0:
                Snackbar(text="Successfully Added DataGroup!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
            else:
                Snackbar(text="Could Not Add DataGroup!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
            closeDialog(None)

        button = MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_release=finishLoad,
                    disabled=True,
                )
        self.dataGroupDialog = MDDialog(
        title="Import data from dataset",
        type="custom",
        content_cls=AddDataGroup(button=button, dataSet=self.text),
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
        self.dataGroupDialog.open()

    def listDataGroups(self):
        global controller

        menu = None
        
        def closeDialog(button):
            self.dataGroupListDialog.dismiss()


        dataSet = self.text
        self.dataGroupListDialog = MDDialog(
        title=f'All DataGroups for the dataset ({self.text})',
        type="custom",
        content_cls=DataGroupList(),
        auto_dismiss=False,
        buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_press=closeDialog,
                ),
            ],
        )
        self.dataGroupListDialog.content_cls.ids.dataGroups.data = []
        for data in controller.getDataGroups(dataSet).keys():
            self.dataGroupListDialog.content_cls.ids.dataGroups.data.append({"viewclass":"OneLineListItem", "text":data, "on_release":lambda : None})
        self.dataGroupListDialog.open()

    def showMenu(self):

        def closeMenu():
            self.menu.dismiss()

        if not self.menu:
            menu_items = [{
                "viewclass": "OptionRow",
                "text": "Add DataGroup",
                "icon": "plus-thick",
                "height": dp(40),
                "width": dp(100),
                "on_press": lambda : self.addDataGroup(),
                "on_release": lambda : closeMenu()
            },
            {
                "viewclass": "OptionRow",
                "text": "List Datagroups",
                "icon": "format-list-bulleted",
                "height": dp(40),
                "width": dp(100),
                "on_press": lambda : self.listDataGroups(),
                "on_release": lambda : closeMenu()
            },
            {
                "viewclass": "OptionRow",
                "text": "List Datagroups",
                "icon": "file-export",
                "height": dp(40),
                "width": dp(100),
                "on_press": lambda : self.exportDataGroups(),
                "on_release": lambda : closeMenu()
            }
            ]
            self.menu = MDDropdownMenu(
                items=menu_items,
                width_mult=3,
            )    
        self.menu.caller = self
        self.menu.open()

class FileRow(OneLineIconListItem):
    icon = StringProperty()
    originalPath = StringProperty()
    dataDialog = None
    importDialog = None
    menu = None
    importDatasetDialog = None

    def deleteEntry(self):
        global controller

        def closeDialog(button):
            self.confirmDialog.dismiss()

        def confirm(button):
            val = controller.deleteFile(self.text)
            if val == 1:
                Snackbar(text="Successfully Deleted File!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
            else:
                Snackbar(text="Could not Delete File!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
            App.get_running_app().screen.list_files()
            closeDialog(None)

        self.confirmDialog = MDDialog(
        title="WARNING!",
        text="Warning! You are about to delete a sheet, are you sure?",
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

    def showData(self):
        global controller
        #dataFile = controller.getLoadedFile(self.text)["file"]
        #thread = Thread(target=tabloo.show, args=(dataFile,))
        #thread.start()
        #tabloo.show(dataFile)
        
        def closeDialog(button):
            self.dataDialog.dismiss()

        dataKey = self.text
        dataFile = controller.getLoadedFile(dataKey)
        rowList = []
        for i, row in dataFile.iterrows():
            thisRow = [i + 1]
            for val in row:
                thisRow.append(val)
            rowList.append(thisRow)
        self.dataDialog = MDDialog(
        title=f'Displaying {dataKey}',
        type="custom",
        content_cls=DataTableDisplay(),
        auto_dismiss=False,
        buttons=[
                MDFlatButton(
                    text="CLOSE",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_press=closeDialog
                )
            ],
        )
        dataFrame = MDDataTable(
            pos_hint = {},
            pos = self.dataDialog.pos,
            use_pagination=True,
            #rows_num=len(dataFile),
            column_data=[[usefulFunctions.column_string(i), dp(30)] for i in range(len(dataFile.columns) + 1)],
            row_data=rowList,
        )
        self.dataDialog.content_cls.clear_widgets()
        self.dataDialog.content_cls.add_widget(dataFrame)
        self.dataDialog.open()
    
    '''Create a drop down menu for any loaded file'''
    def createDropDown(self):
        if not self.menu:
            menu_items = [{
                "viewclass": "OptionRow",
                "text": "Display Sheet",
                "icon": "table-large",
                "height": dp(40),
                "on_press": lambda : self.showData(),
                "on_release": lambda : self.closeMenu()
            },
            {
                "viewclass": "OptionRow",
                "text": "Import Data",
                "icon": "database-import",
                "height": dp(40),
                "width": dp(120),
                "on_press": lambda : self.dataSetImportDialog(),
                "on_release": lambda : self.closeMenu()
            },
            {
                "viewclass": "OptionRow",
                "text": "Delete Sheet",
                "icon": "delete",
                "height": dp(40),
                "on_press": lambda : self.deleteEntry(),
                "on_release": lambda : self.closeMenu()
            }
            ]
            self.menu = MDDropdownMenu(
                items=menu_items,
                width_mult=3,
            )    
        self.menu.caller = self
        self.menu.open()

    def dataSetImportDialog(self):
        global controller
        
        def closeDialog(button):
            self.importDatasetDialog.dismiss()

        def finishLoad(button):
            title = self.importDatasetDialog.content_cls.ids.importName.text
            dataSet = self.importDatasetDialog.content_cls.ids.dataSet.current_item
            dataGroup = self.importDatasetDialog.content_cls.ids.dataGroup.current_item
            subUnit = self.importDatasetDialog.content_cls.ids.subUnit.current_item
            numRows = self.importDatasetDialog.content_cls.ids.numRows.text
            invalidID = self.importDatasetDialog.content_cls.ids.invalidID.text
            columnDates = self.importDatasetDialog.content_cls.ids.columnDates.text
            startRowDates = self.importDatasetDialog.content_cls.ids.startRowDates.text
            columnData = self.importDatasetDialog.content_cls.ids.columnData.text
            startRowData = self.importDatasetDialog.content_cls.ids.startRowData.text

            colData = usefulFunctions.column_string_to_int(columnData)
            colDate = usefulFunctions.column_string_to_int(columnDates)

            dataFrame = controller.getLoadedFile(self.text)

            data = dataFrame.iloc[range(int(startRowData), (int(startRowData)+int(numRows))), [int(colData)]]
            dates = dataFrame.iloc[range(int(startRowDates), int(startRowDates)+int(numRows)), [int(colData)]]


            retval = controller.dataToGroup(title, dataSet, dataGroup, subUnit, self.originalPath, data, dates)
            if retval:
                Snackbar(text="Data Successfully Imported!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
            else:
                Snackbar(text="Could not Import Data!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()


        button = MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_release=finishLoad,
                    disabled=True,
                )
        self.importDatasetDialog = MDDialog(
        title="Import data from dataset",
        type="custom",
        content_cls=ImportDatasetData(button=button, dataFrame=self.text),
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
        self.importDatasetDialog.open()

    '''Close the menu created when clicking a loaded sheet'''
    def closeMenu(self):
        self.menu.dismiss()

class FileList(Screen):

    importDialog = None
    importDialogExcel = None
    datasetDialog = None
    preferencesDialog = None
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
        """
        The saveFile function saves all loaded files to a specified HDF File.
        
        :param self: Used to Access the class attributes.
        :return: None.
        
        :doc-author: Trelent
        """
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
    
    def loadProject(self):
        """
        The loadProject function loads a project from the specified file.
        It does this by first clearing all of the current data, and then loading in new data from the HDF5 file.
        
        :param self: Used to Access the class attributes and methods.
        :return: A boolean value.
        
        :doc-author: Trelent
        """
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
            closeDialog(None)


        if not self.importDialog:
            button = MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=App.get_running_app().theme_cls.primary_color,
                        on_release=finishLoad,
                        disabled=True
                    )
            self.importDialog = MDDialog(
            title="Please select a name for the imported file",
            type="custom",
            content_cls=ImportFile(button=button),
            auto_dismiss=False,
            buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=App.get_running_app().theme_cls.primary_color,
                        on_press=closeDialog
                    ),
                    button
                ],
            )
        self.importDialog.content_cls.ids.fileLabel.text = f'Importing file {filePath}'
        self.importDialog.open()
    
    def showDatasetDialog(self):
        global controller


        def closeDialog(button):
            self.datasetDialog.dismiss()
            self.datasetDialog = None

        def finishLoad(button):
            datasetName = self.datasetDialog.content_cls.ids.datasetName

            retval = controller.addDataSet(datasetName.text)
            if retval == 0:
                Snackbar(text=f'Could not add dataset', snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
            else:
                Snackbar(text=f'Successfully added dataset', snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
            closeDialog(None)
            self.list_files()
            


        button = MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_press=finishLoad,
                    disabled=True,
                )
        self.datasetDialog = MDDialog(
        title="Create a new dataset",
        type="custom",
        content_cls=DatasetAddDialog(button=button),
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
        self.datasetDialog.open()
        
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
     
    def showPreferencesDialog(self):
        global controller

        def closeDialog(button):
            self.preferencesDialog.dismiss()
        
        self.preferencesDialog = MDDialog(
        title="Your Preferences",
        type="custom",
        content_cls=PreferencesMenu(),
        auto_dismiss=False,
        buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_press=closeDialog,
                ),
            ],
        )
        configUnits = controller.getConfigUnits()
        self.preferencesDialog.content_cls.ids.units.data = []
        for unit in configUnits:
            self.preferencesDialog.content_cls.ids.units.data.append(
                {
                    "viewclass": "PreferencesLine",
                    "text": unit,
                    "unit": unit,
                    "dialog": self.preferencesDialog
                })
        self.preferencesDialog.open()       
        
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
        self.list_datasets()
                
    
    def list_datasets(self):
        global controller
        
        def add_file(data):
            self.ids.datasetList.data.append(
                {
                    "viewclass": "DatasetData",
                    "text": f'{data}',
                    "icon": "atom",
                })
        self.ids.datasetList.data = []
        keys = controller.getDataSets().keys()
        for key in keys:
            add_file(key)

class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = FileList()
        self.exitDialog = None
        
    def on_request_close(self, *args, **kwargs):
        self.showExitDialog()
        return True
    
    def showExitDialog(self):
        global controller

        def closeDialog(button):
            self.exitDialog.dismiss()
            self.exitDialog = None

        def confirm(button):
            controller.doAutoSave()
            self.stop()
        
        
        if not self.exitDialog:
            self.exitDialog = MDDialog(
            title="WARNING!",
            text="Warning! Make sure you save your project before exiting!",
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
            self.exitDialog.open()

    def build(self):
        Window.bind(on_request_close=self.on_request_close)
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