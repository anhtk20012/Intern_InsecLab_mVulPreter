# coding=utf-8
import os
import re
from clean_gadget import clean_gadget
from pathlib import Path

def preprocess(path):
    Path(path).mkdir(exist_ok=True, parents=True)
    
def normalize(path, directory_path, directory_temp):
    file_list = os.listdir(path)
    name_folder = path.split('/')[-1]
    for _file in file_list:
        pro_one_file(os.path.join(path, _file), name_folder, directory_path, directory_temp)

def remove_comments(text):
    """Delete comments from code."""
    
    def replacer(match):
        s = match.group(0)
        if s.startswith("/"):
            return " "  # note: a space and not an empty string
        else:
            return s

    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"|/\*.*?$',
        re.DOTALL | re.MULTILINE,
    )
    return re.sub(pattern, replacer, text)

def pro_one_file(filepath, namefolder, directory_path, directory_temp):
    with open(filepath, "r") as file:
        code = file.read()
        
    code = remove_comments(code)
    
    file_name = filepath.split('/')[-1]
    temp_file = directory_temp / namefolder
    preprocess(temp_file)
    
    temp_file2=os.path.join(temp_file, file_name)
    with open(temp_file2, "w") as file:
        file.write(code.strip())
        
    with open(temp_file2, "r") as file:
        org_code = file.readlines()
        nor_code = clean_gadget(org_code)
        
    norm_path = directory_path / namefolder
    preprocess(norm_path)
    
    norm_path2=os.path.join(norm_path, file_name)
    with open(norm_path2, "w") as file:
        file.writelines(nor_code)

def load_dir(directory):
    directory_paths = []
    for root, directories, files in os.walk(directory):
        for dirname in directories:
            dirname = os.path.join(root, dirname)
            directory_paths.append(dirname)
    return directory_paths

def find_folders_with_pattern(root_folder, pattern):
    matched_folders = set()
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if re.search(pattern, content):
                        matched_folders.add(root)
                        break
            except Exception as e:
                print(f"Don't read file {file_path}: {e}")
    return matched_folders

if __name__ == '__main__':
    directory_path = Path(__file__).parent.parent.parent / "dataset" / "all_dataset"
    if os.path.exists(directory_path):
        directory_out = Path(__file__).parent.parent.parent / "dataset" / "all_dataset_clear"
        preprocess(directory_out)
        directory_temp = Path(__file__).parent.parent.parent / "dataset" / "temp"
        preprocess(directory_temp)
        files = load_dir(directory_path)
        print("======== Normalize comment and change style function ========")
        for file in files:
            normalize(file, directory_out, directory_temp)
    else:
        print("Dataset not exists")
        
    print("======== Check comment all file in folder dataset clear ========")
    root_folder = Path(__file__).parent.parent.parent / "dataset" / "all_dataset_clear"
    if os.path.exists(root_folder):
        pattern = r'\/\*'
        matched_files = find_folders_with_pattern(root_folder, pattern)
        count = 0
        for folder in matched_files:
            count += 1
            print(folder)
        print(f"Total file exist comment {count}")
    else:
        print("Dataset normalization not exists")