import os
import subprocess
import re
import shutil

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import customtkinter
import sv_ttk
import sys
import configparser

from tkinter import filedialog


class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.config(state=tk.NORMAL)
        self.widget.insert(tk.END, str, (self.tag,))
        self.widget.see(tk.END)
        self.widget.config(state=tk.DISABLED)
        self.widget.update()
        root.update()

    def flush(self):
        pass


# Make a config parser
config = configparser.ConfigParser()

# Read the config file if it exists
if os.path.isfile('config.ini'):
    config.read('config.ini')
else:
    # If it doesn't exist, create it with default values
    config['Folders'] = {'mod_folder': '',
                         'language_folder': '', 'output_folder': '', 'game': 'Persona 5 Royal'}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# Get the saved values or set default values if they don't exist
mod_folder = config.get('Folders', 'mod_folder', fallback='')
language_folder = config.get('Folders', 'language_folder', fallback='')
output_folder = config.get('Folders', 'output_folder', fallback='')
game = config.get('Folders', 'game', fallback='Persona 5 Royal')

root = customtkinter.CTk()


def disable_button():
    run_button.config(state="disabled")


def enable_button():
    run_button.config(state="normal")


# Log box with scrollbar and no text editing
log_box = tk.Text(root, height=20, width=50)
log_box.grid(row=5, columnspan=3, column=0, sticky='ew')
# use columnspan to make the widget span multiple columns
# log_box.grid(columnspan=2)
# Create a scrollbar and associate it with log_box
scrollbar = ttk.Scrollbar(root, command=log_box.yview)
scrollbar.grid(row=5, column=4, sticky='ns')
# Disable editing
log_box.config(state=tk.DISABLED, yscrollcommand=scrollbar.set)


sys.stdout = TextRedirector(log_box, "stdout")


def on_select(event):
    # Make the variable global so it can be used
    global game
    game = dropdown.get()
    # Clear the log box
    log_box.config(state=tk.NORMAL)
    log_box.delete('1.0', tk.END)
    log_box.config(state=tk.DISABLED)
    print(f"Game: {game}")


# Options for the dropdown
options = ["Persona 5 Royal", "Persona 5"]

# Make the dropdown
dropdown = ttk.Combobox(root, values=options)

# Check if the saved value in the config file exists in the options list
if game in options:
    # Set the saved value in the config file as the default option
    dropdown.current(options.index(game))
else:
    dropdown.current(0)

# Disable write in the dropdown
dropdown.configure(state="readonly")

# Add the on_select function to the dropdown
dropdown.bind("<<ComboboxSelected>>", on_select)

# Run the on_select function when the program starts
on_select(None)

# Set the position of the dropdown in the window
dropdown.grid(row=3, column=0, padx=10, pady=10)


# specify the size of the window
root.geometry("680x600")

# disable resizing the GUI
root.resizable(False, False)


def browse_mod_folder():
    mod_folder = filedialog.askdirectory()
    mod_folder_entry.delete(0, tk.END)
    mod_folder_entry.insert(0, mod_folder)


def browse_language_folder():
    language_folder = filedialog.askdirectory()
    language_folder_entry.delete(0, tk.END)
    language_folder_entry.insert(0, language_folder)


def browse_output_folder():
    output_folder = filedialog.askdirectory()
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(0, output_folder)


def run_program():
    if not mod_folder_entry.get() or not language_folder_entry.get() or not output_folder_entry.get():
        messagebox.showerror(
            "Error", "Please fill in all fields.")
        return
    disable_button()
    # Clear the log box
    log_box.config(state=tk.NORMAL)
    log_box.delete('1.0', tk.END)
    log_box.config(state=tk.DISABLED)

    mod_folder = mod_folder_entry.get()
    language_folder = language_folder_entry.get()
    output_folder = output_folder_entry.get()

    # Get the name of the last folder in the paths
    mod_folder_name = os.path.basename(os.path.normpath(mod_folder))
    language_folder_name = os.path.basename(
        os.path.normpath(language_folder))
    output_folder_name = os.path.basename(os.path.normpath(output_folder))

    # List files and folders in mod_folder including those in subfolders and full path
    mod_files_list = []
    for root, dirs, files in os.walk(mod_folder):
        for file in files:
            path = os.path.join(root, file)
            mod_files_list.append(path)

    # Delete the value of mod_folder from the path
    mod_files_list = [x.replace(mod_folder, '') for x in mod_files_list]

    # List files and folders in language_folder including those in subfolders and full path
    language_files_list = []
    for root, dirs, files in os.walk(language_folder):
        for file in files:
            path = os.path.join(root, file)
            language_files_list.append(path)

    # Delete the value of language_folder from the path
    language_files_list = [x.replace(language_folder, '')
                           for x in language_files_list]

    print("Deleting files from language_folder that don't exist in mod_folder")

    # If the file exists in language_folder and not in mod_folder, delete it from language_folder
    for file in language_files_list:
        full_path = language_folder + file
        if file not in mod_files_list:
            os.remove(full_path)

    print("Copying files missing in language_folder from mod_folder")

    # If the file exists in mod_folder and not in language_folder, copy it from mod_folder to language_folder to avoid errors
    for file in mod_files_list:
        full_path = mod_folder + file
        if file not in language_files_list:
            # New path for the file
            new_path = language_folder + file
            print("Copying " + file + " to " + new_path)
            shutil.copy(full_path, new_path)

    print("Deleting files with wrong extension")

    language_files_list_updated = []
    for root, dirs, files in os.walk(language_folder):
        for file in files:
            path = os.path.join(root, file)
            language_files_list_updated.append(path)

    # Delete the path of language_folder from the list
    language_files_list_updated = [x.replace(language_folder, '')
                                   for x in language_files_list_updated]

    mod_files_list_updated = []
    for root, dirs, files in os.walk(mod_folder):
        for file in files:
            path = os.path.join(root, file)
            mod_files_list_updated.append(path)

    # Delete the path of mod_folder from the list
    mod_files_list_updated = [x.replace(mod_folder, '')
                              for x in mod_files_list_updated]

    # Delete files from language_folder that don't end with .bf or .bmd
    for file in language_files_list_updated:
        full_path = language_folder + file
        if not file.lower().endswith((".bf", ".bmd")):
            # print(f"El archivo {file} no es .bf o .bmd, se eliminará.")
            os.remove(full_path)

    for file in mod_files_list_updated:
        full_path = mod_folder + file
        if not file.lower().endswith((".bf", ".bmd")):
            # print(f"El archivo {file} no es .bf o .bmd, se eliminará.")
            os.remove(full_path)

    # Path to the dependencies
    personaeditor_path = os.path.join(
        'dependencies', 'personaeditor', 'personaeditorcmd.exe')
    atlus_script_tools_path = os.path.join(
        "dependencies", "atlusscripttools", "AtlusScriptCompiler.exe")

    # Current directory
    current_dir = os.path.abspath(os.path.dirname(__file__))

    # Define the functions that will be executed in each case

    # AtlusScriptCompiler functions
    def ASCDecompile(input_file_path):
        input_file_name = os.path.basename(input_file_path)
        if game == "Persona 5 Royal":

            print(f"Decompiling BMD file: {input_file_name} with P5R library")
            subprocess.run([atlus_script_tools_path, input_file_path,
                            "-Decompiled", "-Library", "P5R", "-Encoding", "P5"])
        else:
            print(f"Decompiling BMD file: {input_file_name} with P5 library")
            subprocess.run([atlus_script_tools_path, input_file_path,
                            "-Decompiled", "-Library", "P5", "-Encoding", "P5"])

    def ASCCompile(input_file_path):
        input_file_name = os.path.basename(input_file_path)
        if game == "Persona 5 Royal":
            print(f"Compiling BMD file: {input_file_name} with P5R library")
            output_file_path = os.path.splitext(input_file_path)[0] + '.bmd'
            subprocess.run([atlus_script_tools_path, input_file_path, "-Out",
                            output_file_path, "-Compile", "-OutFormat", "V1BE", "-Library", "P5R", "-Encoding", "P5"])
        else:
            print(f"Compiling BMD file: {input_file_name} with P5 library")
            output_file_path = os.path.splitext(input_file_path)[0] + '.bmd'
            subprocess.run([atlus_script_tools_path, input_file_path, "-Out",
                            output_file_path, "-Compile", "-OutFormat", "V1BE", "-Library", "P5", "-Encoding", "P5"])

    # PersonaEditor functions
    def PEExport(input_file_path):
        subprocess.run([personaeditor_path, input_file_path, '-expall'])

    def PEImport(input_file_path):
        subprocess.run([personaeditor_path, input_file_path,
                        '-impall', '-save', input_file_path])

    def des_case_bmd(name_file):
        ASCDecompile(name_file)

    def des_case_bf(path_file):
        PEExport(path_file)
        # the name_file is a path, so we need to get the name of the file
        name_file = os.path.basename(path_file)
        print(f"Extracting all files from bf file: {path_file}")
        # change the extension of the file to .bmd
        name_file_bmd = os.path.splitext(path_file)[0] + '.bmd'
        # the name of the file without the extension
        name_file_only = os.path.splitext(name_file)[0]
        # search for the bf file on the mod_folder
        for root, dirs, files in os.walk(mod_folder):
            for file in files:
                if file.lower() == name_file.lower() and file.lower().endswith('.bf'):
                    print(
                        f"Searching for the bf file: {name_file} in the mod folder")
                    name_file_bf_mod = os.path.join(root, file)
                    rel_path = os.path.relpath(name_file_bf_mod, mod_folder)
                    output_file = os.path.join(output_folder, rel_path)
                    output_dir = os.path.dirname(output_file)
                    # create the output directory if it doesn't exist
                    os.makedirs(output_dir, exist_ok=True)
                    shutil.copy(name_file_bf_mod, output_file)
                    break

        # check if the file exists
        if os.path.isfile(name_file_bmd):
            des_case_bmd(name_file_bmd)
        # dirname
        name_file_dirname = os.path.dirname(path_file)
        # get all the .dat files in the folder
        # get all the .dat files in the folder
        dat_files = []
        for root, dirs, files in os.walk(name_file_dirname):
            for file in files:
                if file.endswith('.DAT'):
                    dat_files.append(os.path.join(root, file))

        # if the files name start with name_file.name, copy the .dat files to the output folder
        for dat_file in dat_files:
            if dat_file.startswith(name_file_dirname):
                # replace the mod_folder or language_folder with the output_folder
                name_file_dirname_output = name_file_dirname.replace(
                    mod_folder, output_folder).replace(language_folder, output_folder)
        # create the output directory if it doesn't exist
                os.makedirs(os.path.dirname(
                    name_file_dirname_output), exist_ok=True)
        # copy the file to the output directory
                shutil.copy(dat_file, name_file_dirname_output)

    def com_case_bmd(name_file):
        ASCCompile(name_file)

    # replace

    def process_msg(name_file):

        # get the name of the file without the extension and add .msg
        name_file_msg = name_file

        # replace the mod_folder with language_folder
        name_file_msg_editlang = name_file_msg.replace(
            mod_folder, language_folder)
        # replace the language_folder with mod_folder
        name_file_msg_editmod = name_file_msg.replace(
            language_folder, mod_folder)

        # name_file_msg get the name_file_msg, and change the Mod folder for the Language folder
        name_file_msg_lang = os.path.join(
            name_file_msg_editlang)
        print("the name of the file is: ", name_file_msg_lang)

        # name_file_msg from the mod folder
        name_file_msg_mod = os.path.join(
            name_file_msg_editmod)

        name_file_msg_mod_msg = name_file_msg

        # get the route but on the output folder
        name_file_with_file = os.path.join(
            output_folder, os.path.basename(name_file_msg_mod_msg))

        mod_msg_names = []  # list with the names of the msg
        lang_msg_names = []  # list with the names of the msg

        excluded_keyslist = ['Ryuji', 'Morgana', 'Yusuke', 'Ann', 'Makoto', 'Futaba', 'Haru', 'Goro', 'Akechi', 'Kasumi', 'Yoshisawa', 'Kamoshida', 'Madarame', 'Kaneshiro',    'Okumura', 'Shido', 'Yaldabaoth', 'Sojiro', 'Sae', 'Nijima', 'Igor', 'Caroline', 'Justine', 'Tae', 'Takemi',
                             'Munehisa', 'Chihaya', 'Mifune', 'Yuki', 'Mishima', 'Ohya', 'Kawakami', 'Toranosuke', 'Shinya', 'Oya', 'Ichiko', 'Sadayo', 'Hifumi', 'Togo', 'Sugimura', 'Kawanabe', 'Iwai', 'Shiho', 'Wakaba', 'Maruki', 'Jose', 'Takuto', 'Joker', 'Kitagawa', 'Niijima', 'Sakamoto', 'Takamaki', 'Sakura', 'Sumire']

        with open(name_file_msg_lang, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for line in f:
                if line.startswith('[msg'):
                    # Remove everything before the second space and the [ and ]
                    fields = line.strip().split(' ', 2)
                    if len(fields) >= 3:
                        key = fields[2]
                        key = key[1:-1]
                        if key not in excluded_keyslist:
                            # Save the key in the msg_names list
                            lang_msg_names.append(key)
                        else:
                            print(
                                f"Warning: Line '{line.strip()}' in {name_file_msg_lang} is not in the expected format.")

        # Read the lines of the mod .msg file and save the lines that start with '[msg'
        with open(name_file_msg_mod, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for line in f:
                if line.startswith('[msg'):
                    # Remove everything before the second space and the [ and ]
                    fields = line.strip().split(' ', 2)
                    if len(fields) >= 3:
                        key = fields[2]
                        key = key[1:-1]
                        if key not in excluded_keyslist:
                            # Save the line in the msg_names list
                            mod_msg_names.append(key)
                    else:
                        print(
                            f"Warning: Line '{line.strip()}' in {name_file_msg_mod} is not in the expected format.")

        # Get the two lists and join them by index
        msg_names = zip(mod_msg_names, lang_msg_names)

        # Make the dictionary from the joined lists
        dic_names = dict(msg_names)

        lang_msg_lines = {}

        match = r"\[[^\[\]]*\]|\[[^\[]*[^\s\[\]]\]"

        # Read the lines of the language .msg file and save the lines that start with '[msg'
        with open(name_file_msg_lang, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for line in f:
                if line.startswith('[msg'):
                    value = []
                    while True:
                        next_line = next(f).strip()
                        if next_line:
                            # Apply regular expression to remove text between brackets
                            result = []
                            position = 0
                            while True:
                                coincidencia = re.search(
                                    match, next_line[position:])
                                if coincidencia:
                                    result.append(coincidencia.group(0))
                                    position += coincidencia.end()
                                else:
                                    break
                            # Check if the next character is a space or a bracket
                                if len(next_line[position:].strip()) == 0 or next_line[position:position+5] == "[var " or next_line[position:position+7] == "[f 4 1]" or next_line[position:position+7] == "[f 4 2]" or next_line[position:position+5] == "[clr " or next_line[position] != "[":
                                    break
                            # Remove the text between brackets and the characters "[w]" and "[e]"
                            for item in result:
                                next_line = next_line.replace(item, "")
                            next_line = next_line.replace("[w]", "").replace(
                                "[e]", "")
                        # Fix compilation error, replace "/" with "l"
                            value.append(next_line)
                        else:
                            break
                    lang_msg_lines[line.strip()] = "$f$".join(value)
                if line.startswith('[sel'):
                    value = []
                    while True:
                        next_line = next(f).strip()
                        if next_line:
                            value.append(next_line)
                        else:
                            break
                    lang_msg_lines[line.strip()] = "$f$".join(value)

        mod_msg_lines = {}

        # Open mod file and process each line
        with open(name_file_msg_mod, 'r', encoding='utf-8-sig', errors='ignore') as f:
            for line in f:
                if line.startswith('[msg'):
                    value = []
                    while True:
                        next_line = next(f).strip()
                        if next_line:
                            # Apply regular expression to remove text between brackets
                            result = []
                            position = 0
                            while True:
                                coincidencia = re.search(
                                    match, next_line[position:])
                                if coincidencia:
                                    result.append(coincidencia.group(0))
                                    position += coincidencia.end()
                                else:
                                    break
                            # Check if the next character is a space or a bracket
                                if len(next_line[position:].strip()) == 0 or next_line[position:position+5] == "[var " or next_line[position:position+7] == "[f 4 1]" or next_line[position:position+7] == "[f 4 2]" or next_line[position:position+5] == "[clr " or next_line[position] != "[":
                                    break
                        # Remove the text between brackets and the characters "[w]" and "[e]"
                            for item in result:
                                next_line = next_line.replace(item, "")
                            next_line = next_line.replace("[w]", "").replace(
                                "[e]", "")
                        # Fix compilation error, replace "/" with "l"
                            value.append(next_line)
                        else:
                            break
                    mod_msg_lines[line.strip()] = "$f$".join(value)
                if line.startswith('[sel'):
                    value = []
                    while True:
                        next_line = next(f).strip()
                        if next_line:
                            value.append(next_line)
                        else:
                            break
                    mod_msg_lines[line.strip()] = "$f$".join(value)

        # Delete [name] from key
        for key in mod_msg_lines.copy().keys():
            # delete all next from the second space
            new_key = key.split(' ', 2)[0] + ' ' + key.split(' ', 2)[1]
        # remove the last character (']') from the new key
            new_key = new_key.rstrip(']')
        # replace the key with the new key
            mod_msg_lines[new_key] = mod_msg_lines.pop(key)

        for key in lang_msg_lines.copy().keys():
            # delete all next from the second space
            new_key = key.split(' ', 2)[0] + ' ' + key.split(' ', 2)[1]
        # remove the last character (']') from the new key
            new_key = new_key.rstrip(']')
        # replace the key with the new key
            lang_msg_lines[new_key] = lang_msg_lines.pop(key)

        # """
        # Get the common keys
        common_keys = set(mod_msg_lines.keys()) & set(lang_msg_lines.keys())

        # Make a new dictionary with the corresponding keys and values of both dictionaries
        msg_matches = {}

        # Add the keys and values of the common keys
        for key in common_keys:
            mod_msg_text = mod_msg_lines[key].strip()
            lang_msg_text = lang_msg_lines[key].strip()
            msg_matches[mod_msg_text] = lang_msg_text

        keys_to_delete = []

        keys_to_add = []

        for key, value in msg_matches.items():
            if "$f$" in key:
                original_key = key
                key = key.split("$f$")
                value = value.split("$f$")
                for i in range(len(key)):
                    if i < len(key) and i < len(value):
                        keys_to_add.append((key[i], value[i]))
                keys_to_delete.append(original_key)
            if "$f$" in value:
                original_key = key
                key = key.split("$f$")
                value = value.split("$f$")
                for i in range(len(key)):
                    if i < len(key) and i < len(value):
                        keys_to_add.append((key[i], value[i]))
                keys_to_delete.append(original_key)

        # Delete the keys from the list
        for key in keys_to_delete:
            del msg_matches[key]

        # Add the keys from the list
        for key, value in keys_to_add:
            msg_matches[key] = value

        # Check if the file has the .msg extension
        if os.path.splitext(name_file_msg)[1].lower() != '.msg':
            return

        # Change language_folder or mod_folder to output_folder
        name_file_msg_mod_msg2 = name_file_msg_mod_msg.replace(
            language_folder, output_folder).replace(mod_folder, output_folder)
        # delete the file_name from the path
        file_name = os.path.basename(name_file_msg_mod_msg2)
        # delete the file_name from the path
        output_folder_msg_withoutroute = name_file_msg_mod_msg2.replace(
            file_name, '')

        print(f"Coping {name_file_msg_mod} to {name_file_msg_mod_msg2}")
        # Check if the output folder exists, otherwise create it
        if not os.path.exists(output_folder_msg_withoutroute):
            os.makedirs(output_folder_msg_withoutroute)

        # Copy the file to the output folder
        shutil.copy(name_file_msg_mod_msg, name_file_msg_mod_msg2)

        num_lines_replaced = 0

        # Replace the lines of the name_file.msg file in the output_folder folder that match key with the value of msg_matches[key]
        if os.path.isfile(name_file_msg_mod_msg2) and name_file_msg_mod_msg2.lower().endswith('.msg'):
            with open(name_file_msg_mod_msg2, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()
            for key, value in msg_matches.items():
                content, num_replaced = content.replace(
                    key, value), content.count(key)
                num_lines_replaced += num_replaced
            with open(name_file_msg_mod_msg2, 'w', encoding='utf-8-sig', errors='ignore') as f:
                f.write(content)
        # Replace "/" with "l"
        if os.path.isfile(name_file_msg_mod_msg2) and name_file_msg_mod_msg2.lower().endswith('.msg'):
            with open(name_file_msg_mod_msg2, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.readlines()
            with open(name_file_msg_mod_msg2, 'w', encoding='utf-8-sig', errors='ignore') as f:
                for line in content:
                    # check if the line not start with [msg, [sel, // or is empty
                    if not line.startswith('[msg') and not line.startswith('//') and not line.startswith('[sel') and line.strip():
                        line = line.replace('/', 'l')
                    f.write(line)
        # Add [f 0 5 -258] at the start of all lines that do not start with [msg, [sel or are empty
        with open(name_file_msg_mod_msg2, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.readlines()
        with open(name_file_msg_mod_msg2, 'w', encoding='utf-8-sig', errors='ignore') as f:
            for line in content:
                if line.startswith('[msg') or line.startswith('//') or line.startswith('[sel') or not line.strip():
                    f.write(line)
                else:
                    f.write('[f 0 5 -258]' + line)
        # Replace the lines with the dic_names dictionary, search the keys and replace them with their values in the name_file_with_file file
        with open(name_file_msg_mod_msg2, 'r', encoding='utf-8-sig', errors='ignore') as f:
            content = f.readlines()
        with open(name_file_msg_mod_msg2, 'w', encoding='utf-8-sig', errors='ignore') as f:
            for line in content:
                if line.startswith("[msg"):
                    for key, value in dic_names.items():
                        line, num_replaced = line.replace(
                            key, value), line.count(key)
                        num_lines_replaced += num_replaced
                f.write(line)

        if num_lines_replaced == 0:
            print(f"No lines replaced in {name_file_msg_mod_msg2}")
        elif num_lines_replaced == 1:
            print(f"1 line replaced in {name_file_msg_mod_msg2}")
        else:
            print(f"{num_lines_replaced} lines replaced in {name_file_msg_mod_msg2}")

    # Delete all files that are not .bin, .bmd, .pak or .bf
    for folder in [mod_folder, language_folder]:
        for file in os.scandir(folder):
            if file.is_file() and not file.name.lower().endswith((".bin", ".bmd", ".pak", ".bf")):
                os.remove(file.path)

    # Check all types of files in the "Mod" folder
    # Read all files in the root and its subfolders
    for folder_name, subfolders, files in os.walk(mod_folder):
        # Read all files in the current folder
        for name_file in files:
            print(f"Processing file: {name_file}")
            file_extension = name_file.split('.')[-1]
            switcher = {
                'bmd': des_case_bmd,
                'bf': des_case_bf,
                'BMD': des_case_bmd,
                'BF': des_case_bf
            }
            if file_extension in switcher:
                print(f"Processing switcher file: {name_file}")
                switcher[file_extension](os.path.join(folder_name, name_file))

    # Check all types of files in the "Language" folder
    # Read all files in the root and its subfolders
    for folder_name, subfolders, files in os.walk(language_folder):
        # Read all files in the current folder
        for name_file in files:
            print(f"Processing file: {name_file}")
            file_extension = name_file.split('.')[-1]
            switcher = {
                'bmd': des_case_bmd,
                'bf': des_case_bf,
                'BMD': des_case_bmd,
                'BF': des_case_bf
            }
            if file_extension in switcher:
                print(f"Processing switcher file: {name_file}")
                switcher[file_extension](os.path.join(folder_name, name_file))

    # Proccess all .msg files in the "Mod" folder and make the changes in the "Output" folder
    for root, dirs, files in os.walk(mod_folder):
        for name_file in files:
            if name_file.lower().endswith('.msg'):
                # print(f"Processing file: {root}/{name_file}")
                process_msg(os.path.join(root, name_file))

    for root, dirs, files in os.walk(output_folder):
        for msg_file in files:
            if msg_file.lower().endswith('.msg'):
                print(f"Compiling {msg_file}")
                ASCCompile(os.path.join(root, msg_file))

    # Change all the endwith .bmd.bmd to .bmd
    for root, dirs, files in os.walk(output_folder):
        for name in files:
            if name.lower().endswith('.bmd.bmd'):
                old_path = os.path.join(root, name)
                new_path = os.path.join(root, name[:-8] + ".bmd")
                print(f"Renaming {old_path} to {new_path}")
                try:
                    os.rename(old_path, new_path)
                except FileExistsError:
                    print(f"Skipping {old_path} as {new_path} already exists")
                    continue

    # Import all .bf files in the "Output" folder with PEImport
    for root, dirs, files in os.walk(output_folder):
        for mod_file in files:
            if mod_file.lower().endswith('.bf'):
                mod_file_path = os.path.join(root, mod_file)
                print(f"Importing {mod_file} in {root}")
                PEImport(mod_file_path)
            mod_file_name_new = mod_file.split('.')[0]

    # print(f"Deleting extra files from {output_folder}...")

    # print(mod_files_list)

    # Delete all files that are not in the mod_files_list, this leaves only the original mod files
    for root, dirs, files in os.walk(output_folder):
        # get the full path of the files in the current directory
        file_paths = [os.path.join(root, file) for file in files]
        # loop over the file paths
        for file_path in file_paths:
            # get all the lines of the mod_files_list
            for line in mod_files_list:
                # if the file path is not in the list of paths to keep, delete it
                mod_file_list_path = output_folder + line.strip()
                if file_path not in mod_file_list_path:
                    print(f"Deleting {file_path}")
                    try:
                        os.remove(file_path)
                        print(f"Deleted {file_path}")
                    except FileNotFoundError:
                        print(f"File {file_path} not found, skipping")
                        continue

    # Delete all files that are not in the mod_files_list, this leaves only the original mod files
    for root, dirs, files in os.walk(mod_folder):
        # get the full path of the files in the current directory
        file_paths = [os.path.join(root, file) for file in files]
        # loop over the file paths
        for file_path in file_paths:
            # get all the lines of the mod_files_list
            for line in mod_files_list:
                # if the file path is not in the list of paths to keep, delete it
                mod_file_list_path = mod_folder + line.strip()
                if file_path not in mod_file_list_path:
                    print(f"Deleting {file_path}")
                    try:
                        os.remove(file_path)
                        print(f"Deleted {file_path}")
                    except FileNotFoundError:
                        print(f"File {file_path} not found, skipping")
                        continue

    # Delete all files that are not in the language_files_list, this leaves only the original language files
    for root, dirs, files in os.walk(language_folder):
        # get the full path of the files in the current directory
        file_paths = [os.path.join(root, file) for file in files]
        # loop over the file paths
        for file_path in file_paths:
            # get all the lines of the mod_files_list
            for line in language_files_list:
                # if the file path is not in the list of paths to keep, delete it
                language_file_list_path = language_folder + line.strip()
                if file_path not in language_file_list_path:
                    print(f"Deleting {file_path}")
                    try:
                        os.remove(file_path)
                        print(f"Deleted {file_path}")
                    except FileNotFoundError:
                        print(f"File {file_path} not found, skipping")
                        continue

    print("Done!")
    enable_button()
    tk.messagebox.showinfo("Finished", "Replaced all the names in the mod!")


# Mod folder
mod_folder_label = ttk.Label(root, text="Mod folder:", background="#242424")
mod_folder_entry = ttk.Entry(root, width=60)
mod_folder_button = ttk.Button(root, text="Browse", command=browse_mod_folder)
mod_folder_entry.insert(0, mod_folder)  # Insert the saved value

mod_folder_label.grid(row=0, column=0, padx=5, pady=10)
mod_folder_entry.grid(row=0, column=1, padx=5, pady=10)
mod_folder_button.grid(row=0, column=2, padx=5, pady=10)

# Language folder
language_folder_label = ttk.Label(
    root, text="Language folder:", background="#242424")
language_folder_entry = ttk.Entry(root, width=60)
language_folder_button = ttk.Button(
    root, text="Browse", command=browse_language_folder)
language_folder_entry.insert(0, language_folder)  # Insert the saved value

language_folder_label.grid(row=1, column=0, padx=5, pady=10)
language_folder_entry.grid(row=1, column=1, padx=5, pady=10)
language_folder_button.grid(row=1, column=2, padx=5, pady=10)

# Output folder
output_folder_label = ttk.Label(
    root, text="Output folder:", background="#242424")
output_folder_entry = ttk.Entry(root, width=60)
output_folder_button = ttk.Button(
    root, text="Browse", command=browse_output_folder)
output_folder_entry.insert(0, output_folder)  # Insert the saved value

output_folder_label.grid(row=2, column=0, padx=5, pady=10)
output_folder_entry.grid(row=2, column=1, padx=5, pady=10)
output_folder_button.grid(row=2, column=2, padx=5, pady=10)

# Run button
run_button = ttk.Button(root, text="Replace", command=run_program)
run_button.grid(row=4, column=1, padx=0, pady=15)


def save_config():
    # Save the values in the config file
    config['Folders'] = {
        'mod_folder': mod_folder_entry.get(),
        'language_folder': language_folder_entry.get(),
        'output_folder': output_folder_entry.get(),
        'game': game
    }

    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def on_closing():
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
        save_config()
        root.destroy()


# Run the on_closing function when the window is closed
root.protocol("WM_DELETE_WINDOW", on_closing)

sv_ttk.set_theme("dark")

# set theme dark in cttk
customtkinter.set_appearance_mode("dark")

root.iconbitmap("dependencies/test2.ico")

root.title("Persona 5 Royal Text Swapper")

root.mainloop()
