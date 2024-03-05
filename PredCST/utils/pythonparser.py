import codecs
import glob
import os
from typing import Dict, List, Tuple
import difflib

from PredCST.processors.parsers.python_parser import PythonParser


def traverse_and_collect_rtd(directory):
    """
    This function traverses a directory and collects content from .rst files.
    The content is stored in a list of tuples, with filename as 0th element and content as 1st.

    Parameters:
    directory (str): The directory to traverse

    Returns:
    list: A list of tuples containing filename and file content
    """

    # Placeholder for the list of tuples
    data = []

    # Traversing the directory recursively
    for filename in glob.glob(os.path.join(directory, "**", "*.rst"), recursive=True):
        # Open file
        with codecs.open(filename, "r", encoding="utf-8", errors="ignore") as file:
            # Read content and add to list
            content = file.read()
            data.append((filename, content))

    return data



def print_code_diff(code1, code2):
    # Split the code into lines for a detailed comparison
    lines1 = code1.splitlines(keepends=True)
    lines2 = code2.splitlines(keepends=True)
    
    # Generate the diff using difflib
    diff = difflib.unified_diff(lines1, lines2, fromfile="code1.py", tofile="code2.py")
    
    # Print the diff
    print(''.join(diff))