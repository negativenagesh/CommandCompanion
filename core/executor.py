"""
Action execution handling for CommandCompanion
"""

from actions.app_launcher import open_app
from actions.system_tasks import system_task
from actions.file_creator import create_file

def execute_action(action_data, context=None):
    """
    Execute a single action based on the interpreted data.
    
    Args:
        action_data (dict): Action data to execute
        context (dict, optional): Context for tracking state between actions
        
    Returns:
        str: Status message about the operation
    """
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
        # This will be handled in the main app to quit the tkinter app
        return "Application closed"
        
    elif action == 'unknown':
        return "Command not understood"
        
    elif action == 'error':
        return f"Error: {action_data.get('message', 'Unknown error')}"
        
    return f"Unknown action: {action}"