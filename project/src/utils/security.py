"""
Security module for protecting virtual assistant data and interactions
"""
import os
import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from src.utils.logger import get_logger

class SecurityManager:
    """Security Manager for handling authentication and encryption"""
    def __init__(self):
        self.logger = get_logger()
        self.secret_key = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
        self.encryption_key = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
        self.fernet = Fernet(self.encryption_key)
        self.session_duration = timedelta(hours=24)
        self.max_login_attempts = 3
        self.login_attempts = {}
        self.blocked_ips = set()
        self.active_sessions = {}
    
    def hash_password(self, password):
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    def verify_password(self, password, hashed):
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode(), hashed)
    
    def generate_token(self, user_id, ip_address):
        """Generate a JWT token for authentication"""
        try:
            payload = {
                'user_id': user_id,
                'ip': ip_address,
                'exp': datetime.utcnow() + self.session_duration
            }
            return jwt.encode(payload, self.secret_key, algorithm='HS256')
        except Exception as e:
            self.logger.error(f"Error generating token: {e}")
            return None
    
    def verify_token(self, token, ip_address):
        """Verify a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            if payload['ip'] != ip_address:
                raise jwt.InvalidTokenError("IP address mismatch")
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {e}")
            return None
    
    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        try:
            return self.fernet.encrypt(data.encode())
        except Exception as e:
            self.logger.error(f"Error encrypting data: {e}")
            return None
    
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        try:
            return self.fernet.decrypt(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"Error decrypting data: {e}")
            return None
    
    def check_login_attempt(self, ip_address):
        """Check if login is allowed for this IP"""
        if ip_address in self.blocked_ips:
            return False
        
        attempts = self.login_attempts.get(ip_address, {'count': 0, 'last_attempt': None})
        
        # Reset attempts if last attempt was more than 1 hour ago
        if attempts['last_attempt'] and \
           datetime.now() - attempts['last_attempt'] > timedelta(hours=1):
            attempts['count'] = 0
        
        return attempts['count'] < self.max_login_attempts
    
    def record_login_attempt(self, ip_address, success):
        """Record a login attempt"""
        if ip_address not in self.login_attempts:
            self.login_attempts[ip_address] = {'count': 0, 'last_attempt': None}
        
        if not success:
            self.login_attempts[ip_address]['count'] += 1
            if self.login_attempts[ip_address]['count'] >= self.max_login_attempts:
                self.blocked_ips.add(ip_address)
        else:
            self.login_attempts[ip_address]['count'] = 0
        
        self.login_attempts[ip_address]['last_attempt'] = datetime.now()
    
    def create_session(self, user_id, ip_address):
        """Create a new session"""
        session_id = secrets.token_hex(16)
        self.active_sessions[session_id] = {
            'user_id': user_id,
            'ip_address': ip_address,
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        return session_id
    
    def validate_session(self, session_id, ip_address):
        """Validate a session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        if session['ip_address'] != ip_address:
            self.terminate_session(session_id)
            return False
        
        if datetime.now() - session['created_at'] > self.session_duration:
            self.terminate_session(session_id)
            return False
        
        session['last_activity'] = datetime.now()
        return True
    
    def terminate_session(self, session_id):
        """Terminate a session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def sanitize_input(self, input_str):
        """Sanitize user input"""
        # Remove potentially dangerous characters
        sanitized = ''.join(char for char in input_str 
                          if char.isalnum() or char in ' .,!?-_@#$%^&*()[]{}')
        return sanitized.strip()
    
    def validate_api_key(self, api_key):
        """Validate an API key"""
        # Implement API key validation logic
        return False  # Placeholder
    
    def log_security_event(self, event_type, details):
        """Log security-related events"""
        self.logger.warning(f"Security event: {event_type} - {details}")