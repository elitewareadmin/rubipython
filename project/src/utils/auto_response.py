"""
Auto-response module
Provides automatic response generation functionality
"""
from datetime import datetime, timedelta
from src.utils.logger import get_logger

class AutoResponseManager:
    """Auto Response Manager for handling automated responses"""
    def __init__(self):
        self.logger = get_logger()
        self.templates = {
            "out_of_office": "I am currently out of the office until {return_date}. "
                           "For urgent matters, please contact {alternate_contact}.",
            
            "meeting_scheduled": "Your meeting '{meeting_title}' has been scheduled for "
                               "{meeting_date} at {meeting_time}. Location: {location}",
            
            "task_completed": "The task '{task_title}' has been completed. "
                            "Status: {status}\nNotes: {notes}",
            
            "deadline_reminder": "Reminder: The task '{task_title}' is due on {due_date}. "
                               "Current progress: {progress}%",
            
            "meeting_reminder": "Reminder: You have a meeting '{meeting_title}' in "
                              "{time_until} minutes."
        }
    
    def generate_response(self, template_name, **kwargs):
        """Generate an automatic response using a template"""
        if template_name not in self.templates:
            return None
        
        template = self.templates[template_name]
        try:
            response = template.format(**kwargs)
            return response
        except KeyError as e:
            self.logger.error(f"Missing template variable: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return None
    
    def add_template(self, name, template):
        """Add a new response template"""
        self.templates[name] = template
    
    def get_template(self, name):
        """Get a response template"""
        return self.templates.get(name)
    
    def update_template(self, name, template):
        """Update an existing response template"""
        if name in self.templates:
            self.templates[name] = template
            return True
        return False