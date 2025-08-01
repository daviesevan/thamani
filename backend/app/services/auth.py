import logging
import jwt
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from flask import abort, current_app
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import Session

from app.extensions.extensions import db
from app.models.user import User, UserSession, UserPreference
from app.config.app_config import AppConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bcrypt = Bcrypt()

class AuthService:
    """
    Authentication service for handling user authentication with SQLAlchemy and JWT.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password
        """
        return bcrypt.generate_password_hash(password).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.check_password_hash(hashed_password, password)

    @staticmethod
    def generate_jwt_token(user_id: str, expires_in: int = None) -> str:
        """
        Generate a JWT token for a user.
        
        Args:
            user_id: User ID
            expires_in: Token expiration time in seconds
            
        Returns:
            str: JWT token
        """
        if expires_in is None:
            expires_in = AppConfig.JWT_EXPIRATION
            
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, AppConfig.JWT_SECRET, algorithm=AppConfig.JWT_ALGORITHM)

    @staticmethod
    def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Optional[Dict[str, Any]]: Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, AppConfig.JWT_SECRET, algorithms=[AppConfig.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None

    @classmethod
    def register_user(cls, email: str, password: str, username: str = None, full_name: str = None) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            email: User's email address
            password: User's password
            username: User's username (optional)
            full_name: User's full name (optional)
            
        Returns:
            Dict containing user data
            
        Raises:
            Flask abort: If registration fails
        """
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                abort(409, description="User with this email already exists")
            
            if username:
                existing_username = User.query.filter_by(username=username).first()
                if existing_username:
                    abort(409, description="Username already taken")
            
            # Create new user
            user = User(
                user_id=str(uuid.uuid4()),
                email=email,
                password_hash=cls.hash_password(password),
                username=username,
                full_name=full_name,
                email_verified=False  # Require email verification
            )
            
            db.session.add(user)
            db.session.commit()
            
            # Create default user preferences
            preferences = UserPreference(user_id=user.user_id)
            db.session.add(preferences)
            db.session.commit()

            # Send verification email
            from app.services.email_service import EmailService
            email_sent = EmailService.send_verification_email(user.user_id, user.email, user.full_name)

            if not email_sent:
                logger.warning(f"Failed to send verification email to {user.email}")

            return {
                "user_id": user.user_id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "created_at": user.created_at.isoformat(),
                "email_verified": user.email_verified,
                "message": "Registration successful. Please check your email to verify your account."
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error registering user: {str(e)}")
            abort(500, description="Internal server error")

    @classmethod
    def login_with_email(cls, email: str, password: str, device_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User's email address
            password: User's password
            device_info: Dictionary containing device and browser information
            
        Returns:
            Dict containing user data and session
            
        Raises:
            Flask abort: If authentication fails
        """
        try:
            # Find user by email
            user = User.query.filter_by(email=email).first()
            if not user:
                abort(401, description="Invalid credentials")
            
            # Verify password
            if not cls.verify_password(password, user.password_hash):
                abort(401, description="Invalid credentials")
            
            # Update last login timestamp
            user.last_login_at = datetime.now(timezone.utc)
            db.session.commit()
            
            # Generate JWT token
            token = cls.generate_jwt_token(user.user_id)
            
            # Create session record
            session = UserSession(
                session_id=str(uuid.uuid4()),
                user_id=user.user_id,
                token=token[:32],  # Store truncated token as identifier
                device_info=json.dumps(device_info) if device_info else None,
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=AppConfig.JWT_EXPIRATION)
            )
            
            db.session.add(session)
            db.session.commit()

            # Get onboarding status from user preferences
            from app.models.user import UserPreference
            preferences = UserPreference.query.filter_by(user_id=user.user_id).first()
            onboarding_completed = preferences.onboarding_completed if preferences else False

            return {
                "user": {
                    "user_id": user.user_id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "account_status": user.account_status,
                    "email_verified": user.email_verified,
                    "onboarding_completed": onboarding_completed
                },
                "session": {
                    "access_token": token,
                    "expires_in": AppConfig.JWT_EXPIRATION,
                    "token_type": "bearer"
                }
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during login: {str(e)}")
            abort(500, description="Internal server error")

    @classmethod
    def get_current_user(cls, token: str) -> Optional[User]:
        """
        Get the current user from a JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Optional[User]: User object or None if invalid
        """
        try:
            payload = cls.verify_jwt_token(token)
            if not payload:
                return None
            
            user_id = payload.get('user_id')
            if not user_id:
                return None
            
            user = User.query.get(user_id)
            return user
            
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            return None

    @classmethod
    def logout_user(cls, token: str) -> bool:
        """
        Logout a user by invalidating their session.
        
        Args:
            token: JWT token
            
        Returns:
            bool: True if logout successful, False otherwise
        """
        try:
            # Find and delete session
            token_identifier = token[:32]
            session = UserSession.query.filter_by(token=token_identifier).first()
            
            if session:
                db.session.delete(session)
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during logout: {str(e)}")
            return False

    @classmethod
    def change_password(cls, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Change a user's password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            bool: True if password changed successfully
            
        Raises:
            Flask abort: If password change fails
        """
        try:
            user = User.query.get(user_id)
            if not user:
                abort(404, description="User not found")
            
            # Verify current password
            if not cls.verify_password(current_password, user.password_hash):
                abort(401, description="Current password is incorrect")
            
            # Update password
            user.password_hash = cls.hash_password(new_password)
            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error changing password: {str(e)}")
            abort(500, description="Internal server error")

    @classmethod
    def update_user_profile(cls, user_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update user profile information.
        
        Args:
            user_id: User ID
            **kwargs: Profile fields to update
            
        Returns:
            Dict containing updated user data
            
        Raises:
            Flask abort: If update fails
        """
        try:
            user = User.query.get(user_id)
            if not user:
                abort(404, description="User not found")
            
            # Update allowed fields
            allowed_fields = ['username', 'full_name', 'profile_image_url']
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    setattr(user, field, value)
            
            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return {
                "user_id": user.user_id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "profile_image_url": user.profile_image_url,
                "account_status": user.account_status,
                "email_verified": user.email_verified,
                "updated_at": user.updated_at.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating user profile: {str(e)}")
            abort(500, description="Internal server error")

    @classmethod
    def complete_onboarding(cls, user_id: str) -> Dict[str, Any]:
        """
        Mark user's onboarding as completed in user preferences.

        Args:
            user_id: User ID

        Returns:
            Dict containing user data with onboarding status

        Raises:
            Flask abort: If completion fails
        """
        try:
            from app.models.user import UserPreference

            user = User.query.get(user_id)
            if not user:
                abort(404, description="User not found")

            # Get or create user preferences
            preferences = UserPreference.query.filter_by(user_id=user_id).first()
            if not preferences:
                preferences = UserPreference(
                    user_id=user_id,
                    onboarding_completed=True
                )
                db.session.add(preferences)
            else:
                preferences.onboarding_completed = True
                preferences.updated_at = datetime.now(timezone.utc)

            db.session.commit()

            # Return user data with onboarding status
            return {
                "user_id": user.user_id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "profile_image_url": user.profile_image_url,
                "account_status": user.account_status,
                "email_verified": user.email_verified,
                "onboarding_completed": True,
                "updated_at": user.updated_at.isoformat()
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error completing onboarding: {str(e)}")
            abort(500, description="Internal server error")

    @classmethod
    def verify_email(cls, token: str) -> Dict[str, Any]:
        """
        Verify a user's email address using a verification token

        Args:
            token: Email verification token

        Returns:
            Dict containing verification result

        Raises:
            Flask abort: If verification fails
        """
        try:
            from app.utils.token_utils import TokenManager
            from app.services.email_service import EmailService

            # Verify the token
            payload = TokenManager.verify_verification_token(token)
            if not payload:
                abort(400, description="Invalid or expired verification token")

            user_id = payload.get('user_id')
            email = payload.get('email')

            if not user_id or not email:
                abort(400, description="Invalid token payload")

            # Find the user
            user = User.query.get(user_id)
            if not user:
                abort(404, description="User not found")

            # Check if email matches
            if user.email != email:
                abort(400, description="Token email does not match user email")

            # Check if already verified
            if user.email_verified:
                return {
                    "message": "Email already verified",
                    "user": {
                        "user_id": user.user_id,
                        "email": user.email,
                        "email_verified": True
                    }
                }

            # Mark email as verified
            user.email_verified = True
            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()

            # Send welcome email
            EmailService.send_welcome_email(user.email, user.full_name)

            logger.info(f"Email verified successfully for user {user_id}")

            return {
                "message": "Email verified successfully",
                "user": {
                    "user_id": user.user_id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "email_verified": True
                }
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error verifying email: {str(e)}")
            abort(500, description="Internal server error")

    @classmethod
    def verify_email_with_otp(cls, user_id: str, email: str, otp_code: str) -> Dict[str, Any]:
        """
        Verify a user's email address using an OTP code

        Args:
            user_id: User's ID
            email: User's email address
            otp_code: OTP verification code

        Returns:
            Dict containing verification result

        Raises:
            Flask abort: If verification fails
        """
        try:
            from app.services.otp_service import OTPService
            result = OTPService.verify_email_otp(user_id, email, otp_code)

            # Return user data along with verification result
            user = User.query.get(user_id)
            if user:
                result["user"] = {
                    "user_id": user.user_id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "email_verified": True
                }

            return result

        except Exception as e:
            logger.error(f"Error verifying email with OTP: {str(e)}")
            if hasattr(e, 'code') and hasattr(e, 'description'):
                # Re-raise Flask abort exceptions
                raise e
            else:
                abort(500, description="Email verification failed")

    @classmethod
    def resend_verification_email(cls, email: str) -> Dict[str, Any]:
        """
        Resend verification email to a user

        Args:
            email: User's email address

        Returns:
            Dict containing result message

        Raises:
            Flask abort: If resend fails
        """
        try:
            from app.services.email_service import EmailService

            # Find user by email
            user = User.query.filter_by(email=email).first()
            if not user:
                abort(404, description="User not found")

            # Check if already verified
            if user.email_verified:
                abort(400, description="Email is already verified")

            # Generate and send new OTP
            from app.services.otp_service import OTPService
            otp_code = OTPService.resend_email_verification_otp(user.user_id, user.email)

            # Send verification email with OTP
            success = EmailService.send_verification_email(user.user_id, user.email, user.full_name)

            if not success:
                logger.warning(f"Failed to send verification email to {email}, but continuing...")
                # Don't abort - user can still request resend later

            logger.info(f"Verification OTP resent to {email}")

            return {
                "message": "Verification code sent successfully",
                "email": email,
                "expires_in_minutes": OTPService.OTP_EXPIRY_MINUTES
            }

        except Exception as e:
            logger.error(f"Error resending verification email: {str(e)}")
            abort(500, description="Internal server error")
