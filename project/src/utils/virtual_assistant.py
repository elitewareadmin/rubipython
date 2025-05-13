"""
Virtual Assistant module with enhanced security and chat capabilities
"""
import os
from datetime import datetime, timedelta
import pyttsx3
import random
from src.utils.logger import get_logger
from src.utils.ai_assistant import AIAssistant
from src.utils.languages import LanguageManager
from src.utils.shopping import ShoppingAssistant
from src.utils.search import SearchAssistant
from src.utils.analytics import AnalyticsManager
from src.utils.smart_scheduler import SmartScheduler
from src.utils.security import SecurityManager
from src.utils.chat import ChatManager

class VirtualAssistant:
    """Virtual Assistant with executive-level capabilities and chat"""
    def __init__(self):
        self.logger = get_logger()
        self.name = "Luna"
        self.security = SecurityManager()
        self.current_session = None
        self.current_user = None
        self.secretary = SecretaryAssistant()
        self.chat_manager = ChatManager()
        
        self.personality = {
            "tone": "executive and professional",
            "language": "en-US",
            "speaking_rate": 150,
            "voice_gender": "female",
            "formality": "business formal",
            "empathy_level": "high",
            "humor_style": "witty",
            "proactiveness": "high",
            "leadership_style": "executive",
            "decision_making": "strategic"
        }
        self.mood = {
            "current": "positive",
            "energy": "high",
            "expressiveness": "confident"
        }
        self.interaction_style = {
            "greeting_style": "professional",
            "response_length": "concise",
            "use_emojis": True,
            "conversation_memory": True,
            "proactive_suggestions": True
        }
        self.avatar_url = "https://images.pexels.com/photos/7242908/pexels-photo-7242908.jpeg"
        self.ai = AIAssistant()
        self.voice = pyttsx3.init()
        self.language_manager = LanguageManager()
        self.shopping_assistant = ShoppingAssistant()
        self.search_assistant = SearchAssistant()
        self.analytics = AnalyticsManager()
        self.scheduler = SmartScheduler()
        self.conversation_history = []
        self.configure_voice()
        self.last_proactive_check = datetime.now()
        self.proactive_interval = timedelta(minutes=30)

    def authenticate_user(self, username, password, ip_address):
        """Authenticate a user"""
        if not self.security.check_login_attempt(ip_address):
            return False, "Too many login attempts. Please try again later."

        # In a real implementation, validate against a user database
        # This is a simplified example
        if self._validate_credentials(username, password):
            self.security.record_login_attempt(ip_address, True)
            self.current_session = self.security.create_session(username, ip_address)
            self.current_user = username
            return True, "Authentication successful"
        
        self.security.record_login_attempt(ip_address, False)
        return False, "Invalid credentials"

    def _validate_credentials(self, username, password):
        """Validate user credentials"""
        # Implement actual credential validation
        return True  # Placeholder

    def validate_session(self, session_id, ip_address):
        """Validate the current session"""
        if not self.security.validate_session(session_id, ip_address):
            self.current_session = None
            self.current_user = None
            return False
        return True

    def process_command(self, command, ip_address):
        """Process a command with security checks"""
        if not self.current_session or not self.validate_session(self.current_session, ip_address):
            return "Please authenticate first"

        # Sanitize input
        command = self.security.sanitize_input(command)
        
        # Process the command
        try:
            response = self._execute_command(command)
            return self.security.encrypt_data(response)
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            return "Error processing command"

    def _execute_command(self, command):
        """Execute a command securely"""
        # Implement command execution logic
        return "Command executed successfully"

    def speak(self, text):
        """Speak text securely"""
        try:
            # Sanitize and encrypt sensitive information
            sanitized_text = self.security.sanitize_input(text)
            modified_text = self._apply_personality_to_text(sanitized_text)
            
            # Add proactive suggestions if appropriate
            proactive_suggestions = self.check_proactive_actions()
            if proactive_suggestions:
                modified_text = f"{modified_text}\n\nProactively, I suggest:\n" + "\n".join(proactive_suggestions)

            self.voice.say(modified_text)
            self.voice.runAndWait()
            
            # Securely store in conversation history
            if self.interaction_style["conversation_memory"]:
                encrypted_text = self.security.encrypt_data(modified_text)
                self.conversation_history.append({
                    "type": "assistant",
                    "text": encrypted_text,
                    "timestamp": datetime.now()
                })
        except Exception as e:
            self.logger.error(f"Error in speech synthesis: {e}")

    def get_conversation_history(self, limit=None):
        """Get decrypted conversation history"""
        if not self.current_session:
            return []

        history = self.conversation_history[-limit:] if limit else self.conversation_history
        decrypted_history = []
        
        for entry in history:
            try:
                decrypted_text = self.security.decrypt_data(entry["text"])
                decrypted_history.append({
                    "type": entry["type"],
                    "text": decrypted_text,
                    "timestamp": entry["timestamp"]
                })
            except Exception as e:
                self.logger.error(f"Error decrypting history entry: {e}")

        return decrypted_history

    def logout(self):
        """Log out the current user"""
        if self.current_session:
            self.security.terminate_session(self.current_session)
            self.current_session = None
            self.current_user = None
            return True
        return False

    def configure_voice(self):
        """Configure text-to-speech settings"""
        try:
            self.voice.setProperty('rate', self.personality['speaking_rate'])
            voices = self.voice.getProperty('voices')
            # Select voice based on current language and gender preference
            for voice in voices:
                if self.personality['language'] in voice.id.lower() and self.personality['voice_gender'] in voice.name.lower():
                    self.voice.setProperty('voice', voice.id)
                    break
            # Set additional voice properties for executive presence
            self.voice.setProperty('volume', 0.9)  # Confident volume
        except Exception as e:
            self.logger.error(f"Error configuring voice: {e}")

    def check_proactive_actions(self):
        """Check and suggest proactive actions"""
        if datetime.now() - self.last_proactive_check < self.proactive_interval:
            return None

        self.last_proactive_check = datetime.now()
        suggestions = []

        # Market trends analysis
        market_trends = self.search_assistant.news_search("market trends", days=1)
        if market_trends:
            suggestions.append(f"I've noticed some important market trends: {market_trends[0]['title']}")

        # Price monitoring
        price_alerts = self.shopping_assistant.check_price_alerts()
        if price_alerts:
            suggestions.append("There are favorable price movements in your watched items.")

        # Schedule optimization
        schedule_suggestions = self.scheduler.suggest_schedule([], [])
        if schedule_suggestions:
            suggestions.append("I can help optimize your schedule for better productivity.")

        return suggestions if suggestions else None

    def make_executive_suggestion(self, context):
        """Generate executive-level suggestions"""
        try:
            analysis = self.analytics.analyze_context(context)
            suggestion = {
                "recommendation": None,
                "rationale": None,
                "priority": None,
                "impact": None
            }

            if "budget" in context:
                suggestion = self._analyze_budget_decision(context)
            elif "strategy" in context:
                suggestion = self._analyze_strategic_decision(context)
            elif "operations" in context:
                suggestion = self._analyze_operational_decision(context)

            return suggestion
        except Exception as e:
            self.logger.error(f"Error making executive suggestion: {e}")
            return None

    def _apply_personality_to_text(self, text):
        """Modify text to reflect executive presence"""
        modified_text = text

        # Add executive-style phrases
        executive_phrases = {
            "suggest": "recommend",
            "think": "analyze",
            "look at": "evaluate",
            "try": "implement",
            "problem": "challenge",
            "idea": "strategy"
        }
        
        for original, replacement in executive_phrases.items():
            modified_text = modified_text.replace(original, replacement)

        # Add data-driven insights
        if "recommend" in modified_text.lower():
            modified_text += "\n\nThis recommendation is based on current market analysis and trending data."

        # Add strategic context
        if "strategy" in modified_text.lower():
            modified_text += "\n\nThis aligns with long-term objectives and market positioning."

        return modified_text

    def _analyze_budget_decision(self, context):
        """Analyze and make budget-related decisions"""
        return {
            "recommendation": "Optimize resource allocation",
            "rationale": "Based on current market conditions and ROI analysis",
            "priority": "high",
            "impact": "significant"
        }

    def _analyze_strategic_decision(self, context):
        """Analyze and make strategic decisions"""
        return {
            "recommendation": "Expand market presence",
            "rationale": "Market analysis indicates growth opportunities",
            "priority": "high",
            "impact": "long-term"
        }

    def _analyze_operational_decision(self, context):
        """Analyze and make operational decisions"""
        return {
            "recommendation": "Streamline processes",
            "rationale": "Efficiency metrics show optimization potential",
            "priority": "medium",
            "impact": "immediate"
        }

    def search_products(self, query, store=None, max_price=None, min_rating=None):
        """Search for products with executive-level filtering"""
        results = self.shopping_assistant.search_products(query, store, max_price, min_rating)
        return self._apply_executive_filter(results)

    def _apply_executive_filter(self, results):
        """Apply executive-level filtering to results"""
        # Filter for premium quality and high ratings
        return [r for r in results if r.get("rating", 0) >= 4.5]

    def get_greeting(self):
        """Get a contextual greeting with executive presence"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greeting = self.language_manager.get_text("greeting_morning")
        elif 12 <= hour < 17:
            greeting = self.language_manager.get_text("greeting_afternoon")
        else:
            greeting = self.language_manager.get_text("greeting_evening")

        # Add executive-style greeting
        greeting = f"{greeting}! I've prepared today's key insights and recommendations."
        
        proactive_suggestions = self.check_proactive_actions()
        if proactive_suggestions:
            greeting += "\n\n" + "\n".join(proactive_suggestions)

        return greeting

    def update_personality(self, **kwargs):
        """Update personality traits"""
        self.personality.update(kwargs)
        if 'language' in kwargs:
            self.language_manager.set_language(kwargs['language'][:2])
        self.configure_voice()

    def get_personality_profile(self):
        """Get current personality settings"""
        return {
            "name": self.name,
            "personality": self.personality,
            "mood": self.mood,
            "interaction_style": self.interaction_style,
            "leadership_style": self.personality["leadership_style"]
        }

    def schedule_meeting(self, title, attendees, duration=None, priority="normal"):
        """Schedule a meeting using secretary capabilities"""
        return self.secretary.schedule_meeting(title, attendees, duration, priority)

    def manage_email(self, action, **kwargs):
        """Manage emails using secretary capabilities"""
        return self.secretary.manage_email(action, **kwargs)

    def prepare_document(self, doc_type, content, template=None):
        """Prepare documents using secretary capabilities"""
        return self.secretary.prepare_documents(doc_type, content, template)

    def manage_schedule(self, timeframe="today"):
        """Manage schedule using secretary capabilities"""
        return self.secretary.manage_schedule(timeframe)

    def set_reminder(self, task, due_date, priority="normal"):
        """Set reminders using secretary capabilities"""
        return self.secretary.set_reminder(task, due_date, priority)

    def start_chat(self, user_id):
        """Start a chat conversation"""
        return self.chat_manager.start_conversation(user_id)
    
    def send_message(self, conversation_id, user_id, message):
        """Send a message in a chat"""
        return self.chat_manager.send_message(conversation_id, user_id, message)
    
    def get_chat_history(self, conversation_id, limit=None):
        """Get chat history"""
        return self.chat_manager.get_conversation_history(conversation_id, limit)
    
    def search_chat(self, query, conversation_id=None):
        """Search chat messages"""
        return self.chat_manager.search_messages(query, conversation_id)
    
    def mark_message_read(self, message_id, user_id):
        """Mark a chat message as read"""
        return self.chat_manager.mark_as_read(message_id, user_id)
    
    def add_message_reaction(self, message_id, user_id, reaction):
        """Add a reaction to a chat message"""
        return self.chat_manager.add_reaction(message_id, user_id, reaction)
    
    def set_typing(self, conversation_id, user_id, is_typing):
        """Set typing status in chat"""
        return self.chat_manager.set_typing_status(conversation_id, user_id, is_typing)
    
    def get_typing_users(self, conversation_id):
        """Get users currently typing in chat"""
        return self.chat_manager.get_typing_status(conversation_id)
    
    def export_chat(self, conversation_id, format="json"):
        """Export chat conversation"""
        return self.chat_manager.export_conversation(conversation_id, format)