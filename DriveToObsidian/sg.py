import quickstart
import os
import json
from PySimpleGUI import PySimpleGUI as sg
# import PySimpleGUI as sg

current_directory = os.getcwd()

local_folder = os.path.join(current_directory, "temp")
dataFile = os.path.join(os.path.dirname(current_directory), "data.json")

with open(dataFile, 'r') as file:
    data = json.load(file)


sg.LOOK_AND_FEEL_TABLE['MyCreatedTheme'] = {'BACKGROUND': '#1E1E1E',
                                        'TEXT': '#FFFFFF',
                                        'INPUT': '#262626',
                                        'TEXT_INPUT': '#FFFFFF',
                                        'SCROLL': '#99CC99',
                                        'BUTTON': ('#FFFFFF', '#3026BB'),
                                        'PROGRESS': ('#D1826B', '#CC8019'),
                                        'BORDER': 1, 'SLIDER_DEPTH': 0,
'PROGRESS_DEPTH': 0, }

sg.theme("MyCreatedTheme")


names = quickstart.main()
tags = data["userTags"]
selected = ''
selected_tags = []

layout = [[sg.Text('Sync Notebook')],
          [sg.Input(size=(20, 1), enable_events=True, key='-INPUT-')],
          [sg.Listbox(names, size=(20, 4), enable_events=True, key='-LIST-')],
          [sg.Button('Cancel'), sg.Button('Sync')]]

tagLayout = [
    [sg.Text('Choose tags')],
    [sg.Listbox(tags, size=(20, 4), enable_events=True, key='-LIST-')],
    [sg.Text('Currently Selected:')],
    [sg.Listbox(selected_tags, size=(20, 4), enable_events=True, key='-TAGS-')],
    [sg.Button('Confirm')]
]

window = sg.Window('Sync Notebook', layout)

tagWindow = sg.Window('Select Tags', tagLayout)


def setTags(index):


    #Reset selected Tags
    data["tags"] = []
    with open(dataFile, 'w') as file:
        json.dump(data, file, indent = 4)


    while True:
        event, values = tagWindow.read()

        if event == sg.WIN_CLOSED:
            break
        elif event == '-LIST-':
            selected_tag = values['-LIST-'][0]  # Assuming only one tag can be selected at a time
            if selected_tag in selected_tags:
                selected_tags.remove(selected_tag)
            else:
                selected_tags.append(selected_tag)

            tagWindow['-LIST-'].update(set(tags))
            tagWindow['-TAGS-'].update(set(selected_tags))
        if event in ('Confirm'):
            #print(dataFile)

            # Update the existing data with new data (selected_tags in your case)
            if "tags" not in data:
                data["tags"] = []
            data["tags"] = selected_tags

            # Write the updated data back to the file
            with open(dataFile, 'w') as file:
                json.dump(data, file, indent=4)
                print('data written.')
            tagWindow.close()
            print('Windows closed')
            quickstart.getFiles(index, local_folder)  # Pass both index and local_folder


# Event Loop
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    if event in ('Sync'):

        print(dataFile)

        if selected == '':
            sg.popup('Choose a folder')
        else:

            index = names.index(selected)
            print(index)
            if data["automaticallyTag"] == True:
                window.close()
                setTags(index)
            else:
                window.close()
                quickstart.getFiles(index, local_folder)  # Pass both index and local_folder
            break

    if values['-INPUT-'] != '' and selected == '':
        search = values['-INPUT-']
        new_values = [x for x in names if search in x]
        window['-LIST-'].update(new_values)
    else:
        window['-LIST-'].update(names)
    if event == '-LIST-' and len(values['-LIST-']):
        selected = str(values['-LIST-']).replace("[", "").replace("]", "").replace("'", "")
        window['-INPUT-'].update(values['-LIST-'])

window.close()
