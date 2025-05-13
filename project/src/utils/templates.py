"""
Templates module for document management
"""
import os
import json
from datetime import datetime
from src.utils.logger import get_logger

class TemplateManager:
    """Template Manager for handling document templates"""
    def __init__(self, templates_dir="data/templates"):
        self.logger = get_logger()
        self.templates_dir = templates_dir
        self.templates = {}
        self.load_templates()
    
    def load_templates(self):
        """Load templates from the templates directory"""
        try:
            os.makedirs(self.templates_dir, exist_ok=True)
            
            if os.path.exists(os.path.join(self.templates_dir, "templates.json")):
                with open(os.path.join(self.templates_dir, "templates.json"), "r") as f:
                    self.templates = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading templates: {e}")
    
    def save_templates(self):
        """Save templates to file"""
        try:
            with open(os.path.join(self.templates_dir, "templates.json"), "w") as f:
                json.dump(self.templates, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving templates: {e}")
    
    def add_template(self, name, content, variables=None):
        """Add a new template"""
        template = {
            "name": name,
            "content": content,
            "variables": variables or [],
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat()
        }
        self.templates[name] = template
        self.save_templates()
        return template
    
    def get_template(self, name):
        """Get a template by name"""
        return self.templates.get(name)
    
    def fill_template(self, name, variables):
        """Fill a template with variables"""
        template = self.get_template(name)
        if not template:
            return None
        
        content = template["content"]
        for var_name, value in variables.items():
            content = content.replace(f"{{{var_name}}}", str(value))
        
        return content