import logging
import jwt
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from supabase.client import Client
from flask import abort

from app.config.supabase import SupabaseConfig
from app.config.app_config import AppConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthService:
    """
    Authentication service for handling user authentication with Supabase.
    """

    @staticmethod
    def get_supabase_client() -> Client:
        """
        Get a Supabase client instance.

        Returns:
            Client: A Supabase client instance.
        """
        return SupabaseConfig.get_client()

    @staticmethod
    def get_admin_client() -> Client:
        """
        Get a Supabase admin client instance.

        Returns:
            Client: A Supabase client instance with admin privileges.
        """
        return SupabaseConfig.get_admin_client()

    @classmethod
    async def signup_with_email(cls, email: str, password: str, full_name: str = None) -> Dict[str, Any]:
        """
        Register a new user with email and password.

        Args:
            email: User's email address
            password: User's password
            full_name: User's full name (optional)

        Returns:
            Dict containing user data and session

        Raises:
            Flask abort: If registration fails
        """
        try:
            supabase = cls.get_supabase_client()

            # Register user with Supabase Auth
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name
                    }
                }
            })

            if not auth_response.user:
                abort(400, description="Failed to create user account")

            user_id = auth_response.user.id

            # Get full name from user metadata if available
            user_metadata = auth_response.user.user_metadata or {}
            display_name = user_metadata.get("full_name") or full_name

            # Add additional user data to the users table
            user_data = {
                "user_id": user_id,
                "email": email,
                "password_hash": password,  # Store the password hash
                "full_name": display_name,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "email_verified": False
            }

            # Use admin client to insert user data
            admin_client = cls.get_admin_client()
            user_response = admin_client.table("users").insert(user_data).execute()

            if len(user_response.data) == 0:
                # If user data insertion fails, we should delete the auth user
                admin_client.auth.admin.delete_user(user_id)
                abort(500, description="Failed to create user profile")

            # Create default user preferences
            preferences_data = {
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }

            admin_client.table("user_preferences").insert(preferences_data).execute()

            # Create a serializable version of the user and session
            user_data = {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "full_name": full_name,
                "email_verified": False
            }

            session_data = None
            if auth_response.session:
                session_data = {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "expires_in": auth_response.session.expires_in,
                    "token_type": auth_response.session.token_type
                }

            return {
                "user": user_data,
                "session": session_data,
                "message": "User registered successfully. Please verify your email."
            }

        except Exception as e:
            logger.error(f"Error during signup: {str(e)}")
            if "User already registered" in str(e):
                abort(409, description="User with this email already exists")
            abort(500, description=f"Error during signup: {str(e)}")

    @classmethod
    async def login_with_email(cls, email: str, password: str, device_info: Dict[str, Any] = None) -> Dict[str, Any]:
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
            supabase = cls.get_supabase_client()

            # Authenticate user with Supabase Auth
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not auth_response.user:
                abort(401, description="Invalid credentials")

            user_id = auth_response.user.id

            # Update last login timestamp
            admin_client = cls.get_admin_client()
            admin_client.table("users").update({
                "last_login_at": datetime.now(timezone.utc).isoformat()
            }).eq("user_id", user_id).execute()

            # Record session - use a truncated or hashed token to fit in VARCHAR(255)
            # We'll use the first 32 characters of the token as an identifier
            # This is safe because we're just using it as a reference, not for authentication
            token_identifier = auth_response.session.access_token[:32]

            # Prepare session data
            session_data = {
                "user_id": user_id,
                "token": token_identifier,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=auth_response.session.expires_in)).isoformat(),
                "last_active_at": datetime.now(timezone.utc).isoformat()
            }

            # Add device info if available
            if device_info:
                # Convert device info to JSONB format
                session_data["device_info"] = json.dumps(device_info)
                if "ip_address" in device_info:
                    session_data["ip_address"] = device_info["ip_address"]

            try:
                admin_client.table("user_sessions").insert(session_data).execute()
            except Exception as e:
                # If session recording fails, log it but don't fail the login
                logger.error(f"Failed to record session: {str(e)}")
                # Continue with login process

            # Get user preferences to check onboarding status
            preferences_response = admin_client.table("user_preferences").select("*").eq("user_id", user_id).execute()
            preferences_data = preferences_response.data[0] if len(preferences_response.data) > 0 else {}

            # Create a serializable version of the user and session
            user_data = {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "email_verified": auth_response.user.email_confirmed_at is not None,
                "onboarding_completed": preferences_data.get("onboarding_completed", False)
            }

            session_data = None
            if auth_response.session:
                session_data = {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "expires_in": auth_response.session.expires_in,
                    "token_type": auth_response.session.token_type
                }

            return {
                "user": user_data,
                "session": session_data,
                "message": "Login successful"
            }

        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            if "Invalid login credentials" in str(e):
                abort(401, description="Invalid email or password")
            abort(500, description=f"Error during login: {str(e)}")

    @classmethod
    async def login_with_google(cls, access_token: str, device_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Authenticate a user with Google OAuth.

        Args:
            access_token: Google OAuth access token
            device_info: Dictionary containing device and browser information

        Returns:
            Dict containing user data and session

        Raises:
            Flask abort: If authentication fails
        """
        try:
            supabase = cls.get_supabase_client()

            # Sign in with Google OAuth token
            auth_response = supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "access_token": access_token
            })

            if not auth_response.user:
                abort(401, description="Google authentication failed")

            user_id = auth_response.user.id
            email = auth_response.user.email

            # Check if user exists in our database
            admin_client = cls.get_admin_client()
            user_response = admin_client.table("users").select("*").eq("user_id", user_id).execute()

            if len(user_response.data) == 0:
                # Get user metadata
                user_metadata = auth_response.user.user_metadata or {}
                display_name = user_metadata.get("full_name") or user_metadata.get("name") or email.split("@")[0]

                # First-time Google login, create user profile
                user_data = {
                    "user_id": user_id,
                    "email": email,
                    "password_hash": "google_oauth",  # Placeholder for OAuth users
                    "full_name": display_name,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "email_verified": True
                }

                admin_client.table("users").insert(user_data).execute()

                # Create default user preferences
                preferences_data = {
                    "user_id": user_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }

                admin_client.table("user_preferences").insert(preferences_data).execute()
            else:
                # Update last login timestamp
                admin_client.table("users").update({
                    "last_login_at": datetime.now(timezone.utc).isoformat()
                }).eq("user_id", user_id).execute()

            # Record session - use a truncated or hashed token to fit in VARCHAR(255)
            # We'll use the first 32 characters of the token as an identifier
            token_identifier = auth_response.session.access_token[:32]

            # Prepare session data
            session_data = {
                "user_id": user_id,
                "token": token_identifier,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=auth_response.session.expires_in)).isoformat(),
                "last_active_at": datetime.now(timezone.utc).isoformat()
            }

            # Add device info if available
            if device_info:
                # Convert device info to JSONB format
                session_data["device_info"] = json.dumps(device_info)
                if "ip_address" in device_info:
                    session_data["ip_address"] = device_info["ip_address"]

            try:
                admin_client.table("user_sessions").insert(session_data).execute()
            except Exception as e:
                # If session recording fails, log it but don't fail the login
                logger.error(f"Failed to record session: {str(e)}")
                # Continue with login process

            # Get user preferences to check onboarding status
            preferences_response = admin_client.table("user_preferences").select("*").eq("user_id", user_id).execute()
            preferences_data = preferences_response.data[0] if len(preferences_response.data) > 0 else {}

            # Create a serializable version of the user and session
            user_metadata = auth_response.user.user_metadata or {}
            user_data = {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "full_name": user_metadata.get("full_name") or user_metadata.get("name"),
                "email_verified": True,
                "onboarding_completed": preferences_data.get("onboarding_completed", False)
            }

            session_data = None
            if auth_response.session:
                session_data = {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "expires_in": auth_response.session.expires_in,
                    "token_type": auth_response.session.token_type
                }

            return {
                "user": user_data,
                "session": session_data,
                "message": "Google login successful"
            }

        except Exception as e:
            logger.error(f"Error during Google login: {str(e)}")
            abort(500, description=f"Error during Google login: {str(e)}")

    @classmethod
    async def login_with_facebook(cls, access_token: str, device_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Authenticate a user with Facebook OAuth.

        Args:
            access_token: Facebook OAuth access token
            device_info: Dictionary containing device and browser information

        Returns:
            Dict containing user data and session

        Raises:
            Flask abort: If authentication fails
        """
        try:
            supabase = cls.get_supabase_client()

            # Sign in with Facebook OAuth token
            auth_response = supabase.auth.sign_in_with_oauth({
                "provider": "facebook",
                "access_token": access_token
            })

            if not auth_response.user:
                abort(401, description="Facebook authentication failed")

            user_id = auth_response.user.id
            email = auth_response.user.email

            # Check if user exists in our database
            admin_client = cls.get_admin_client()
            user_response = admin_client.table("users").select("*").eq("user_id", user_id).execute()

            if len(user_response.data) == 0:
                # Get user metadata
                user_metadata = auth_response.user.user_metadata or {}
                display_name = user_metadata.get("full_name") or user_metadata.get("name") or email.split("@")[0]

                # First-time Facebook login, create user profile
                user_data = {
                    "user_id": user_id,
                    "email": email,
                    "password_hash": "facebook_oauth",  # Placeholder for OAuth users
                    "full_name": display_name,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "email_verified": True
                }

                admin_client.table("users").insert(user_data).execute()

                # Create default user preferences
                preferences_data = {
                    "user_id": user_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }

                admin_client.table("user_preferences").insert(preferences_data).execute()
            else:
                # Update last login timestamp
                admin_client.table("users").update({
                    "last_login_at": datetime.now(timezone.utc).isoformat()
                }).eq("user_id", user_id).execute()

            # Record session - use a truncated or hashed token to fit in VARCHAR(255)
            # We'll use the first 32 characters of the token as an identifier
            token_identifier = auth_response.session.access_token[:32]

            # Prepare session data
            session_data = {
                "user_id": user_id,
                "token": token_identifier,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=auth_response.session.expires_in)).isoformat(),
                "last_active_at": datetime.now(timezone.utc).isoformat()
            }

            # Add device info if available
            if device_info:
                # Convert device info to JSONB format
                session_data["device_info"] = json.dumps(device_info)
                if "ip_address" in device_info:
                    session_data["ip_address"] = device_info["ip_address"]

            try:
                admin_client.table("user_sessions").insert(session_data).execute()
            except Exception as e:
                # If session recording fails, log it but don't fail the login
                logger.error(f"Failed to record session: {str(e)}")
                # Continue with login process

            # Get user preferences to check onboarding status
            preferences_response = admin_client.table("user_preferences").select("*").eq("user_id", user_id).execute()
            preferences_data = preferences_response.data[0] if len(preferences_response.data) > 0 else {}

            # Create a serializable version of the user and session
            user_metadata = auth_response.user.user_metadata or {}
            user_data = {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "full_name": user_metadata.get("full_name") or user_metadata.get("name"),
                "email_verified": True,
                "onboarding_completed": preferences_data.get("onboarding_completed", False)
            }

            session_data = None
            if auth_response.session:
                session_data = {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "expires_in": auth_response.session.expires_in,
                    "token_type": auth_response.session.token_type
                }

            return {
                "user": user_data,
                "session": session_data,
                "message": "Facebook login successful"
            }

        except Exception as e:
            logger.error(f"Error during Facebook login: {str(e)}")
            abort(500, description=f"Error during Facebook login: {str(e)}")

    @classmethod
    async def logout(cls, access_token: str) -> Dict[str, str]:
        """
        Log out a user and invalidate their session.

        Args:
            access_token: User's access token

        Returns:
            Dict with success message

        Raises:
            Flask abort: If logout fails
        """
        try:
            supabase = cls.get_supabase_client()

            # Sign out from Supabase Auth
            supabase.auth.sign_out()

            # Invalidate session in our database
            # Use the same truncation method as in login
            token_identifier = access_token[:32]

            admin_client = cls.get_admin_client()
            try:
                admin_client.table("user_sessions").update({
                    "expires_at": datetime.now(timezone.utc).isoformat()
                }).eq("token", token_identifier).execute()
            except Exception as e:
                # If session invalidation fails, log it but don't fail the logout
                logger.error(f"Failed to invalidate session: {str(e)}")
                # Continue with logout process

            return {"message": "Logout successful"}

        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            abort(500, description=f"Error during logout: {str(e)}")

    @classmethod
    async def reset_password_request(cls, email: str) -> Dict[str, str]:
        """
        Request a password reset for a user.

        Args:
            email: User's email address

        Returns:
            Dict with success message

        Raises:
            Flask abort: If request fails
        """
        try:
            supabase = cls.get_supabase_client()

            # Send password reset email
            supabase.auth.reset_password_email(email)

            return {"message": "Password reset instructions sent to your email"}

        except Exception as e:
            logger.error(f"Error during password reset request: {str(e)}")
            # Don't reveal if email exists or not for security
            return {"message": "If your email is registered, you will receive password reset instructions"}

    @classmethod
    async def verify_email(cls, token: str) -> Dict[str, str]:
        """
        Verify a user's email address.

        Args:
            token: Email verification token

        Returns:
            Dict with success message

        Raises:
            Flask abort: If verification fails
        """
        try:
            # This is handled by Supabase Auth directly via email link
            # We just need to update our database to reflect the verified status

            # Decode the token to get user_id
            payload = jwt.decode(token, AppConfig.JWT_SECRET, algorithms=[AppConfig.JWT_ALGORITHM])
            user_id = payload.get("sub")

            if not user_id:
                abort(400, description="Invalid verification token")

            # Update email_verified status
            admin_client = cls.get_admin_client()
            admin_client.table("users").update({
                "email_verified": True,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("user_id", user_id).execute()

            return {"message": "Email verified successfully"}

        except jwt.PyJWTError:
            abort(400, description="Invalid or expired verification token")
        except Exception as e:
            logger.error(f"Error during email verification: {str(e)}")
            abort(500, description=f"Error during email verification: {str(e)}")

    @classmethod
    async def get_user_profile(cls, user_id: str) -> Dict[str, Any]:
        """
        Get a user's profile information.

        Args:
            user_id: User's ID

        Returns:
            Dict containing user profile data

        Raises:
            Flask abort: If retrieval fails
        """
        try:
            admin_client = cls.get_admin_client()

            # Get user data
            user_response = admin_client.table("users").select("*").eq("user_id", user_id).execute()

            if len(user_response.data) == 0:
                abort(404, description="User not found")

            # Get user preferences
            preferences_response = admin_client.table("user_preferences").select("*").eq("user_id", user_id).execute()

            user_data = user_response.data[0]
            preferences_data = preferences_response.data[0] if len(preferences_response.data) > 0 else {}

            # Combine user data and preferences
            profile = {
                "user_id": user_data.get("user_id"),
                "email": user_data.get("email"),
                "username": user_data.get("username"),
                "full_name": user_data.get("full_name"),
                "profile_image_url": user_data.get("profile_image_url"),
                "email_verified": user_data.get("email_verified"),
                "account_status": user_data.get("account_status"),
                "created_at": user_data.get("created_at"),
                "onboarding_completed": preferences_data.get("onboarding_completed", False),
                "preferences": preferences_data
            }

            return profile

        except Exception as e:
            logger.error(f"Error retrieving user profile: {str(e)}")
            abort(500, description=f"Error retrieving user profile: {str(e)}")

    @classmethod
    async def change_password(cls, user_id: str, current_password: str, new_password: str) -> Dict[str, str]:
        """
        Change a user's password.

        Args:
            user_id: User's ID
            current_password: User's current password
            new_password: User's new password

        Returns:
            Dict with success message

        Raises:
            Flask abort: If password change fails
        """
        try:
            supabase = cls.get_supabase_client()
            admin_client = cls.get_admin_client()

            # First, verify the current password by attempting to sign in
            # Get the user's email
            user_response = admin_client.table("users").select("email").eq("user_id", user_id).execute()

            if not user_response.data or len(user_response.data) == 0:
                abort(404, description="User not found")

            email = user_response.data[0].get("email")

            # Try to authenticate with current password
            try:
                auth_response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": current_password
                })

                if not auth_response.user:
                    abort(401, description="Current password is incorrect")
            except Exception as e:
                logger.error(f"Authentication error during password change: {str(e)}")
                abort(401, description="Current password is incorrect")

            # If authentication succeeded, update the password
            # Use the admin API to update the user's password
            auth_user = supabase.auth.admin.update_user_by_id(
                user_id,
                {"password": new_password}
            )

            if not auth_user:
                abort(500, description="Failed to update password")

            return {"message": "Password changed successfully"}

        except Exception as e:
            logger.error(f"Error during password change: {str(e)}")
            if "401" in str(e) or "incorrect" in str(e).lower():
                abort(401, description="Current password is incorrect")
            abort(500, description=f"Error changing password: {str(e)}")

    @classmethod
    async def update_user_profile(cls, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a user's profile information.

        Args:
            user_id: User's ID
            profile_data: Dict containing profile data to update

        Returns:
            Dict containing updated user profile data

        Raises:
            Flask abort: If update fails
        """
        try:
            admin_client = cls.get_admin_client()

            # Separate user data and preferences
            user_updates = {}
            preference_updates = {}

            # Fields that can be updated in the users table
            user_fields = ["username", "full_name", "profile_image_url"]

            # Fields that can be updated in the user_preferences table
            preference_fields = ["currency", "language", "theme", "notification_email", "notification_push"]

            # Check if onboarding_completed is in the profile_data
            if "onboarding_completed" in profile_data:
                try:
                    # Try to update onboarding_completed
                    admin_client.table("user_preferences").update({
                        "onboarding_completed": profile_data["onboarding_completed"]
                    }).eq("user_id", user_id).execute()
                except Exception as e:
                    # If it fails, log the error but continue with other updates
                    logger.error(f"Error updating onboarding_completed: {str(e)}")
                    # Remove it from profile_data to prevent further errors
                    profile_data.pop("onboarding_completed", None)

            for key, value in profile_data.items():
                if key in user_fields:
                    user_updates[key] = value
                elif key in preference_fields:
                    preference_updates[key] = value

            # Add updated_at timestamp
            if user_updates:
                user_updates["updated_at"] = datetime.now(timezone.utc).isoformat()

                # Update user data
                admin_client.table("users").update(user_updates).eq("user_id", user_id).execute()

            if preference_updates:
                preference_updates["updated_at"] = datetime.now(timezone.utc).isoformat()

                # Update user preferences
                admin_client.table("user_preferences").update(preference_updates).eq("user_id", user_id).execute()

            # Get updated profile
            return await cls.get_user_profile(user_id)

        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            abort(500, description=f"Error updating user profile: {str(e)}")
