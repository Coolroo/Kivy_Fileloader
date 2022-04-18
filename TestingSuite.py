from Controller import Controller, getFileType
import pandas as pd
import usefulFunctions

running = True
controller = Controller()

while running:
    print()
    print("Please input an option from the following:")
    print("N: Start a new Project")
    print("P: Load a project")
    print("S: Save the project")
    print("L: Load a new file")
    print("F: List loaded files")
    print("I: Load data from a loaded file")
    print("DS: Create a new DataSet")
    print("LDS: List all dataDets")
    print("G: Create a new DataGroup")
    print("LDG: List all datagroups in a dataset")
    print("E: Export datagroups from a dataset")
    print("*: Exit the program")
    print()

    inData = input()

    if(inData == "N"):
        controller.clearProject()
        print("Project Cleared")
    elif(inData == "P"):
        path = input("Please input the path to the project: ")
        if not controller.loadProject(path):
            print("Could not load project!")
        else:
            print("Successfully loaded project")
    elif(inData == "S"):
        path = input("Please input the path to the new HDF file: ")
        if controller.save(path):
            print("Successfully saved file")
        else:
            print("Could not save file")
    elif(inData == "L"):
        path = input("Please input the path to the file to load: ")
        filetype = getFileType(path)
        retval = 0
        if filetype == "csv":
            name = input("Please input the name for this file: ")
            if controller.loadFile(path, name):
                print("File successfully loaded!")
            else:
                print("Could not load file")
        elif filetype == "Excel":
            sheets = pd.ExcelFile(path).sheet_names
            print("Please select a sheet to import:")
            for sheet in sheets:
                print(sheet)
            print()
            sheet = input()
            if sheet not in sheets:
                print("This sheet does not exist in this excel file")
            else:
                name = input("Please input the name for this sheet: ")
                if controller.loadExcelSheet(path, sheet, name):
                    print("Successfully loaded sheet")
                else:
                    print("Could not load sheet")
        else:
            print("This is not a valid filetype")
    elif(inData == "F"):
        files = controller.getLoadedFiles()
        if len(files.keys()) < 1:
            print("No files to display")
        else:
            print("-----LOADED FILES-----")
            for file in files.keys():
                print(f'{files[file]["fileName"]}: {file}')
    elif(inData == "DS"):
        if controller.addDataSet(input("Please input the name for the new dataset: ")):
            print("Successfully added new dataset")
        else:
            print("Could not add a dataset")
    elif(inData == "G"):
        groupName = input("Please input the name of the new DataGroup: ")
        print("What dataset will this dataGroup be in?: ")
        for dataSet in controller.getDataSets().keys():
            print(dataSet)
        print()
        dataSet = input()
        if dataSet not in controller.getDataSets():
            print("This dataset does not exist")
        else:
            print("Please select a unit from the following: ")
            for unit in controller.getConfigUnits():
                print(unit)
            print()
            unit = input()
            if unit not in controller.getConfigUnits():
                print("This unit does not exist")
            else:
                if controller.addDataGroup(dataSet, groupName, unit):
                    print("Successfully added datagroup")
                else:
                    print("Could not add dataGroup")
    elif(inData == "I"):
        dataName = input("Input the title of the imported data: ")
        print("Please input which loaded file you'd like to import data from")
        for file in controller.getLoadedFiles().keys():
            print(file)
        print()
        fileName = input()
        if fileName not in controller.getLoadedFiles().keys():
            print("This file does not exist")
        else:
            print("Please select what DataSet to import to: ")
            for dataSet in controller.getDataSets().keys():
                print(dataSet)
            print()
            dataSet = input()
            if dataSet not in controller.getDataSets().keys():
                print("This DataSet does not exist")
            else:
                print("Please select a DataGroup to import to: ")
                for dataGroup in controller.getDataGroups(dataSet).keys():
                    print(dataGroup)
                print()
                dataGroup = input()
                if dataGroup not in controller.getDataGroups(dataSet).keys():
                    print("This dataGroup does not exist")
                else:
                    print("Please select the subUnit for the data:")
                    for subUnit in controller.getConfigSubUnits(controller.getDataGroup(dataSet, dataGroup)["unit"]):
                        print(subUnit)
                    print()
                    subUnit = input()
                    if subUnit not in controller.getConfigSubUnits(controller.getDataGroup(dataSet, dataGroup)["unit"]):
                        print("This is not a valid subUnit")
                    else:
                        numColumns = len(controller.getLoadedDataFrame(fileName).columns)
                        columns = [usefulFunctions.column_string(i+1) for i in range(numColumns)]
                        dateCol = input("Please input the column for the dates: ")
                        dataCol = input("Please input the column for the data: ")
                        if dateCol not in columns or dataCol not in columns:
                            print("Invalid Columns")
                        else:
                            startRow = input("Please input the starting row for the data: ")
                            numRows = input("Please input the number of data point to import: ")
                            lenRows = len(controller.getLoadedDataFrame(fileName))
                            validNumbers = (numRows.isdigit() and startRow.isdigit() and startRow.isdigit() and int(startRow) > 0 and int(startRow) > 0 and
                                            int(numRows) > 0 and int(startRow) + int(numRows) - 1 <= lenRows and 
                                            int(startRow) + int(numRows) - 1 > 0 and int(startRow) + int(numRows) - 1 <= lenRows and 
                                            int(startRow) + int(numRows) - 1 > 0)
                            if not validNumbers:
                                print("Invalid input, please select a valid start row/end row")
                            else:
                                dataFrame = controller.getLoadedFile(fileName)
                                dataCol = usefulFunctions.column_string_to_int(dataCol)
                                dateCol = usefulFunctions.column_string_to_int(dateCol)
                                data = dataFrame.iloc[range(int(startRow) - 1, (int(startRow)+int(numRows)) - 1), [int(dataCol)]]
                                dates = dataFrame.iloc[range(int(startRow) - 1, int(startRow)+int(numRows) - 1), [int(dateCol)]]
                                retval = controller.dataToGroup(dataSet, dataGroup, subUnit, f'{controller.getLoadedFile(fileName, False)["fileName"]} ({dataName})', [arr[0] for arr in data.to_numpy().tolist()], [arr[0] for arr in dates.to_numpy().tolist()])
                                if not retval:
                                    print("Could not import data")
                                else:
                                    print("Successfully imported data")
    elif(inData == "E"):
        path = input("Please input the path to the exported file (XLSX File): ")
        print("Please select a dataSet to export from: ")
        for dataSet in controller.getDataSets().keys():
            print(dataSet)
        print()
        dataSet = input()
        if dataSet not in controller.getDataSets():
            print("Input was not a valid dataSet")
        else:
            print("Select the dataGroups you would like to export, seperating their names with spaces: ")
            for dataGroup in controller.getDataGroups(dataSet).keys():
                print(dataGroup)
            print()
            dataGroups = input().split(" ")
            validGroups = []
            for dataGroup in dataGroups:
                if dataGroup not in controller.getDataGroups(dataSet).keys():
                    print(f'dataGroup {dataGroup} is not valid')
                else:
                    validGroups.append(dataGroup)
            if len(validGroups) == 0:
                print("No valid dataGroups to export")
            else:
                if controller.exportDataGroups(path, dataSet, validGroups):
                    print("Successfully exported dataGroups")
                else:
                    print("Could not export dataGroups")
    elif(inData == "*"):
        running = False
    elif(inData == "LDS"):
        print("---DATASETS---")
        for dataSet in controller.getDataSets().keys():
            print(dataSet)
        print()
    elif(inData == "LDG"):
        print("Please select a dataset: ")
        for dataSet in controller.getDataSets().keys():
            print(dataSet)
        print()
        dataSet = input()
        if dataSet not in controller.getDataSets():
            print("This is not a valid dataset")
        else:
            print("----DATA GROUPS----")
            for dataGroup in controller.getDataGroups(dataSet).keys():
                print(dataGroup)
            print()
    else:
        print(f'{inData} is not a valid command, please try again')

