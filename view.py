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

controller = Controller()
Builder.load_file('AppLayout.kv') 

class BulkImport(BoxLayout):
    '''The BulkImport class is used for a dialog created to import files in bulk'''
    button = ObjectProperty()
    dataSet = StringProperty()
    menu = None

    def validate(self):
        """
        The validate function ensures that all the data inputted into the dialog is correct, if the data is not correct it will disable the confirmation button
        
        :param self: Used to Access the class attributes and methods.
        
        :doc-author: Trelent
        """
        title = self.ids.title.text
        dataGroup = self.ids.dataGroup.current_item
        subUnit = self.ids.subUnit.current_item
        numRows = self.ids.numRows.text
        startRowDates = self.ids.startRowDates.text
        startRowData = self.ids.startRowData.text

        #if dataGroup in controller.getDataGroups(dataSet):
            #print(controller.getDataGroup(dataSet, dataGroup))

        validateDatasets = dataGroup not in controller.getDataGroups(self.dataSet) or subUnit not in controller.getConfigSubUnits(controller.getDataGroup(self.dataSet, dataGroup)["unit"])

        validNumbers = numRows.isdigit() and startRowDates.isdigit() and startRowData.isdigit() and int(numRows) > 0

        self.button.disabled = title == "" or validateDatasets or not validNumbers

    def setDropdownItem(self, dropdown, text):
        """
        The setDropdownItem function sets the text of a dropdown item and then validates the content of the dialog
        
        :param self: Used to Access the attributes and methods of the class in python.
        :param dropdown: Used to Specify the dropdown menu that is being modified.
        :param text: Used to Set the text of the dropdown item.
        """
        dropdown.set_item(text)
        self.menu.dismiss()
        self.menu = None
        self.validate()

    def showDataGroupMenu(self, caller):
        """
        The showDataGroupMenu function displays a dropdown menu of the data groups in the selected dataset.
        The function is called when a user clicks on the "Data Group" button, and it displays all of 
        the data groups for that dataset.
        
        :param self: Used to Access the attributes and methods of the class in python.
        :param caller: Used to Pass the widget that opened the menu to the callback.
        
        :doc-author: Trelent
        """
        global controller
        if self.dataSet not in controller.getDataSets():
            return
        if self.menu:
            self.menu.dismiss()
        menu_items = []
        for dataCategory in controller.getDataGroups(self.dataSet):
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
        """
        The showUnitMenu function is used to create a dropdown menu for the user to select which unit they would like the imported data to use.
        The function takes in the caller (DropdownItem) as an argument and uses that information to determine what data group is currently selected.
        If there is no current data group selected, then nothing happens. If there is a current data group selected, 
        then it checks if that particular unit has subunits or not by calling getConfigSubUnits on the controller module. 
        If it does have subunits, then those are added as options in the dropdown menu with their names being their respective units.
        
        :param self: Used to Access the class attributes.
        :param caller: Reference to the DropdownItem that called this
        
        :doc-author: Trelent
        """
        if self.ids.dataGroup.current_item not in controller.getDataGroups(self.dataSet):
            return
        if self.menu:
            self.menu.dismiss()
            self.menu = None
        menu_items = []
        for Unit in controller.getConfigSubUnits(controller.getDataGroups(self.dataSet)[self.ids.dataGroup.current_item]["unit"]):
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

class SelectDataGroup(OneLineAvatarIconListItem):
    '''The SelectDataGroup class is used to list datagroups to select in a dialog'''
    divider = None

    def set_icon(self, instance):
        """
        Enables/disables the checkmark
        
        :param self: Used to Access the attributes and methods of the class in python.
        :param instance: Used to Pass the widget that called the function.
        
        :doc-author: Trelent
        """
        instance.active = not instance.active

class DataGroupList(BoxLayout):
    '''The DataGroupList class is used to display a list of all the datagroups in a dataset'''
    pass

class ImportDatasetData(BoxLayout):
    button = ObjectProperty()
    dataFrame = StringProperty()
    menu = None

    def validate(self):
        """
        The validate function checks to see if all of the fields are filled out correctly and that they contain valid data. 
        
        :param self: Used to Access the class attributes and methods.
        
        :doc-author: Trelent
        """
        title = self.ids.title.text
        dataSet = self.ids.dataSet.current_item
        dataGroup = self.ids.dataGroup.current_item
        subUnit = self.ids.subUnit.current_item
        numRows = self.ids.numRows.text
        columnDates = self.ids.columnDates.text
        startRowDates = self.ids.startRowDates.text
        columnData = self.ids.columnData.text
        startRowData = self.ids.startRowData.text

        #if dataGroup in controller.getDataGroups(dataSet):
            #print(controller.getDataGroup(dataSet, dataGroup))

        validateDatasets = dataSet not in controller.getDataSets() or dataGroup not in controller.getDataGroups(dataSet) or subUnit not in controller.getConfigSubUnits(controller.getDataGroup(dataSet, dataGroup)["unit"])

        lenRows = len(controller.getLoadedDataFrame(self.dataFrame))
        validNumbers = (numRows.isdigit() and startRowDates.isdigit() and startRowData.isdigit() and int(startRowData) > 0 and int(startRowDates) > 0 and
        int(numRows) > 0 and int(startRowData) + int(numRows) - 1 <= lenRows and 
        int(startRowData) + int(numRows) - 1 > 0 and int(startRowDates) + int(numRows) - 1 <= lenRows and 
        int(startRowDates) + int(numRows) - 1 > 0)

        numColumns = len(controller.getLoadedDataFrame(self.dataFrame).columns)
        columns = [usefulFunctions.column_string(i+1) for i in range(numColumns)]
        validColumns = title == "" or columnDates in columns and columnData in columns 
        #print(f'columnData = {columnData}, "columnNames = {str(controller.getLoadedDataFrame(self.dataFrame).columns)}')
        #print(f'validateDatasets = {validateDatasets}, validNumbers = {validNumbers}, validColumns = {validColumns}')
        self.button.disabled = validateDatasets or not validNumbers or not validColumns


    def setDropdownItem(self, dropdown, text):
        """
        The setDropdownItem function sets the text of a dropdown menu, and then validates the inputs
        
        :param self: Used to Access the class attributes.
        :param dropdown: Used to Specify the dropdown menu that will be used.
        :param text: Used to Set the text of the dropdown item.
        
        :doc-author: Trelent
        """
        dropdown.set_item(text)
        self.menu.dismiss()
        self.menu = None
        self.validate()

    def showDataSetMenu(self, caller):
        """
        The showDataSetMenu function displays a dropdown menu of all the data sets that are currently loaded into the program. 
        The user can select one of these data sets.
        
        :param self: Used to Access the instance of the class that is currently executing.
        :param caller: Used to Pass the name of the data set to be used.
        
        :doc-author: Trelent
        """
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
        """
        The showDataGroupMenu function is called when the user selects a data set from the dropdown menu. 
        It then displays all of the data groups that are associated with that particular dataset.
        
        :param self: Used to Access the attributes and methods of the class in python.
        :param caller: Used to Pass the widget that triggered the menu to be created.
        :return: A dictionary of the items that are in the data group dropdown menu.
        
        :doc-author: Trelent
        """
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
        """
        The showUnitMenu function displays a dropdown menu of the subunits that are available for the current data group.
        The function is called when a user clicks on the "Sub-Unit" button in the Unit screen.
        
        :param self: Used to Access the attributes and methods of the class in which it is used.
        :param caller: Used to Pass the name of the currently selected unit to the callback function.
        :return: A list of dictionaries that contain the unit names.
        
        :doc-author: Trelent
        """
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
    '''The AddDataGroup is used in a dialog to create a new DataGroup'''
    button = ObjectProperty()
    dataSet = StringProperty()
    menu = None

    def validate(self):
        """
        The validate function checks the data for errors and disables the confirmation button.
        
        :param self: Used to Refer to the object that is calling the method.
        :return: A dictionary of the form:.
        
        :doc-author: Trelent
        """
        self.button.disabled = not usefulFunctions.isIdentifier(self.ids.name.text) or  self.ids.name.text in controller.getDataSets()[self.dataSet]

    def setDropdownItem(self, dropdown, text):
        """
        The setDropdownItem function sets the text of a dropdown menu, and then validates the dialog inputs.
        
        :param self: Used to Access the class attributes.
        :param dropdown: Used to Specify the dropdown menu that is being modified.
        :param text: Used to Set the text of the dropdown item.
        :return: The dropdown widget.
        
        :doc-author: Trelent
        """
        dropdown.set_item(text)
        self.menu.dismiss()
        self.menu = None
        self.validate()

    def showUnitMenu(self, caller):
        """
        The showUnitMenu function displays a dropdown menu of the available units.
        The function is called when the user clicks on the Unit button.
        
        :param self: Used to Access the attributes and methods of the class.
        :param caller: Used to Pass the name of the unit to be set.
        :return: A list of menu items.
        
        :doc-author: Trelent
        """
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

class DataTableDisplay(BoxLayout):
    '''The DataTableDisplay class is used to display a datatable in a dialog'''
    pass

#These Classes are not used as they were not implemented, could be used in the future though
'''class SubunitDialog(BoxLayout):
    The SubUnit Dialog 
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
                        })'''

class DatasetAddDialog(BoxLayout):
    '''The DatasetAddDialog class is used to create a new dataset in a dialog'''
    button = ObjectProperty()
    menu = None
    
    def closeMenu(self):
        """
        The closeMenu function closes the menu.
        
        :param self: Used to Access variables that belongs to the class.
        :return: The value of the variable self.
        
        :doc-author: Trelent
        """
        self.menu.dismiss()

    def unitUpdate(self, button, unit):
        """
        The unitUpdate function is called when the user selects a different unit from the dropdown menu. 
        It sets the current_item of measurementStandard to an empty string, and then it validates the dialog items
        
        :param self: Used to Access the class variables.
        :param button: Used to Identify which button was pressed.
        :param unit: Used to Determine which unit button was pressed.
        :return: The current item of the measurementstandard dropdown.
        
        :doc-author: Trelent
        """
        self.ids.measurementStandard.set_item("")
        button.set_item(unit)
        self.validate()

    def validate(self):
        """
        The validate function checks to make sure that the user has entered a valid dataset name. 
        It also checks to make sure that the dataset does not already exist in the controller.
        
        :param self: Used to Access the attributes and methods of the class in python.
        :return: A boolean value.
        
        :doc-author: Trelent
        """
        global controller
        self.button.disabled = (self.ids.datasetName.text == "" or 
                                self.ids.datasetName.text in controller.getDataSets() or 
                                not usefulFunctions.isIdentifier(self.ids.datasetName.text))
                                
    def buttonPress(self,button, buttonID):
        """
        The buttonPress function is called when a button is pressed. It takes the button that was pressed as an argument, and uses it to determine what menu should be displayed. 
        If the measurementUnit or measurementStandard buttons are pressed, then a list of units/standards will be displayed in a dropdown menu. 
        The function also calls unitUpdate
        
        :param self: Used to Access the class attributes.
        :param button: Used to Determine which button was pressed.
        :param buttonID: Used to Determine which button was pressed and what function to call.
        :return: The menu_items list.
        
        :doc-author: Trelent
        """
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
    '''The ImportExcelFile class is used when importing an aexcel file, and acts as an item of the dropdown menu'''
    sheet = StringProperty()
    confirmButton = ObjectProperty(None)
    textbox = ObjectProperty(None)
    
    def setStatus(self, check):
        """
        The setStatus function sets the active attribute of a checkbox to the opposite of its current value.
        
        :param self: Used to Access the attributes and methods of the class in python.
        :param check: Used to Set the active property of the checkbox to true or false.
        :return: The opposite of the current state of the checkbox.
        
        :doc-author: Trelent
        """
        check.active = not check.active
        
        self.checkValidity(check)
        
    def checkValidity(self, check):
        """
        The checkValidity function checks to see if the user has entered a valid option for each checkbox in the group.
        If they have, it returns True, otherwise it returns False.
        
        :param self: Used to Access the attributes and methods of the class in python.
        :param check: Used to Check if the user has selected a valid option.
        :return: A boolean value.
        
        :doc-author: Trelent
        """
        validOption = False
        check_list = check.get_widgets(check.group)
        for ch in check_list:
            if ch.active:
                validOption = validOption or usefulFunctions.isIdentifier(ch.textbox.text)
        
        self.confirmButton.disabled = not validOption
        
class TooltipLeftIconWidget(IconLeftWidget, MDTooltip):
    '''The TooltipLeftIconWidget is used to display a tooltip on an icon'''
    pass

class ImportFile(BoxLayout):
    '''The ImportFile class is used to import CSV files in a dialog'''
    button = ObjectProperty()
    Path = StringProperty()
    
    def checkValidity(self):
        """
        The checkValidity function checks if the name provided is a valid 
        
        :param self: Used to Access the class attributes.
        :param text: Used to Check if the input is valid.
        
        :doc-author: Trelent
        """
        self.button.disabled = not (usefulFunctions.isIdentifier(self.ids.dialogTextBox.text) and self.ids.dialogTextBox.text not in controller.getLoadedFiles())

class OptionRow(OneLineIconListItem):
    '''This is used in menus to display an option'''
    icon = StringProperty()

class DatasetData(OneLineIconListItem):
    '''The DatasetData class is used as an item in the main display, it is used in the Datasets column'''
    icon = StringProperty()
    menu = None
    dataGroupDialog = None
    dataGroupListDialog = None
    dataGroupExportDialog = None
    deleteDataGroupsDialog = None
    bulkImportDialog = None
    bulkFilesDialog = None

    def getBulkFiles(self):
        """
        The getBulkFiles function is used to get a list of files from the user. 
        This is done by creating a dialog box that allows the user to select multiple files and then passing those selected files into the bulkImport function.
        
        :param self: Used to Access the class variables and methods.
        :return: A dialog that allows the user to select multiple files from a list of loaded files.
        
        :doc-author: Trelent
        """
        global controller
        
        def closeDialog(button):
            self.bulkFilesDialog.dismiss()
        
        def finishLoad(button):
            selectedFiles = []

            for item in self.bulkFilesDialog.items:
                if item.ids.check.active:
                    selectedFiles.append(item.text)
            if(len(selectedFiles) > 0):
                #print(selectedFiles)
                self.bulkImport(selectedFiles)
            closeDialog(None)

        self.bulkFilesDialog = MDDialog(
        title=f'Please select Loaded Files to import from',
        type="confirmation",
        items = [SelectDataGroup(text=file) for file in controller.getLoadedFiles().keys()],
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
        self.bulkFilesDialog.open()

    def bulkImport(self, loadedFiles):
        """
        The bulkImport function is used to import data from loadedFiles into the current dataset
        It takes in a list of file names, and then allows the user to select which columns contain the dates and data.
        The function will then iterate through each file, and for each file it will add an entry to the database with that filename as well as all of its corresponding dates/data points.
        It then brings this data into the DataGroup.
        
        :param self: Used to Access the class attributes and methods.
        :param loadedFiles: Used to Pass in the list of files that were loaded from the filechooser.
        :return: The number of selections that were successfully imported.
        
        :doc-author: Trelent
        """
        global controller
        
        def closeDialog(button):
            self.bulkImportDialog.dismiss()

        def finishLoad(button):
            #title = self.bulkImportDialog.content_cls.ids.importName.text
            title = self.bulkImportDialog.content_cls.ids.title.text
            dataGroup = self.bulkImportDialog.content_cls.ids.dataGroup.current_item
            subUnit = self.bulkImportDialog.content_cls.ids.subUnit.current_item
            numRows = self.bulkImportDialog.content_cls.ids.numRows.text
            columnDates = self.bulkImportDialog.content_cls.ids.columnDates.text
            startRowDates = int(self.bulkImportDialog.content_cls.ids.startRowDates.text) - 1
            columnData = self.bulkImportDialog.content_cls.ids.columnData.text
            startRowData = int(self.bulkImportDialog.content_cls.ids.startRowData.text) - 1

            colData = usefulFunctions.column_string_to_int(columnData)
            colDate = usefulFunctions.column_string_to_int(columnDates)
            retval = 0
            for file in loadedFiles:
                try:
                    realFile = controller.getLoadedFile(file, False)
                    dataFrame = realFile["file"]
                    
                    data = dataFrame.iloc[range(int(startRowData), int(startRowData)+int(numRows)), [int(colData)]]
                    dates = dataFrame.iloc[range(int(startRowDates), int(startRowDates)+int(numRows)), [int(colDate)]]

                    retval += controller.dataToGroup(self.text, dataGroup, subUnit, f'{realFile["fileName"]} ({title})', [arr[0] for arr in data.to_numpy().tolist()], [arr[0] for arr in dates.to_numpy().tolist()])
                except:
                    pass
            if retval:
                Snackbar(text=f'Successfully imported {retval}/{len(loadedFiles)} Selections', snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
            else:
                Snackbar(text="Could not Import Data!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
            closeDialog(None)


        button = MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=App.get_running_app().theme_cls.primary_color,
                    on_release=finishLoad,
                    disabled=True,
                )
        self.bulkImportDialog = MDDialog(
        title="Import data from dataset",
        type="custom",
        content_cls=BulkImport(button=button, dataSet=self.text),
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
        self.bulkImportDialog.open()

    def deleteDataGroups(self):
        """
        The deleteDataGroups function is used to delete a data group from the specified dataSet.
        It will display a dialog box that allows the user to select which data groups they would like to delete.
        
        :param self: Used to Access the class variables.
        :return: The mddialog object that is used to display the deletedatagroups dialog.
        
        :doc-author: Trelent
        """
        global controller
        
        def closeDialog(button):
            self.deleteDataGroupsDialog.dismiss()
        
        def finishLoad(button):
            selectedDataGroups = []
            successes = 0

            for item in self.deleteDataGroupsDialog.items:
                if item.ids.check.active:
                    selectedDataGroups.append(item.text)
            if(len(selectedDataGroups) > 0):
                for dataGroup in selectedDataGroups:
                    successes += controller.deleteDataGroup(self.text, dataGroup)
                Snackbar(text=f'Successfully Deleted {successes}/{len(selectedDataGroups)} DataGroups!', snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
            else:
                Snackbar(text="No Datagroups Selected!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
            closeDialog(None)

        self.deleteDataGroupsDialog = MDDialog(
        title=f'Please select DataGroups to delete from ({self.text})',
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
        self.deleteDataGroupsDialog.open()

    def exportDataGroups(self):
        """
        The exportDataGroups function exports the selected data groups from a given dataset.
        
        :param self: Used to Access the class variables.
        :return: A dialog that allows the user to select which data groups they would like to export from a given site.
        
        :doc-author: Trelent
        """
        global controller
        
        def closeDialog(button):
            self.dataGroupExportDialog.dismiss()
        
        def finishLoad(button):
            selectedDataGroups = []

            for item in self.dataGroupExportDialog.items:
                if item.ids.check.active:
                    selectedDataGroups.append(item.text)
            if(len(selectedDataGroups) > 0):
                file = filechooser.save_file(filters = [["Excel Spreadsheet", "*.xlsx", "*.XLSX"]])
                if file:
                    if controller.exportDataGroups(file[0], self.text, selectedDataGroups):
                        Snackbar(text=f'Successfully Exported DataGroups!', snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
                    else:
                        Snackbar(text=f'Could not Export DataGroups!', snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
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
        """
        The addDataGroup function is used to add a new data group to the current dataset.
        It takes in the name of the dataset.
        
        :param self: Used to Access the class attributes.
        :return: The dialog that is used to add data groups.
        
        :doc-author: Trelent
        """
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
        """
        The listDataGroups function displays a list of all the data groups for a given dataset.
        
        :param self: Used to Access the attributes and methods of the class in python.
        :return: A list of all the data groups for a given dataset.
        
        :doc-author: Trelent
        """
        global controller
        
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
        """
        The showMenu function displays a dropdown menu when the user clicks on the Dataset Row.
        The menu contains options to add, delete, and list data groups.
        
        :param self: Used to Access the attributes and methods of the class in python.
        :return: A mddropdownmenu object.
        
        :doc-author: Trelent
        """
        def closeMenu():
            self.menu.dismiss()

        if not self.menu:
            menu_items = [{
                "viewclass": "OptionRow",
                "text": "Add DataGroup",
                "icon": "plus-thick",
                "height": dp(40),
                "on_press": lambda : self.addDataGroup(),
                "on_release": lambda : closeMenu()
            },
            {
                "viewclass": "OptionRow",
                "text": "List Datagroups",
                "icon": "format-list-bulleted",
                "height": dp(40),
                "on_press": lambda : self.listDataGroups(),
                "on_release": lambda : closeMenu()
            },
            {
                "viewclass": "OptionRow",
                "text": "Bulk Import",
                "icon": "database-import",
                "height": dp(40),
                "on_press": lambda : self.getBulkFiles(),
                "on_release": lambda : closeMenu()
            },
            {
                "viewclass": "OptionRow",
                "text": "Export Datagroups",
                "icon": "file-export",
                "height": dp(40),
                "on_press": lambda : self.exportDataGroups(),
                "on_release": lambda : closeMenu()
            },
            {
                "viewclass": "OptionRow",
                "text": "Delete DataGroup",
                "icon": "delete",
                "height": dp(40),
                "on_press": lambda : self.deleteDataGroups(),
                "on_release": lambda : closeMenu()
            },
            ]
            self.menu = MDDropdownMenu(
                items=menu_items,
                width_mult=3.75,
            )    
        self.menu.caller = self
        self.menu.open()

class FileRow(OneLineIconListItem):
    '''The FileRow class is used to display all the loaded files in the left column of the program'''
    icon = StringProperty()
    originalPath = StringProperty()
    dataDialog = None
    importDialog = None
    menu = None
    importDatasetDialog = None

    def deleteEntry(self):
        """
        The deleteEntry function is used to delete a file from the database. It is called when the user clicks on the delete button in a list item.
        
        :param self: Used to Access the attributes and methods of the class in python.
        :return: A confirmation dialog.
        
        :doc-author: Trelent
        """
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
        """
        The showData function displays the data in a dataframe, in a dialog box.
        It takes as input the key of the file that is to be displayed, and displays it in a table format.
        
        :param self: Used to Access the class attributes and methods.
        :return: The data in the selected file.
        
        :doc-author: Trelent
        """
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

    def dataSetImportDialog(self):
        """
        The dataSetImportDialog function is used to create a dialog box that allows the user to import data from a loaded file, and puts it into a datagroup.
        The function takes no parameters and returns nothing.
        
        :param self: Used to Access the attributes and methods of the class in python.
        :return: The dialog that allows the user to import data from a dataset.
        
        :doc-author: Trelent
        """
        global controller
        
        def closeDialog(button):
            self.importDatasetDialog.dismiss()

        def finishLoad(button):
            title = self.importDatasetDialog.content_cls.ids.dataGroup.text
            dataSet = self.importDatasetDialog.content_cls.ids.dataSet.current_item
            dataGroup = self.importDatasetDialog.content_cls.ids.dataGroup.current_item
            subUnit = self.importDatasetDialog.content_cls.ids.subUnit.current_item
            numRows = self.importDatasetDialog.content_cls.ids.numRows.text
            columnDates = self.importDatasetDialog.content_cls.ids.columnDates.text
            startRowDates = self.importDatasetDialog.content_cls.ids.startRowDates.text
            columnData = self.importDatasetDialog.content_cls.ids.columnData.text
            startRowData = self.importDatasetDialog.content_cls.ids.startRowData.text
            try:
                colData = usefulFunctions.column_string_to_int(columnData)
                colDate = usefulFunctions.column_string_to_int(columnDates)
                realFile = controller.getLoadedFile(self.text, False)
                dataFrame = realFile["file"]
                #print(realFile)

                data = dataFrame.iloc[range(int(startRowData) - 1, (int(startRowData)+int(numRows)) - 1), [int(colData)]]
                dates = dataFrame.iloc[range(int(startRowDates) - 1, int(startRowDates)+int(numRows) - 1), [int(colDate)]]
                #print(data)

                #for index, row in data.iterrows():
                    #print(row)
                retval = controller.dataToGroup(dataSet, dataGroup, subUnit, f'{realFile["fileName"]} ({title})', [arr[0] for arr in data.to_numpy().tolist()], [arr[0] for arr in dates.to_numpy().tolist()])
                if retval:
                    Snackbar(text="Data Successfully Imported!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
                else:
                    Snackbar(text="Could not Import Data!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
            except:
                Snackbar(text="Could not Import Data!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
            closeDialog(None)


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
    
    def createDropDown(self):
        """
        The createDropDown function creates a dropdown menu for the user to select from. 
        The function takes no parameters and returns nothing. The function creates a list of options that the user can choose from, 
        and then displays them in a dropdown menu.
        
        :param self: Used to Access the class attributes and methods.
        :return: A mddropdownmenu object.
        
        :doc-author: Trelent
        """
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
                width_mult=3.5,
            )    
        self.menu.caller = self
        self.menu.open()

    '''Close the menu created when clicking a loaded sheet'''
    def closeMenu(self):
        self.menu.dismiss()

class FileList(Screen):
    '''The FileList class is used as the main display, and all the modules are displayed through this class'''

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
        file = filechooser.open_file(filters = [["Data Files (csv, xls, xlsx)", "*.xls", "*.csv", "*.xlsx", "*.XLS", "*.CSV", "*.XLSX"]])
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
        file = filechooser.save_file(filters = [["HDF File", "*.hdf", "*.HDF"]])
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
        file = filechooser.open_file(filters = [["HDF File (*.hdf)", "*.hdf", "*.HDF"]])
        if file:
            returnVal = controller.loadProject(file[0])
            if returnVal:
                Snackbar(text="Successfully Loaded Project!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
            else:
                Snackbar(text="Could not Load Project!", snackbar_x=dp(3), snackbar_y=dp(10), size_hint_x=0.5, duration=1.5).open()
        self.list_files()

    def showImportDialog(self, filePath):
        """
        The showImportDialog function displays a dialog box that allows the user to import a file into the program.
        The function takes one parameter, which is the path of an existing file. The function returns nothing.
        
        :param self: Used to Reference the class instance itself.
        :param filePath: Used to Pass the file path of the file that is being imported.
        :return: The mddialog object.
        
        :doc-author: Trelent
        """
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
        """
        The showDatasetDialog function displays a dialog box that allows the user to create a new dataset.
        The function takes no parameters and returns nothing. 
        
        :param self: Used to Access the attributes and methods of the class in python.
        :return: A dialog that allows the user to create a new dataset.
        
        :doc-author: Trelent
        """
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
        """
        The showImportDialogExcel function displays a dialog box that allows the user to select which sheets they would like to import from an Excel file. 
        The function returns nothing, but it does call the loadExcelSheet function on each sheet that is selected by the user.
        
        :param self: Used to Access the class attributes.
        :param filePath: Used to Load the file.
        :param sheets: Used to Pass the names of the sheets in a workbook.
        :return: The mddialog object that is created.
        
        :doc-author: Trelent
        """
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
     
     #More Preferences Menu stuff that was left unused
    '''def showPreferencesDialog(self):
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
        self.preferencesDialog.open()       '''
        
    def list_files(self):
        """
        The list_files function redisplays all the loaded files in the left column of the program, and reloads all the datasets afterwards
        
        :param self: Used to Access the class attributes.
        :return: A list of dictionaries that contain the file name and icon for each file in the loaded files dictionary.
        
        :doc-author: Trelent
        """
        global controller
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
        """
        The list_datasets function displays a list of datasets in the current project.
        
        :param self: Used to Access the class attributes.
        :return: A list of datasets in the current controller.
        
        :doc-author: Trelent
        """
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

class MVCApp(MDApp):
    '''The MVCApp class is the main app'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = FileList()
        self.exitDialog = None
        
    def on_request_close(self, *args, **kwargs):
        """
        The on_request_close function is called when the user closes the Appliocation
        It prompts the user if they would like to close the app
        
        :param self: Used to Access the attributes and methods of the class in python.
        :param *args: Used to Pass a non-keyworded, variable-length argument list.
        :param **kwargs: Used to Catch any additional keyword arguments that are passed to the function.
        
        :doc-author: Trelent
        """
        self.showExitDialog()
        return True
    
    def showExitDialog(self):
        """
        The showExitDialog function is used to display a dialog box when the user attempts to exit the application. The function takes no parameters and returns nothing.
        
        
        :param self: Used to Access the attributes and methods of the class in python.
        :return: The exitdialog object.
        
        :doc-author: Trelent
        """
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
        """
        The build function is the main function that is called when a Kivy application starts. 
        
        :param self: Used to Access the attributes and methods of the class in python.
        
        :doc-author: Trelent
        """
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
        """
        The on_start function is called once when the app starts
        
        :param self: Used to Access to the attributes and methods of the class
        
        :doc-author: Trelent
        """
        self.screen.list_files()

    
    def loadMenu(self, button):
        """
        The loadMenu function is used to open the dropdown menu for the main application
        
        :param self: Used to Access the attributes and methods of the class in python.
        :param button: The option button
        
        :doc-author: Trelent
        """
        self.menu.caller = button
        self.menu.open()

    def closeMenu(self):
        """
        The closeMenu function closes the menu.
        
        :param self: Used to Access variables that belongs to the class.
        :return: The string "menu closed".
        
        :doc-author: Trelent
        """
        self.menu.dismiss()
        
    def clearProject(self):
        """
        The clearProject function clears the project of all files and datasets
        
        :param self: Used to Access variables, methods and functions that belongs to the class.
        
        :doc-author: Trelent
        """
        self.confirmationDialog()
    
    def confirmationDialog(self):
        """
        The confirmationDialog function is used to display a dialog box that will confirm the user's choice before proceeding with clearing the project.
        
        :param self: Used to Access the attributes and methods of the class in python.
        
        :doc-author: Trelent
        """
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


MVCApp().run()