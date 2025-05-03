"""
System task handlers for CommandCompanion
Optimized for Fedora OS
"""

import subprocess
from config.settings import allowed_tasks

def system_task(task_name):
    """
    Perform a predefined system task.
    
    Args:
        task_name (str): The name of the task to perform
        
    Returns:
        str: Status message about the operation
    """
    command = allowed_tasks.get(task_name.lower())
    if command:
        try:
            subprocess.run(command, shell=True)
            return f"Performed task: {task_name}"
        except Exception as e:
            return f"Error performing task {task_name}: {str(e)}"
    return f"Task '{task_name}' not allowed"