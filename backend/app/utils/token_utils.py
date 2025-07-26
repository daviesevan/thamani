"""
Token utilities for email verification and password reset
"""
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import jwt
from app.config.app_config import AppConfig


class TokenManager:
    """
    Manages secure tokens for email verification and password reset
    """
    
    @staticmethod
    def generate_verification_token(user_id: str, email: str, expires_in_hours: int = 24) -> str:
        """
        Generate a secure email verification token
        
        Args:
            user_id: User's ID
            email: User's email address
            expires_in_hours: Token expiration time in hours
            
        Returns:
            str: JWT token for email verification
        """
        payload = {
            'user_id': user_id,
            'email': email,
            'type': 'email_verification',
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, AppConfig.JWT_SECRET, algorithm=AppConfig.JWT_ALGORITHM)
    
    @staticmethod
    def verify_verification_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode an email verification token
        
        Args:
            token: JWT token to verify
            
        Returns:
            Optional[Dict]: Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, AppConfig.JWT_SECRET, algorithms=[AppConfig.JWT_ALGORITHM])
            
            # Check if it's an email verification token
            if payload.get('type') != 'email_verification':
                return None
                
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def generate_password_reset_token(user_id: str, email: str, expires_in_hours: int = 1) -> str:
        """
        Generate a secure password reset token
        
        Args:
            user_id: User's ID
            email: User's email address
            expires_in_hours: Token expiration time in hours (default 1 hour)
            
        Returns:
            str: JWT token for password reset
        """
        payload = {
            'user_id': user_id,
            'email': email,
            'type': 'password_reset',
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, AppConfig.JWT_SECRET, algorithm=AppConfig.JWT_ALGORITHM)
    
    @staticmethod
    def verify_password_reset_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a password reset token
        
        Args:
            token: JWT token to verify
            
        Returns:
            Optional[Dict]: Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, AppConfig.JWT_SECRET, algorithms=[AppConfig.JWT_ALGORITHM])
            
            # Check if it's a password reset token
            if payload.get('type') != 'password_reset':
                return None
                
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def generate_secure_random_token(length: int = 32) -> str:
        """
        Generate a cryptographically secure random token
        
        Args:
            length: Length of the token in bytes
            
        Returns:
            str: Hex-encoded random token
        """
        return secrets.token_hex(length)
    
    @staticmethod
    def hash_token(token: str) -> str:
        """
        Hash a token using SHA-256
        
        Args:
            token: Token to hash
            
        Returns:
            str: Hex-encoded hash of the token
        """
        return hashlib.sha256(token.encode()).hexdigest()
