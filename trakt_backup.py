import datetime
import os
import sys
import subprocess
import trakt_request
import pandas
import converters.json_to_csv as jtc
import converters.json_to_xml as jtx

accepted_file_types = ['json', 'csv', 'xml']

def launch_file(filepath):
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', filepath))
    elif os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', filepath))

def convert(file_type, path):
    for file in os.listdir(path):
        if file_type == 'csv':
            dataframe = jtc.get_dataframe_csv(path, file)
            if dataframe is not None:
                dataframe.to_csv(os.path.join(path, file.replace('.json', '.csv')), index=False)
        elif file_type == 'xml':
            tree = jtx.get_tree_xml(path, file)
            if tree is not None:
                with open(os.path.join(path, file.replace('.json', '.xml')), 'wb') as f:
                    f.write(tree)
        if not file.startswith('stats'):
            os.remove(os.path.join(path, file))

folder = input(f"Save files here (shell current working directory) ? [Y/n]\n(files will otherwise be saved in {os.path.expanduser('~')}): ")

if folder.upper() == 'Y':
    root = os.getcwd()
    root = os.path.join(root, 'trakt_backup')
else:
    root = os.path.expanduser('~')
    root = os.path.join(root, 'trakt_backup')

print(f'Files will be saved in: {root}')

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    username = input('Enter your Trakt username: ')

if len(sys.argv) > 2 and sys.argv[2] in accepted_file_types:
    file_type = sys.argv[2].lower()
else:
    print('Unsupported or no file type specified, defaulting to json')
    file_type = 'json'

if not os.path.exists(root):
    os.makedirs(root)

timestamp = os.path.getmtime(root)
backup_folder_name = os.path.join(root, str(datetime.datetime.now().replace(microsecond=0)).replace(':', '.'))
os.makedirs(backup_folder_name)

try:
    trakt_request.create_data_files(username, backup_folder_name)
except Exception as e:
    print(e)
    os.rmdir(backup_folder_name)
    sys.exit()

if file_type != 'json':
    convert(file_type, backup_folder_name)

new_backup_folder_name = f'{backup_folder_name} {file_type}'
os.rename(backup_folder_name, new_backup_folder_name)

launch_file(new_backup_folder_name)
print('Done.')