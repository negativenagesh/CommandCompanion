"""
Application launcher for CommandCompanion
Optimized for Fedora OS
"""

import subprocess
import os
import uuid
from datetime import datetime
from config.settings import app_aliases
from utils.helpers import is_app_available, ensure_directory_exists

# Track the most recent VSCode window information
vscode_info = {
    "folder": None,
    "window_id": None,
    "timestamp": None
}

def open_app(app_name, reuse_window=False):
    """
    Open an application based on the provided name.
    If it's in aliases, use that command, otherwise try to run the app directly.
    
    Args:
        app_name (str): Name of the application to open
        reuse_window (bool): Whether to reuse existing window (for VSCode)
        
    Returns:
        str: Status message about the operation
    """
    global vscode_info
    
    # Clean app name to prevent shell injection
    app_name = app_name.lower().strip()
    
    # Check if it's a known alias
    app_cmd = app_aliases.get(app_name)
    
    if not app_cmd:
        # If not a known alias, use the app name directly (without special characters)
        app_cmd = ''.join(c for c in app_name if c.isalnum() or c in ' -_.')
    
    # Verify app exists before attempting to run
    if app_cmd and (is_app_available(app_cmd.split()[0]) or os.path.exists(app_cmd.split()[0])):
        cmd = [app_cmd.split()[0]]  # Use only the command, not arguments
        
        # Add additional arguments if needed
        if len(app_cmd.split()) > 1:
            cmd.extend(app_cmd.split()[1:])
            
        # Special handling for VSCode to ensure we can track the new window
        if app_name == 'vscode' and not reuse_window:
            # Create a more permanent workspace folder in the home directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            home_dir = os.path.expanduser("~")
            session_folder = os.path.join(home_dir, f"vscode_workspace_{timestamp}")
            
            # Create the directory if it doesn't exist
            ensure_directory_exists(session_folder)
            
            # Update global tracking info
            vscode_info["folder"] = session_folder
            vscode_info["timestamp"] = timestamp
            vscode_info["window_id"] = str(uuid.uuid4())
            
            # Create a placeholder file in this folder to make sure VSCode shows something
            placeholder_path = os.path.join(session_folder, "README.md")
            with open(placeholder_path, "w") as f:
                f.write(f"# New VSCode Workspace\n\nCreated by CommandCompanion at {timestamp}\n")
            
            # Force a completely new window with the workspace folder
            cmd.extend(["--new-window", session_folder])
            
            try:
                subprocess.Popen(cmd)
                print(f"Opened VSCode with workspace: {session_folder}")
                return f"Opened {app_name} with new workspace"
            except Exception as e:
                return f"Error opening {app_name}: {str(e)}"
        elif app_name == 'vscode' and reuse_window:
            cmd.append('--reuse-window')
        
        try:
            subprocess.Popen(cmd)
            return f"Opened {app_name}"
        except Exception as e:
            return f"Error opening {app_name}: {str(e)}"
    
    return f"Application '{app_name}' not found or not executable"