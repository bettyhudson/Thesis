import os
import re
import shutil

def fix_annotations_in_file(file_path):
    # Open the file for reading
    with open(file_path, 'r') as file:
        # Read the content of the file
        content = file.read()

    # Replace all occurrences of three or more underscores followed by digits with two underscores using regular expression
    new_content = re.sub(r'\_{3,}\d*', '__', content)

    # Check if content has changed
    if new_content != content:
        # Backup original file
        backup_path = file_path + ".bak"
        shutil.copyfile(file_path, backup_path)

        # Open the file for writing and overwrite its content with the updated annotations
        with open(file_path, 'w') as file:
            file.write(new_content)
        return True  # Return True if file was modified
    else:
        return False  # Return False if file was not modified

def fix_annotations_in_directory(directory_path):
    changed_files = []  # List to store paths of changed files

    # Iterate over all files in the specified directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):  # assuming annotations are stored in .txt files
            file_path = os.path.join(directory_path, filename)
            # Fix annotations in each file and check if the file was modified
            if fix_annotations_in_file(file_path):
                changed_files.append(file_path)

    return changed_files

# Specify the directory containing your files
directory_path = r'insert_directory_path_here'

# Fix annotations in all files in the specified directory and get a list of changed files
changed_files = fix_annotations_in_directory(directory_path)

# Print paths of changed files
print("Changed files:")
for file_path in changed_files:
    print(file_path)