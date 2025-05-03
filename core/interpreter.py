"""
Command interpretation module for CommandCompanion
"""

import google.generativeai as genai
from config.settings import AI_MODEL, COMMAND_INTERPRETATION_PROMPT
from utils.helpers import extract_json

def interpret_command(prompt):
    """
    Interpret the user's command using Gemini and return a list of actions.
    
    Args:
        prompt (str): The user's natural language command
        
    Returns:
        list: A list of action dictionaries
    """
    try:
        model = genai.GenerativeModel(AI_MODEL)
        response = model.generate_content(COMMAND_INTERPRETATION_PROMPT.format(prompt=prompt))
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