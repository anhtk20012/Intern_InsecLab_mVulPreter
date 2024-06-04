import os
import glob
import argparse
from multiprocessing import Pool
from functools import partial
import subprocess
from pathlib import Path

def joern_parse(file, outdir):
    try:
        Path(outdir).mkdir(exist_ok=True, parents=True)  
    except:
        pass
    name = file.split('/')[-1][:-2]
    out = outdir / (name + '.bin')
    if os.path.exists(out):
        print("================== has been procesed:\t" + out)
        return
    
    print(' ----> now processing parse: ',name)
    c = str(file)
    b = str(out)
    os.system(f'sh joern-parse {c} --language c --out {b}')

def joern_export(bin, outdir, repr):
    bin = bin.strip()
    if repr == 'ddg':
        out = outdir / 'ddg'
    else:
        out = outdir / 'json'
    try:
        Path(out).mkdir(exist_ok=True, parents=True)  
    except:
        pass     
    name = bin.split('/')[-1][:-4]
    out = out / name

    if os.path.exists(out):
        print("================== has been procesed:\t" + out)
        return
    
    print(f' ----> now processing export {repr}: ',name)
    b = str(bin)
    if repr == 'ddg':
        d = str(out)
        os.system(f'sh joern-export {b} --repr {repr} --out {d}')
    elif repr == "json":
        j = str(out)
        joern_process = subprocess.Popen(["./joern"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
        import_cpg_cmd = f"importCpg(\"{b}\")\r"
        script_path = Path(__file__).parent / 'graph-for-funcs.sc'
        run_script_cmd = f"cpg.runScript(\"{script_path}\").toString() |> \"{j}\"\r"
        cmd = import_cpg_cmd + run_script_cmd
        ret , err = joern_process.communicate(cmd)
        
def main():
    joern_path = Path(__file__).parent.parent.parent / 'joern-cli_v1.1.172'
    os.chdir(joern_path)
    input_path = Path(__file__).parent.parent / 'dataset' / 'all_dataset_clear'
    output_path = Path(__file__).parent.parent / 'dataset' / 'dataset_joern'
        
    pool_num = 16
    pool = Pool(pool_num)
    
    # Create folder bin for all file c
    print ("======== Create all file bin ========")
    subfolders = [f.name for f in os.scandir(input_path) if f.is_dir()]
    for folder in subfolders:
        file_input = str(input_path / folder / '*.c')
        files = glob.glob(file_input)
        folder_bin = output_path / folder / 'bin'
        pool.map(partial(joern_parse, outdir = folder_bin), files)
        
    # Create folder ddg dot for all file bin
    print ("======== Create all file ddg.dot and all file cpg.json ========")
    subfolders = [f.name for f in os.scandir(output_path) if f.is_dir()]
    for folder in subfolders:
        file_input = str(output_path / folder / 'bin' /'*.bin')
        bins = glob.glob(file_input)
        folder_out = output_path / folder
        pool.map(partial(joern_export, outdir = folder_out, repr="ddg"), bins)
        pool.map(partial(joern_export, outdir = folder_out, repr="json"), bins)

if __name__ == '__main__':
    main()
