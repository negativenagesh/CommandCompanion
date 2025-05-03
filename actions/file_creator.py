"""
File creation functionality for CommandCompanion
"""

import os
import subprocess
import google.generativeai as genai
from config.settings import AI_MODEL, PYTHON_PROMPT_TEMPLATE, WEBSITE_PROMPT_TEMPLATE
from utils.helpers import sanitize_filename
from actions.app_launcher import vscode_info  # Import the global vscode_info

def generate_content(prompt):
    """
    Generate content using Gemini with detailed debugging.
    
    Args:
        prompt (str): The prompt to send to Gemini
        
    Returns:
        str: The generated content or None if failed
    """
    try:
        model = genai.GenerativeModel(AI_MODEL)
        print(f"Sending prompt to Gemini: {prompt}")
        response = model.generate_content(prompt)
        content = response.text.strip()
        if not content:
            print("Gemini returned empty content")
            return None
        print(f"Generated content: {content[:200]}...")
        return content
    except Exception as e:
        print(f"Error generating content: {str(e)}")
        return None

def create_file(content_type, topic, reuse_vscode=False):
    """
    Create a file with generated content and open it.
    
    Args:
        content_type (str): Type of content to generate ('python' or 'website')
        topic (str): The topic/purpose of the file
        reuse_vscode (bool): Whether to reuse an existing VSCode window
        
    Returns:
        str: Status message about the operation
    """
    if content_type == 'python':
        prompt = PYTHON_PROMPT_TEMPLATE.format(topic=topic)
        content = generate_content(prompt)
        if content:
            filename = f"{sanitize_filename(topic)}.py"
            
            # Determine where to save the file
            folder_path = vscode_info.get("folder")
            if folder_path and os.path.exists(folder_path):
                filepath = os.path.join(folder_path, filename)
                print(f"Creating file in tracked VSCode folder: {filepath}")
            else:
                # Fallback to current directory
                filepath = os.path.abspath(filename)
                print(f"Creating file in current directory: {filepath}")
                
            try:
                # Make sure we have absolute paths
                abs_filepath = os.path.abspath(filepath)
                
                # Write the content to the file
                with open(abs_filepath, 'w') as f:
                    f.write(content)
                print(f"Successfully wrote to {abs_filepath}")
                
                if folder_path and os.path.exists(folder_path):
                    # File was already created in the VSCode workspace folder
                    # It should appear automatically, but we'll open it explicitly just to be sure
                    try:
                        subprocess.run(['code', '--goto', abs_filepath])
                        return f"Created {filename} in the VSCode workspace"
                    except Exception as e:
                        print(f"Warning: Could not open file in VSCode: {str(e)}")
                        return f"Created {filename} in the VSCode workspace"
                else:
                    # No tracked VSCode session, open normally
                    cmd = ['code', abs_filepath]
                    if reuse_vscode:
                        cmd.append('--reuse-window')
                    subprocess.Popen(cmd)
                    return f"Created and opened {filename}"
            except Exception as e:
                print(f"Error writing file {filepath}: {str(e)}")
                return f"Failed to write file {filename}: {str(e)}"
        else:
            print(f"Failed to generate content for topic: {topic}")
            return "Failed to generate Python code - check console for details"
            
    elif content_type == 'website':
        prompt = WEBSITE_PROMPT_TEMPLATE.format(topic=topic)
        content = generate_content(prompt)
        if content:
            filename = f"{sanitize_filename(topic)}.html"
            
            # Determine where to save the file
            folder_path = vscode_info.get("folder")
            if folder_path and os.path.exists(folder_path):
                filepath = os.path.join(folder_path, filename)
                print(f"Creating file in tracked VSCode folder: {filepath}")
            else:
                # Fallback to current directory
                filepath = os.path.abspath(filename)
                print(f"Creating file in current directory: {filepath}")
                
            try:
                # Make sure we have absolute paths
                abs_filepath = os.path.abspath(filepath)
                
                # Write the content to the file
                with open(abs_filepath, 'w') as f:
                    f.write(content)
                print(f"Successfully wrote to {abs_filepath}")
                
                # Open the HTML file in the default browser (xdg-open for Fedora)
                subprocess.Popen(['xdg-open', abs_filepath])
                return f"Created and opened {filename} in browser"
            except Exception as e:
                print(f"Error writing file {filepath}: {str(e)}")
                return f"Failed to write file {filename}: {str(e)}"
        return "Failed to generate website content - check console for details"
        
    return f"Unsupported content type: {content_type}"