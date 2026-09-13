import os
import re

def count_underscore_x(file_path):
    # Open the file for reading
    with open(file_path, 'r') as file:
        # Read the content of the file
        content = file.read()

    # Define the regular expression pattern to match "_x_"
    pattern = r'_x_'

    # Use the findall() function to find all matches of the pattern in the content
    matches = re.findall(pattern, content)

    # Return the count of matches
    return len(matches)

def count_underscore_x_in_directory(directory_path):
    # Iterate over all files in the specified directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):  # assuming annotations are stored in .txt files
            file_path = os.path.join(directory_path, filename)
            # Count occurrences of "_x_" in each file
            count = count_underscore_x(file_path)
            # Print the count for the current file
            print(f"Occurrences of '_x_' in '{filename}': {count}")

# Specify the directory containing your files
directory_path = r'insert_directory_path_here'

# Count occurrences of "_x_" in each file in the specified directory
count_underscore_x_in_directory(directory_path)