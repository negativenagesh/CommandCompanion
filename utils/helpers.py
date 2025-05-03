# filepath: /home/subrahmanya/projects/CommandCompanion/utils/helpers.py
"""
Helper functions for CommandCompanion
"""

import json
import re
import shutil
import os

def is_app_available(app_cmd):
    """
    Check if an application exists in the system path.
    Optimized for Fedora OS.
    """
    return shutil.which(app_cmd) is not None

def extract_json(text):
    """
    Extract JSON object or array from the response text.
    Handles various formats including code blocks.
    """
    match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        start = text.find('{')
        if start == -1:
            start = text.find('[')
        end = text.rfind('}')
        if end == -1:
            end = text.rfind(']')
        if start != -1 and end != -1:
            json_str = text[start:end+1]
        else:
            return None
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None

def sanitize_filename(name):
    """
    Sanitize a string to be used as a filename.
    Removes invalid characters and converts spaces to underscores.
    """
    return name.replace(' ', '_').lower()

def ensure_directory_exists(directory):
    """
    Ensure the specified directory exists, creating it if necessary.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory