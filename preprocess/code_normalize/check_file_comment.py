import os
import re
from pathlib import Path

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
                print(f"Không thể đọc file {file_path}: {e}")
    return matched_folders

root_folder = Path(__file__).parent.parent.parent / "dataset" / "dataset_normalization"
pattern = r'\/\*'
matched_files = find_folders_with_pattern(root_folder, pattern)
count = 0
for folder in matched_files:
    count += 1
    print(folder)
print(count)