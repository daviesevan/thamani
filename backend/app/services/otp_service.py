"""
OTP service for generating and validating one-time passwords
"""
import logging
import random
import string
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from flask import abort
from app.extensions.extensions import db
from app.models.user import User, EmailVerificationOTP

# Set up logger
logger = logging.getLogger(__name__)


class OTPService:
    """
    Service for handling OTP operations
    """
    
    # OTP configuration
    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 10
    MAX_ATTEMPTS = 3
    
    @classmethod
    def generate_otp_code(cls) -> str:
        """
        Generate a random 6-digit OTP code
        
        Returns:
            str: 6-digit OTP code
        """
        return ''.join(random.choices(string.digits, k=cls.OTP_LENGTH))
    
    @classmethod
    def create_email_verification_otp(cls, user_id: str, email: str) -> str:
        """
        Create a new email verification OTP for a user
        
        Args:
            user_id: User's ID
            email: User's email address
            
        Returns:
            str: Generated OTP code
            
        Raises:
            Flask abort: If creation fails
        """
        try:
            # Invalidate any existing OTPs for this user
            existing_otps = EmailVerificationOTP.query.filter_by(
                user_id=user_id, 
                email=email,
                is_used=False
            ).all()
            
            for otp in existing_otps:
                otp.is_used = True
            
            # Generate new OTP
            otp_code = cls.generate_otp_code()
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=cls.OTP_EXPIRY_MINUTES)
            
            # Create OTP record
            otp_record = EmailVerificationOTP(
                user_id=user_id,
                email=email,
                otp_code=otp_code,
                expires_at=expires_at
            )
            
            db.session.add(otp_record)
            db.session.commit()
            
            logger.info(f"Created email verification OTP for user {user_id}")
            return otp_code
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating email verification OTP: {str(e)}")
            abort(500, description="Failed to create verification code")
    
    @classmethod
    def verify_email_otp(cls, user_id: str, email: str, otp_code: str) -> Dict[str, Any]:
        """
        Verify an email verification OTP
        
        Args:
            user_id: User's ID
            email: User's email address
            otp_code: OTP code to verify
            
        Returns:
            Dict containing verification result
            
        Raises:
            Flask abort: If verification fails
        """
        try:
            # Find the most recent valid OTP for this user and email
            otp_record = EmailVerificationOTP.query.filter_by(
                user_id=user_id,
                email=email,
                is_used=False
            ).order_by(EmailVerificationOTP.created_at.desc()).first()
            
            if not otp_record:
                abort(400, description="No valid verification code found. Please request a new one.")
            
            # Increment attempts
            otp_record.attempts += 1
            db.session.commit()
            
            # Check if OTP is valid
            if not otp_record.is_valid():
                if otp_record.is_expired():
                    abort(400, description="Verification code has expired. Please request a new one.")
                elif otp_record.attempts >= cls.MAX_ATTEMPTS:
                    abort(400, description="Too many failed attempts. Please request a new verification code.")
                else:
                    abort(400, description="Invalid verification code")
            
            # Check if OTP code matches
            if otp_record.otp_code != otp_code:
                if otp_record.attempts >= cls.MAX_ATTEMPTS:
                    abort(400, description="Too many failed attempts. Please request a new verification code.")
                else:
                    remaining_attempts = cls.MAX_ATTEMPTS - otp_record.attempts
                    abort(400, description=f"Invalid verification code. {remaining_attempts} attempts remaining.")
            
            # Mark OTP as used
            otp_record.is_used = True
            
            # Mark user's email as verified
            user = User.query.get(user_id)
            if user:
                user.email_verified = True
                user.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            logger.info(f"Successfully verified email for user {user_id}")
            
            return {
                "message": "Email verified successfully",
                "user_id": user_id,
                "email": email,
                "verified_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error verifying email OTP: {str(e)}")
            if hasattr(e, 'code') and hasattr(e, 'description'):
                # Re-raise Flask abort exceptions
                raise e
            else:
                abort(500, description="Failed to verify email")
    
    @classmethod
    def resend_email_verification_otp(cls, user_id: str, email: str) -> str:
        """
        Resend email verification OTP (creates a new one)
        
        Args:
            user_id: User's ID
            email: User's email address
            
        Returns:
            str: New OTP code
        """
        try:
            # Check if user exists and email matches
            user = User.query.get(user_id)
            if not user or user.email != email:
                abort(404, description="User not found")
            
            # Check if email is already verified
            if user.email_verified:
                abort(400, description="Email is already verified")
            
            # Create new OTP
            return cls.create_email_verification_otp(user_id, email)
            
        except Exception as e:
            logger.error(f"Error resending email verification OTP: {str(e)}")
            if hasattr(e, 'code') and hasattr(e, 'description'):
                # Re-raise Flask abort exceptions
                raise e
            else:
                abort(500, description="Failed to resend verification code")
    
    @classmethod
    def cleanup_expired_otps(cls) -> int:
        """
        Clean up expired OTP records (can be called periodically)
        
        Returns:
            int: Number of records cleaned up
        """
        try:
            expired_otps = EmailVerificationOTP.query.filter(
                EmailVerificationOTP.expires_at < datetime.now(timezone.utc)
            ).all()
            
            count = len(expired_otps)
            
            for otp in expired_otps:
                db.session.delete(otp)
            
            db.session.commit()
            
            logger.info(f"Cleaned up {count} expired OTP records")
            return count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error cleaning up expired OTPs: {str(e)}")
            return 0
