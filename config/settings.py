"""
Configuration settings for CommandCompanion
Optimized for Fedora OS
"""

import os
import shutil
import subprocess

GUI_TITLE = "CommandCompanion"
GUI_SIZE = "650x320"
GUI_CONFIG = {
    "bg_color": "#f0f4f8",
    "header_bg": "#2c3e50",
    "title_font": ("Helvetica", 16, "bold"),
    "normal_font": ("Helvetica", 11),
    "status_font": ("Helvetica", 10),
    "button_bg": "#3498db",
    "button_active_bg": "#2980b9",
    "footer_bg": "#ecf0f1",
    "footer_fg": "#7f8c8d"
}

def get_brave_executable():
    """
    Find the correct Brave browser executable for Fedora.
    Returns the full command with any necessary flags.
    """
    # Check possible executable names for Brave on Fedora
    possible_names = ['brave-browser', 'brave', 'brave-browser-stable', 'brave-browser-beta', 'brave-bin']
    for name in possible_names:
        path = shutil.which(name)
        if path:
            return path
    
    # Check common installation paths if executable not in PATH
    common_paths = [
        '/usr/bin/brave-browser',
        '/usr/bin/brave',
        '/opt/brave.com/brave/brave-browser',
        '/opt/brave/brave',
        '/usr/lib/brave-browser/brave-browser',
        '/app/bin/brave'  # For Flatpak installation
    ]
    for path in common_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    
    # Try flatpak command as a last resort
    flatpak_path = shutil.which('flatpak')
    if flatpak_path:
        # Check if Brave is installed via Flatpak
        try:
            result = subprocess.run(['flatpak', 'list', '--app'], 
                              capture_output=True, text=True)
            if 'com.brave.Browser' in result.stdout:
                return 'flatpak run com.brave.Browser'
        except:
            pass
    
    print("WARNING: Could not find Brave browser executable")
    return 'brave-browser'  # Fall back to default name

app_aliases = {
    'vscode': 'code',
    'trash': 'nautilus trash:///',
    'brave': get_brave_executable(),
    'firefox': 'firefox',
    'terminal': 'gnome-terminal',
    'files': 'nautilus',
    'chrome': 'google-chrome',
    'libreoffice': 'libreoffice',
    'calculator': 'gnome-calculator',
    'gedit': 'gedit',
    'text editor': 'gedit',
    'vlc': 'vlc',
    'settings': 'gnome-control-center'
}

# Allowed system tasks for security
allowed_tasks = {
    'empty_trash': 'rm -rf ~/.local/share/Trash/*'
}

# AI model configuration
AI_MODEL = 'gemini-1.5-flash'

# Prompt templates
PYTHON_PROMPT_TEMPLATE = (
    "Generate complete, executable Python code for '{topic}'. "
    "Include all necessary imports (e.g., torch for PyTorch, numpy, etc.) and ensure the code is functional and ready to run. "
    "Do not include explanations, markdown, or code fences (```); return only the raw Python code."
)

WEBSITE_PROMPT_TEMPLATE = (
    "Generate complete HTML code for a '{topic}' website. "
    "Include basic styling within <style> tags and a clear structure. "
    "Do not include explanations or markdown; return only the raw HTML code."
)

COMMAND_INTERPRETATION_PROMPT = (
    "You are an assistant that interprets natural language commands for a Fedora Linux system. "
    "Based on the command, return a JSON object or an array of JSON objects with the following structure:\n"
    "- For opening any application: {{'action': 'open_app', 'app': '<app_name>'}}\n"
    "- For performing a system task: {{'action': 'system_task', 'task': '<task_name>'}}\n"
    "- For creating a file with generated content: {{'action': 'create_file', 'type': '<content_type>', 'topic': '<topic>'}}\n"
    "- For quitting the application: {{'action': 'quit'}}\n"
    "If the command is unclear or doesn't match any action, return {{'action': 'unknown'}}.\n"
    "For multi-step commands, return an array of actions.\n"
    "The system can now open ANY application available on the Linux system, not just predefined ones.\n"
    "Examples:\n"
    "- 'open VSCode': {{'action': 'open_app', 'app': 'vscode'}}\n"
    "- 'open Firefox': {{'action': 'open_app', 'app': 'firefox'}}\n"
    "- 'launch GIMP': {{'action': 'open_app', 'app': 'gimp'}}\n"
    "- 'run calculator': {{'action': 'open_app', 'app': 'gnome-calculator'}}\n"
    "- 'empty the trash': {{'action': 'system_task', 'task': 'empty_trash'}}\n"
    "- 'build a portfolio website': {{'action': 'create_file', 'type': 'website', 'topic': 'portfolio'}}\n"
    "- 'open VSCode and create a Python file for a CNN model': [{{'action': 'open_app', 'app': 'vscode'}}, {{'action': 'create_file', 'type': 'python', 'topic': 'CNN model'}}]\n"
    "Command: '{prompt}'"
)