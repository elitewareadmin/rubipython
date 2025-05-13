"""
Chat module for real-time messaging and conversation management
"""
from datetime import datetime
import json
from src.utils.logger import get_logger
from src.utils.ai_assistant import AIAssistant
from src.utils.security import SecurityManager

class ChatManager:
    """Chat Manager for handling real-time conversations"""
    def __init__(self):
        self.logger = get_logger()
        self.security = SecurityManager()
        self.ai = AIAssistant()
        self.conversations = {}
        self.active_users = set()
        self.chat_history = {}
        self.message_queue = []
        self.typing_status = {}
        self.read_receipts = {}
        
    def start_conversation(self, user_id, conversation_type="direct"):
        """Start a new conversation"""
        try:
            conversation_id = f"chat_{len(self.conversations) + 1}"
            conversation = {
                "id": conversation_id,
                "type": conversation_type,
                "participants": [user_id],
                "messages": [],
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "status": "active"
            }
            
            self.conversations[conversation_id] = conversation
            self.chat_history[conversation_id] = []
            return conversation_id
        except Exception as e:
            self.logger.error(f"Error starting conversation: {e}")
            return None
    
    def send_message(self, conversation_id, user_id, content, message_type="text"):
        """Send a message in a conversation"""
        try:
            conversation = self.conversations.get(conversation_id)
            if not conversation:
                return False, "Conversation not found"
            
            # Validate and sanitize content
            content = self.security.sanitize_input(content)
            
            message = {
                "id": f"msg_{len(conversation['messages']) + 1}",
                "conversation_id": conversation_id,
                "user_id": user_id,
                "content": content,
                "type": message_type,
                "timestamp": datetime.now(),
                "status": "sent",
                "read_by": set(),
                "reactions": {}
            }
            
            # Process message content
            processed_message = self._process_message(message)
            conversation["messages"].append(processed_message)
            conversation["last_activity"] = datetime.now()
            
            # Update chat history
            self.chat_history[conversation_id].append(processed_message)
            
            # Generate AI response if needed
            if self._should_generate_response(processed_message):
                ai_response = self._generate_ai_response(processed_message)
                if ai_response:
                    self.send_message(conversation_id, "ai_assistant", ai_response)
            
            return True, message["id"]
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return False, str(e)
    
    def get_conversation_history(self, conversation_id, limit=None):
        """Get conversation history"""
        try:
            history = self.chat_history.get(conversation_id, [])
            if limit:
                history = history[-limit:]
            
            # Decrypt messages
            decrypted_history = []
            for message in history:
                try:
                    decrypted_content = self.security.decrypt_data(message["content"])
                    message_copy = message.copy()
                    message_copy["content"] = decrypted_content
                    decrypted_history.append(message_copy)
                except Exception as e:
                    self.logger.error(f"Error decrypting message: {e}")
            
            return decrypted_history
        except Exception as e:
            self.logger.error(f"Error getting conversation history: {e}")
            return []
    
    def mark_as_read(self, message_id, user_id):
        """Mark a message as read"""
        try:
            for conversation in self.conversations.values():
                for message in conversation["messages"]:
                    if message["id"] == message_id:
                        message["read_by"].add(user_id)
                        message["status"] = "read"
                        return True
            return False
        except Exception as e:
            self.logger.error(f"Error marking message as read: {e}")
            return False
    
    def add_reaction(self, message_id, user_id, reaction):
        """Add a reaction to a message"""
        try:
            for conversation in self.conversations.values():
                for message in conversation["messages"]:
                    if message["id"] == message_id:
                        message["reactions"][user_id] = reaction
                        return True
            return False
        except Exception as e:
            self.logger.error(f"Error adding reaction: {e}")
            return False
    
    def set_typing_status(self, conversation_id, user_id, is_typing):
        """Set user typing status"""
        try:
            if conversation_id not in self.typing_status:
                self.typing_status[conversation_id] = {}
            
            self.typing_status[conversation_id][user_id] = {
                "status": is_typing,
                "timestamp": datetime.now()
            }
            return True
        except Exception as e:
            self.logger.error(f"Error setting typing status: {e}")
            return False
    
    def get_typing_status(self, conversation_id):
        """Get typing status for a conversation"""
        try:
            typing_users = []
            current_time = datetime.now()
            
            if conversation_id in self.typing_status:
                for user_id, status in self.typing_status[conversation_id].items():
                    # Check if typing status is recent (within last 5 seconds)
                    if (status["status"] and 
                        (current_time - status["timestamp"]).seconds < 5):
                        typing_users.append(user_id)
            
            return typing_users
        except Exception as e:
            self.logger.error(f"Error getting typing status: {e}")
            return []
    
    def search_messages(self, query, conversation_id=None):
        """Search messages in conversations"""
        try:
            results = []
            query = query.lower()
            
            conversations_to_search = ([self.conversations[conversation_id]] 
                                     if conversation_id 
                                     else self.conversations.values())
            
            for conversation in conversations_to_search:
                for message in conversation["messages"]:
                    decrypted_content = self.security.decrypt_data(message["content"])
                    if query in decrypted_content.lower():
                        results.append({
                            "conversation_id": conversation["id"],
                            "message": message
                        })
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching messages: {e}")
            return []
    
    def _process_message(self, message):
        """Process and enhance message content"""
        try:
            # Encrypt message content
            message["content"] = self.security.encrypt_data(message["content"])
            
            # Add metadata
            message["metadata"] = {
                "client_timestamp": datetime.now(),
                "processed": True
            }
            
            return message
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return message
    
    def _should_generate_response(self, message):
        """Determine if an AI response should be generated"""
        # Add logic to determine when AI should respond
        return True
    
    def _generate_ai_response(self, message):
        """Generate an AI response to a message"""
        try:
            # Decrypt message for processing
            decrypted_content = self.security.decrypt_data(message["content"])
            
            # Generate response using AI assistant
            response = self.ai.generate_response(decrypted_content)
            
            return response
        except Exception as e:
            self.logger.error(f"Error generating AI response: {e}")
            return None
    
    def export_conversation(self, conversation_id, format="json"):
        """Export conversation history in various formats"""
        try:
            history = self.get_conversation_history(conversation_id)
            
            if format == "json":
                return json.dumps(history, default=str, indent=2)
            elif format == "text":
                return self._format_text_export(history)
            else:
                return None
        except Exception as e:
            self.logger.error(f"Error exporting conversation: {e}")
            return None
    
    def _format_text_export(self, history):
        """Format conversation history as text"""
        text = []
        for message in history:
            timestamp = message["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            text.append(f"[{timestamp}] {message['user_id']}: {message['content']}")
        return "\n".join(text)