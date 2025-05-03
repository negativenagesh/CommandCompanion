"""
CommandCompanion - Main entry point
An AI-powered command assistant for Fedora Linux
"""
import sys
import os
import time
import tkinter as tk
from dotenv import load_dotenv
import google.generativeai as genai

# Add the package to the Python path when run as a script
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    __package__ = "commandcompanion"

# Import components from other modules
from .config.settings import GUI_TITLE, GUI_SIZE, GUI_CONFIG
from .core.interpreter import interpret_command
from .core.executor import execute_action
from .gui.interface import create_interface

def main():
    # Load environment variables for API keys
    config_dir = os.path.join(os.path.expanduser("~"), ".config", "commandcompanion")
    env_path = os.path.join(config_dir, ".env")
    
    # Create config directory if it doesn't exist
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    # Check if .env exists, create template if it doesn't
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write("# Set your Gemini API key here\n")
            f.write("GENAI_API_KEY=your_api_key_here\n")
    
    load_dotenv(env_path)
    
    # Configure the Gemini API
    api_key = os.getenv('GENAI_API_KEY')
    if api_key and api_key != "your_api_key_here":
        genai.configure(api_key=api_key)
    else:
        print("Warning: No valid API key found. Please edit ~/.config/commandcompanion/.env")
        # You might want to show a dialog prompting for the API key
    
    # Create main application window
    root = tk.Tk()
    app = CommandCompanion(root)
    root.mainloop()

class CommandCompanion:
    def __init__(self, root):
        self.root = root
        self.root.title(GUI_TITLE)
        self.root.geometry(GUI_SIZE)
        self.root.configure(bg=GUI_CONFIG["bg_color"])
        
        # Set application icon
        try:
            icon_path = self._get_resource_path("icons/commandcompanion.png")
            if os.path.exists(icon_path):
                img = tk.PhotoImage(file=icon_path)
                self.root.tk.call('wm', 'iconphoto', self.root._w, img)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Create the user interface
        self.entry, self.status_label = create_interface(self.root, self.on_submit)
        
        # Bind Enter key to submit
        self.root.bind('<Return>', lambda event: self.on_submit())
    
    def _get_resource_path(self, resource):
        # First check local package
        package_path = os.path.join(os.path.dirname(__file__), "resources", resource)
        if os.path.exists(package_path):
            return package_path
        
        # Then check system path
        system_path = os.path.join("/usr/share/commandcompanion", resource)
        if os.path.exists(system_path):
            return system_path
        
        return None
    
    def on_submit(self):
        """Handle the submit button press."""
        user_input = self.entry.get().strip()
        if user_input:
            # Interpret the command
            actions = interpret_command(user_input)
            status_messages = []
            context = {}  # Context to track if VSCode was opened
            
            # Execute each action
            for i, action_data in enumerate(actions):
                # For multi-step commands involving VSCode, add extra delay
                if i > 0 and action_data.get('action') == 'create_file' and actions[i-1].get('action') == 'open_app' and actions[i-1].get('app', '').lower() == 'vscode':
                    print("Waiting for VSCode to fully initialize before creating file...")
                    time.sleep(3)  # Increased wait time for VSCode to fully initialize
                
                # Special handling for quit action
                if action_data.get('action') == 'quit':
                    self.root.quit()
                    return
                
                # Execute the action and get status
                status = execute_action(action_data, context)
                status_messages.append(status)
            
            # Update status display
            self.status_label.config(text="; ".join(status_messages))
            self.entry.delete(0, tk.END)  # Clear the input field

if __name__ == "__main__":
    main()