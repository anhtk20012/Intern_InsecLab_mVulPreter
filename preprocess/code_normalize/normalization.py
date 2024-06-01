# coding=utf-8
import os
import re
import shutil
from clean_gadget import clean_gadget
from pathlib import Path

# 预处理文件，每个C文件外包一层同名文件夹，并将文件放入joern的指定路径
def preprocess(org_path, joern_path):
    SARD = joern_path + "/20000"
    SARD_Vul = SARD + "/Vul"
    SARD_NoVul = SARD + "/NoVul"
    nvd = joern_path + "/ALL_9"
    nvd_Vul = nvd + "/Vul"
    nvd_NoVul = nvd +"/NoVul"
    if not os.path.exists(SARD):
        os.mkdir(SARD)
    if not os.path.exists(SARD_Vul):
        os.mkdir(SARD_Vul)
    if not os.path.exists(SARD_NoVul):
        os.mkdir(SARD_NoVul)
    if not os.path.exists(nvd):
        os.mkdir(nvd)
    if not os.path.exists(nvd_Vul):
        os.mkdir(nvd_Vul)
    if not os.path.exists(nvd_NoVul):
        os.mkdir(nvd_NoVul)

    setfolderlist = os.listdir(org_path)
    for setfolder in setfolderlist:
        catefolderlist = os.listdir(org_path + "/" + setfolder)
        for catefolder in catefolderlist:
            filelist = os.listdir(org_path + "/" + setfolder + "/" + catefolder)
            for file in filelist:
                filename = file[:-2]
                oldpath = org_path + "/" + setfolder + "/" + catefolder
                newpath = joern_path + "/" + setfolder + "/" + catefolder + "/" + filename
                if not os.path.exists(newpath):
                    os.mkdir(newpath)
                shutil.copy(oldpath + "/" + file, newpath)


# 遍历预处理后的文件，对每个文件进行规范化
def normalize(path):
    file_list = os.listdir(path)
    name_folder = path.split('/')[-1]
    for _file in file_list:
        # print(os.path.join(path, _file), name_folder)
        pro_one_file(os.path.join(path, _file), name_folder)
    '''for setfolder in setfolderlist:
        filepath = os.path.join(path, setfolder)
        file_list = os.listdir(filepath)
        filepath_tmp = filepath.replace("Vul", "sard-vul-src_without_comment")
        print("---=-=-=-=-=-=-=", len(os.listdir('/home/Final_Dataset_Old/sard-vul-src_without_comment')))
        if not os.path.exists(filepath_tmp):
            os.mkdir(filepath_tmp)
        else:
            continue
        for _file in file_list:
            pro_one_file(os.path.join(filepath, _file))'''

def remove_comments(text):
    """Delete comments from code."""

    def replacer(match):
        s = match.group(0)
        if s.startswith("/"):
            return " "  # note: a space and not an empty string
        else:
            return s

    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE,
    )
    return re.sub(pattern, replacer, text)


def pro_one_file(filepath, namefolder):
    directory_temp = Path(__file__).parent.parent.parent / "dataset" / "temp"
    Path(directory_temp).mkdir(exist_ok=True, parents=True)
    directory_path = Path(__file__).parent.parent.parent / "dataset" / "dataset_normalization"
    Path(directory_path).mkdir(exist_ok=True, parents=True)
    linefeed='\n'
    with open(filepath, "r") as file:
        code = file.read()
    code = remove_comments(code)
    # annotations = re.findall('(?<!:)\\/\\/.*|\\/\\*(?:\\s|.)*?\\*\\/', code)
    # for annotation in annotations:
    #     lf_num = annotation.count('\n')
    #     if lf_num == 0:
    #         code = code.replace(annotation,'')
    #         continue
    #     code = code.replace(annotation,lf_num*linefeed)
    file_name = filepath.split('/')[-1]
    temp_file = directory_temp / namefolder
    Path(temp_file).mkdir(exist_ok=True, parents=True)
    temp_file2=os.path.join(temp_file, file_name)
    with open(temp_file2, "w") as file:
        file.write(code.strip())
    with open(temp_file2, "r") as file:
        org_code = file.readlines()
        nor_code = clean_gadget(org_code)
    norm_path = directory_path / namefolder
    Path(norm_path).mkdir(exist_ok=True, parents=True)
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


if __name__ == '__main__':
    # preprocess("/mnt/ysr/data_original", "/mnt/ysr/data")
    directory_path = Path(__file__).parent.parent.parent / "dataset" / "dataset_test"
    files = load_dir(directory_path)
    count = 0
    for file in files:
        normalize(file)
    # pro_one_file("/mnt/ysr/data_ocriginal/basic-00001-min.c")
