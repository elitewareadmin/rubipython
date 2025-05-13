"""
Language support module
Provides translations and language management
"""
from src.utils.logger import get_logger

class LanguageManager:
    """Language Manager for handling translations"""
    def __init__(self):
        self.logger = get_logger()
        self.current_language = "en"
        self.translations = {
            "en": {
                "greeting_morning": "Good morning",
                "greeting_afternoon": "Good afternoon",
                "greeting_evening": "Good evening",
                "intro": "I'm {name}, your virtual assistant.",
                "processing": "I'll help you with: {command}",
                "error": "I'm sorry, I couldn't process that command.",
                "task_added": "Task added successfully!",
                "task_completed": "Task completed successfully!",
                "task_updated": "Task updated successfully!"
            },
            "es": {
                "greeting_morning": "Buenos días",
                "greeting_afternoon": "Buenas tardes",
                "greeting_evening": "Buenas noches",
                "intro": "Soy {name}, tu asistente virtual.",
                "processing": "Te ayudaré con: {command}",
                "error": "Lo siento, no pude procesar ese comando.",
                "task_added": "¡Tarea añadida con éxito!",
                "task_completed": "¡Tarea completada con éxito!",
                "task_updated": "¡Tarea actualizada con éxito!"
            },
            "fr": {
                "greeting_morning": "Bonjour",
                "greeting_afternoon": "Bon après-midi",
                "greeting_evening": "Bonsoir",
                "intro": "Je suis {name}, votre assistant virtuel.",
                "processing": "Je vais vous aider avec : {command}",
                "error": "Désolé, je n'ai pas pu traiter cette commande.",
                "task_added": "Tâche ajoutée avec succès !",
                "task_completed": "Tâche terminée avec succès !",
                "task_updated": "Tâche mise à jour avec succès !"
            }
        }
    
    def get_text(self, key, **kwargs):
        """Get translated text for a key"""
        try:
            text = self.translations[self.current_language][key]
            return text.format(**kwargs) if kwargs else text
        except KeyError:
            self.logger.error(f"Missing translation for key: {key}")
            return self.translations["en"][key]  # Fallback to English
        except Exception as e:
            self.logger.error(f"Error getting translation: {e}")
            return key  # Return key as fallback
    
    def set_language(self, language_code):
        """Set the current language"""
        if language_code in self.translations:
            self.current_language = language_code
            return True
        return False
    
    def get_available_languages(self):
        """Get list of available languages"""
        return list(self.translations.keys())
    
    def add_language(self, language_code, translations):
        """Add a new language"""
        self.translations[language_code] = translations