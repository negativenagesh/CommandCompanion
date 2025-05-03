"""
Command interpretation module for CommandCompanion
"""

import json
import google.generativeai as genai
from config.settings import AI_MODEL, COMMAND_INTERPRETATION_PROMPT
from utils.helpers import extract_json

def interpret_command(prompt):
    """Interpret the user's command using Gemini."""
    try:
        model = genai.GenerativeModel(AI_MODEL)
        print(f"Sending prompt to Gemini: '{prompt}'")
        response = model.generate_content(COMMAND_INTERPRETATION_PROMPT.format(prompt=prompt))
        response_text = response.text.strip()
        print(f"Raw Gemini response: {response_text}")
        
        data = extract_json(response_text)
        if data:
            # Successfully parsed the response
            print(f"Successfully parsed JSON: {json.dumps(data, indent=2)}")
            if isinstance(data, list):
                return data
            else:
                return [data]
        else:
            print(f"Failed to parse JSON from response")
            return [{"action": "error", "message": "Invalid response from Gemini"}]
    except Exception as e:
        print(f"Error interpreting command: {str(e)}")
        return [{"action": "error", "message": str(e)}]