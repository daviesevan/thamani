"""
Email service for sending verification and notification emails
"""
import logging
from typing import Optional, Dict, Any
from flask import render_template, current_app
from flask_mail import Message
from app.extensions.extensions import mail
from app.utils.token_utils import TokenManager

# Set up logger
logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for handling email operations
    """
    
    @staticmethod
    def send_verification_email(user_id: str, email: str, user_name: Optional[str] = None) -> bool:
        """
        Send email verification OTP to user

        Args:
            user_id: User's ID
            email: User's email address
            user_name: User's name (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Generate OTP code
            from app.services.otp_service import OTPService
            otp_code = OTPService.create_email_verification_otp(user_id, email)

            # Prepare email content
            subject = "Your Email Verification Code - Thamani"

            # Render HTML template
            html_body = render_template(
                'email/verification_otp.html',
                user_name=user_name,
                email=email,
                otp_code=otp_code,
                expiry_minutes=OTPService.OTP_EXPIRY_MINUTES
            )
            
            # Render text template
            text_body = render_template(
                'email/verification_otp.txt',
                user_name=user_name,
                email=email,
                otp_code=otp_code,
                expiry_minutes=OTPService.OTP_EXPIRY_MINUTES
            )
            
            # Create and send email
            msg = Message(
                subject=subject,
                recipients=[email],
                html=html_body,
                body=text_body
            )
            
            mail.send(msg)
            logger.info(f"Verification email sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {email}: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(user_id: str, email: str, user_name: Optional[str] = None) -> bool:
        """
        Send password reset email to user
        
        Args:
            user_id: User's ID
            email: User's email address
            user_name: User's name (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Generate password reset token
            token = TokenManager.generate_password_reset_token(user_id, email)
            
            # Create reset URL
            frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
            reset_url = f"{frontend_url}/reset-password?token={token}"
            
            # Prepare email content
            subject = "Reset Your Password - Thamani"
            
            # For now, use simple text email (you can create HTML template later)
            text_body = f"""
Hello {user_name or 'there'},

You requested to reset your password for your Thamani account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour for security reasons.

If you didn't request this password reset, please ignore this email.

Best regards,
The Thamani Team
            """
            
            # Create and send email
            msg = Message(
                subject=subject,
                recipients=[email],
                body=text_body
            )
            
            mail.send(msg)
            logger.info(f"Password reset email sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {str(e)}")
            return False
    
    @staticmethod
    def send_welcome_email(email: str, user_name: Optional[str] = None) -> bool:
        """
        Send welcome email to newly verified user
        
        Args:
            email: User's email address
            user_name: User's name (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = "Welcome to Thamani!"
            
            text_body = f"""
Hello {user_name or 'there'},

Welcome to Thamani! Your email has been successfully verified.

You can now:
- Track product prices across multiple retailers
- Set up price alerts for your favorite items
- Create and manage wishlists
- Get personalized recommendations

Start exploring: http://localhost:3000/dashboard

If you have any questions, feel free to contact our support team.

Happy shopping!
The Thamani Team
            """
            
            # Create and send email
            msg = Message(
                subject=subject,
                recipients=[email],
                body=text_body
            )
            
            mail.send(msg)
            logger.info(f"Welcome email sent successfully to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {email}: {str(e)}")
            return False
    
    @staticmethod
    def test_email_configuration() -> Dict[str, Any]:
        """
        Test email configuration
        
        Returns:
            Dict containing test results
        """
        try:
            # Try to connect to mail server
            with mail.connect() as conn:
                logger.info("Email configuration test successful")
                return {
                    "success": True,
                    "message": "Email configuration is working correctly"
                }
        except Exception as e:
            logger.error(f"Email configuration test failed: {str(e)}")
            return {
                "success": False,
                "message": f"Email configuration error: {str(e)}"
            }
