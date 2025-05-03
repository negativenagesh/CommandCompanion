"""
CommandCompanion - Main entry point
An AI-powered command assistant for Fedora Linux
"""

import os
import time
import tkinter as tk
from dotenv import load_dotenv
import google.generativeai as genai

# Import components from other modules
from config.settings import GUI_TITLE, GUI_SIZE, GUI_CONFIG
from core.interpreter import interpret_command
from core.executor import execute_action
from gui.interface import create_interface

# Load environment variables for API keys
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv('GENAI_API_KEY'))

class CommandCompanion:
    def __init__(self, root):
        self.root = root
        self.root.title(GUI_TITLE)
        self.root.geometry(GUI_SIZE)
        self.root.configure(bg=GUI_CONFIG["bg_color"])
        
        # Create the user interface
        self.entry, self.status_label = create_interface(self.root, self.on_submit)
        
        # Bind Enter key to submit
        self.root.bind('<Return>', lambda event: self.on_submit())
    
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

def main():
    # Create main application window
    root = tk.Tk()
    app = CommandCompanion(root)
    root.mainloop()

if __name__ == "__main__":
    main()