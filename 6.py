import os
import re
import string

def count_lexical_words(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Remove silent pauses (__), filled pauses (_x_), and lengthenings (_y_)
    text = re.sub(r'__|_x_|_y_', '', text)
    
    # Remove numeric annotations (like 0.03, __0.52, _y_0.18)
    text = re.sub(r'\b\d*\.?\d+\b', '', text)
    
    # Remove leftover underscores
    text = text.replace('_', '')
    
    # Remove all common punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Split on whitespace
    words = text.split()
    
    # Keep only words that contain at least one alphabetic character and are longer than 1 character
    words = [w for w in words if any(c.isalpha() for c in w) and len(w) > 1]
    
    return len(words)

def count_words_in_directory(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory_path, filename)
            word_count = count_lexical_words(file_path)
            print(f"{filename}: {word_count}")

# Directory path
directory_path = r'insert_directory_path_here'

count_words_in_directory(directory_path)