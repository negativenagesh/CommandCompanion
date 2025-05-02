import subprocess
import tkinter as tk
from tkinter import ttk
import os
import json
import re
import time
import google.generativeai as genai
import shutil
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GENAI_API_KEY'))

# Allowed apps and system tasks for security
app_aliases = {
    'vscode': 'code',
    'trash': 'nautilus trash:///',
    'brave': 'brave-browser',
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

allowed_tasks = {
    'empty_trash': 'rm -rf ~/.local/share/Trash/*'
}

def is_app_available(app_cmd):
    """Check if an application exists in the system path."""
    return shutil.which(app_cmd) is not None

def open_app(app_name, reuse_window=False):
    """Open an application based on the provided name.
    If it's in aliases, use that command, otherwise try to run the app directly."""
    
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
            
        # Add special handling for VSCode
        if app_name == 'vscode' and reuse_window:
            cmd.append('--reuse-window')
            
        try:
            subprocess.Popen(cmd)
            return f"Opened {app_name}"
        except Exception as e:
            return f"Error opening {app_name}: {str(e)}"
    
    return f"Application '{app_name}' not found or not executable"

def system_task(task_name):
    """Perform a predefined system task."""
    command = allowed_tasks.get(task_name.lower())
    if command:
        subprocess.run(command, shell=True)
        return f"Performed task: {task_name}"
    return f"Task '{task_name}' not allowed"

def generate_content(prompt):
    """Generate content (e.g., code, HTML) using Gemini with detailed debugging."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
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
    """Create a file with generated content and open it in the same VSCode instance if specified."""
    if content_type == 'python':
        prompt = (
            f"Generate complete, executable Python code for '{topic}'. "
            f"Include all necessary imports (e.g., torch for PyTorch, numpy, etc.) and ensure the code is functional and ready to run. "
            f"Do not include explanations, markdown, or code fences (```); return only the raw Python code."
        )
        content = generate_content(prompt)
        if content:
            filename = f"{topic.replace(' ', '_')}.py"
            try:
                with open(filename, 'w') as f:
                    f.write(content)
                cmd = ['code', filename]
                if reuse_vscode:
                    cmd.append('--reuse-window')
                subprocess.Popen(cmd)
                return f"Created and opened {filename}"
            except Exception as e:
                print(f"Error writing file {filename}: {str(e)}")
                return f"Failed to write file {filename}"
        else:
            print(f"Failed to generate content for topic: {topic}")
            return "Failed to generate Python code - check console for details"
    elif content_type == 'website':
        prompt = (
            f"Generate complete HTML code for a '{topic}' website. "
            f"Include basic styling within <style> tags and a clear structure. "
            f"Do not include explanations or markdown; return only the raw HTML code."
        )
        content = generate_content(prompt)
        if content:
            filename = f"{topic.replace(' ', '_')}.html"
            try:
                with open(filename, 'w') as f:
                    f.write(content)
                subprocess.Popen(['xdg-open', filename])
                return f"Created and opened {filename}"
            except Exception as e:
                print(f"Error writing file {filename}: {str(e)}")
                return f"Failed to write file {filename}"
        return "Failed to generate website content - check console for details"
    return f"Unsupported content type: {content_type}"

def extract_json(text):
    """Extract JSON object or array from the response text."""
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

def interpret_command(prompt):
    """Interpret the user's command using Gemini and return a list of actions."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            f"You are an assistant that interprets natural language commands for an Ubuntu Linux system. "
            f"Based on the command, return a JSON object or an array of JSON objects with the following structure:\n"
            f"- For opening any application: {{'action': 'open_app', 'app': '<app_name>'}}\n"
            f"- For performing a system task: {{'action': 'system_task', 'task': '<task_name>'}}\n"
            f"- For creating a file with generated content: {{'action': 'create_file', 'type': '<content_type>', 'topic': '<topic>'}}\n"
            f"- For quitting the application: {{'action': 'quit'}}\n"
            f"If the command is unclear or doesn't match any action, return {{'action': 'unknown'}}.\n"
            f"For multi-step commands, return an array of actions.\n"
            f"The system can now open ANY application available on the Linux system, not just predefined ones.\n"
            f"Examples:\n"
            f"- 'open VSCode': {{'action': 'open_app', 'app': 'vscode'}}\n"
            f"- 'open Firefox': {{'action': 'open_app', 'app': 'firefox'}}\n"
            f"- 'launch GIMP': {{'action': 'open_app', 'app': 'gimp'}}\n"
            f"- 'run calculator': {{'action': 'open_app', 'app': 'gnome-calculator'}}\n"
            f"- 'empty the trash': {{'action': 'system_task', 'task': 'empty_trash'}}\n"
            f"- 'build a portfolio website': {{'action': 'create_file', 'type': 'website', 'topic': 'portfolio'}}\n"
            f"- 'open VSCode and create a Python file for a CNN model': [{{\"action\": \"open_app\", \"app\": \"vscode\"}}, {{\"action\": \"create_file\", \"type\": \"python\", \"topic\": \"CNN model\"}}]\n"
            f"Command: '{prompt}'"
        )
        response_text = response.text.strip()
        data = extract_json(response_text)
        if data:
            if isinstance(data, list):
                return data
            else:
                return [data]
        else:
            print(f"Invalid JSON response: {response_text}")
            return [{"action": "error", "message": "Invalid response from Gemini"}]
    except Exception as e:
        print(f"Error interpreting command: {str(e)}")
        return [{"action": "error", "message": str(e)}]

def execute_action(action_data, context=None):
    """Execute a single action based on the interpreted data, with context for VSCode reuse."""
    if context is None:
        context = {}
    
    action = action_data.get('action')
    if action == 'open_app':
        app = action_data.get('app')
        if app:
            # If opening VSCode, mark it in context for reuse
            reuse_window = context.get('vscode_opened', False)
            result = open_app(app, reuse_window=reuse_window)
            if app.lower() == 'vscode':
                context['vscode_opened'] = True
            return result
        return "Missing app parameter"
    elif action == 'system_task':
        task = action_data.get('task')
        return system_task(task) if task else "Missing task parameter"
    elif action == 'create_file':
        content_type = action_data.get('type')
        topic = action_data.get('topic')
        if content_type and topic:
            # Reuse VSCode window if it was previously opened
            reuse_vscode = context.get('vscode_opened', False)
            return create_file(content_type, topic, reuse_vscode=reuse_vscode)
        return "Missing type or topic parameter"
    elif action == 'quit':
        root.quit()
        return "Application closed"
    elif action == 'unknown':
        return "Command not understood"
    elif action == 'error':
        return f"Error: {action_data.get('message', 'Unknown error')}"
    return f"Unknown action: {action}"

def on_submit():
    """Handle the submit button press."""
    user_input = entry.get().strip()
    if user_input:
        actions = interpret_command(user_input)
        status_messages = []
        context = {}  # Context to track if VSCode was opened
        for action_data in actions:
            status = execute_action(action_data, context)
            status_messages.append(status)
            # Small delay to ensure VSCode has time to open before next action
            if action_data.get('action') == 'open_app' and action_data.get('app', '').lower() == 'vscode':
                time.sleep(1)  # Wait 1 second for VSCode to initialize
        status_label.config(text="; ".join(status_messages))
        entry.delete(0, tk.END)  # Clear the input field

# Create the GUI
root = tk.Tk()
root.title("Ubuntu Command Executor")
root.geometry("500x250")

# Instructions
instructions = tk.Label(root, text="Type a command (e.g., 'open VSCode and build a PyTorch CNN model for MNIST', 'build a portfolio website'):")
instructions.pack(pady=10)

# Input field
entry = tk.Entry(root, width=50)
entry.pack(pady=5)
entry.focus()

# Submit button
submit_btn = ttk.Button(root, text="Execute", command=on_submit)
submit_btn.pack(pady=5)

# Status label
status_label = tk.Label(root, text="Ready", wraplength=450)
status_label.pack(pady=10)

# Bind Enter key to submit
root.bind('<Return>', lambda event: on_submit())

# Start the application
root.mainloop()
