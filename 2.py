import os
import re

def count_silent_pauses(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Match "__" not preceded or followed by x or y
    pattern = r'(?<![xy])__(?![xy])'

    return len(re.findall(pattern, text))

def count_silent_pauses_in_directory(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory_path, filename)
            count = count_silent_pauses(file_path)
            print(f"{filename}: {count}")

# CHANGE THIS PATH
directory_path = r'C:\path\to\your\directory'

count_silent_pauses_in_directory(directory_path)