import json
import os

RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')

def load_file(filename):
    """Loads text content from a file in the resources directory."""
    path = os.path.join(RESOURCES_DIR, filename)
    if not os.path.exists(path):
        return f"Error: {filename} not found."
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def load_json_template(key):
    """Loads a specific template from the input_templates.json file."""
    path = os.path.join(RESOURCES_DIR, 'input_templates.json')
    if not os.path.exists(path):
        return {}
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get(key, {})

def get_style_guide():
    return load_file('style_guide.md')

def get_company_info():
    return load_file('company_info.md')

def load_master_prompt():
    """Loads the immutable master prompt from file."""
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'C1_MASTER_PROMPT.md')
    if not os.path.exists(path):
        return "Error: C1_MASTER_PROMPT.md not found."
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
