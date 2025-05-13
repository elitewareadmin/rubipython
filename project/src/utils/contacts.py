"""
Contacts management module
"""
import os
import json
from datetime import datetime
from src.utils.logger import get_logger

class ContactManager:
    """Contact Manager for handling contacts"""
    def __init__(self, contacts_file="data/contacts.json"):
        self.logger = get_logger()
        self.contacts_file = contacts_file
        self.contacts = {}
        self.load_contacts()
    
    def load_contacts(self):
        """Load contacts from file"""
        try:
            os.makedirs(os.path.dirname(self.contacts_file), exist_ok=True)
            
            if os.path.exists(self.contacts_file):
                with open(self.contacts_file, "r") as f:
                    self.contacts = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading contacts: {e}")
    
    def save_contacts(self):
        """Save contacts to file"""
        try:
            with open(self.contacts_file, "w") as f:
                json.dump(self.contacts, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving contacts: {e}")
    
    def add_contact(self, name, email, phone=None, company=None, notes=None):
        """Add a new contact"""
        contact = {
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "notes": notes,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat()
        }
        self.contacts[email] = contact
        self.save_contacts()
        return contact
    
    def update_contact(self, email, **kwargs):
        """Update a contact"""
        if email in self.contacts:
            self.contacts[email].update(kwargs)
            self.contacts[email]["modified"] = datetime.now().isoformat()
            self.save_contacts()
            return self.contacts[email]
        return None
    
    def get_contact(self, email):
        """Get a contact by email"""
        return self.contacts.get(email)
    
    def search_contacts(self, query):
        """Search contacts"""
        query = query.lower()
        results = []
        
        for contact in self.contacts.values():
            if (query in contact["name"].lower() or
                query in contact["email"].lower() or
                (contact["company"] and query in contact["company"].lower())):
                results.append(contact)
        
        return results
    
    def get_all_contacts(self):
        """Get all contacts"""
        return list(self.contacts.values())