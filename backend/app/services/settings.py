import logging
from typing import Dict, Any, Optional
from flask import abort
from datetime import datetime, timezone
from app.config.app_config import AppConfig
from app.services.auth import AuthService

# Set up logger
logger = logging.getLogger(__name__)

class SettingsService:
    """
    Service for managing user settings and preferences
    """

    @classmethod
    def get_admin_client(cls):
        """
        Get the Supabase admin client for database operations
        """
        return AuthService.get_admin_client()

    @classmethod
    async def get_user_settings(cls, user_id: str) -> Dict[str, Any]:
        """
        Get a user's settings and preferences

        Args:
            user_id: User's ID

        Returns:
            Dict containing user settings and preferences

        Raises:
            Flask abort: If retrieval fails
        """
        try:
            admin_client = cls.get_admin_client()

            # Get user preferences
            preferences_response = admin_client.table("user_preferences").select("*").eq("user_id", user_id).execute()

            if not preferences_response.data or len(preferences_response.data) == 0:
                # Create default preferences if they don't exist
                default_preferences = {
                    "user_id": user_id,
                    "currency": "KES",
                    "language": "en",
                    "theme": "light",
                    "notification_email": True,
                    "notification_push": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }

                admin_client.table("user_preferences").insert(default_preferences).execute()
                return default_preferences

            return preferences_response.data[0]

        except Exception as e:
            logger.error(f"Error retrieving user settings: {str(e)}")
            abort(500, description=f"Error retrieving user settings: {str(e)}")

    @classmethod
    async def update_user_settings(cls, user_id: str, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a user's settings and preferences

        Args:
            user_id: User's ID
            settings_data: Dict containing settings data to update

        Returns:
            Dict containing updated user settings

        Raises:
            Flask abort: If update fails
        """
        logger.info(f"Updating settings for user {user_id}: {settings_data}")

        try:
            admin_client = cls.get_admin_client()

            # Fields that can be updated in the user_preferences table
            allowed_fields = [
                "currency",
                "language",
                "theme",
                "notification_email",
                "notification_push"
            ]

            # Filter out fields that are not allowed to be updated
            updates = {k: v for k, v in settings_data.items() if k in allowed_fields}

            logger.info(f"Filtered updates: {updates}")

            # Add updated_at timestamp
            if updates:
                updates["updated_at"] = datetime.now(timezone.utc).isoformat()

                # Check if preferences exist for the user
                preferences_response = admin_client.table("user_preferences").select("*").eq("user_id", user_id).execute()

                if not preferences_response.data or len(preferences_response.data) == 0:
                    # Create new preferences if they don't exist
                    logger.info(f"Creating new preferences for user {user_id}")
                    updates["user_id"] = user_id
                    updates["created_at"] = datetime.now(timezone.utc).isoformat()
                    insert_response = admin_client.table("user_preferences").insert(updates).execute()
                    logger.info(f"Insert response: {insert_response.data}")
                else:
                    # Update existing preferences
                    logger.info(f"Updating existing preferences for user {user_id}")
                    update_response = admin_client.table("user_preferences").update(updates).eq("user_id", user_id).execute()
                    logger.info(f"Update response: {update_response.data}")
            else:
                logger.warning(f"No valid fields to update for user {user_id}")

            # Get updated settings
            updated_settings = await cls.get_user_settings(user_id)
            logger.info(f"Updated settings: {updated_settings}")
            return updated_settings

        except Exception as e:
            logger.error(f"Error updating user settings: {str(e)}", exc_info=True)
            abort(500, description=f"Error updating user settings: {str(e)}")

    @classmethod
    async def update_theme_setting(cls, user_id: str, theme: str) -> Dict[str, Any]:
        """
        Update a user's theme preference

        Args:
            user_id: User's ID
            theme: Theme preference ('light', 'dark', or 'system')

        Returns:
            Dict containing updated user settings

        Raises:
            Flask abort: If update fails
        """
        if theme not in ['light', 'dark', 'system']:
            abort(400, description="Invalid theme value. Must be 'light', 'dark', or 'system'")

        return await cls.update_user_settings(user_id, {"theme": theme})

    @classmethod
    async def update_notification_settings(cls, user_id: str, email_enabled: bool, push_enabled: bool) -> Dict[str, Any]:
        """
        Update a user's notification settings

        Args:
            user_id: User's ID
            email_enabled: Whether email notifications are enabled
            push_enabled: Whether push notifications are enabled

        Returns:
            Dict containing updated user settings

        Raises:
            Flask abort: If update fails
        """
        updates = {
            "notification_email": email_enabled,
            "notification_push": push_enabled
        }

        return await cls.update_user_settings(user_id, updates)

    @classmethod
    async def update_currency_setting(cls, user_id: str, currency: str) -> Dict[str, Any]:
        """
        Update a user's currency preference

        Args:
            user_id: User's ID
            currency: Currency code (e.g., 'KES', 'USD')

        Returns:
            Dict containing updated user settings

        Raises:
            Flask abort: If update fails
        """
        # You could add validation for supported currencies here
        valid_currencies = ['KES', 'USD', 'EUR', 'GBP']
        if currency not in valid_currencies:
            abort(400, description=f"Invalid currency code. Supported currencies are: {', '.join(valid_currencies)}")

        return await cls.update_user_settings(user_id, {"currency": currency})

    @classmethod
    async def update_language_setting(cls, user_id: str, language: str) -> Dict[str, Any]:
        """
        Update a user's language preference

        Args:
            user_id: User's ID
            language: Language code (e.g., 'en', 'sw')

        Returns:
            Dict containing updated user settings

        Raises:
            Flask abort: If update fails
        """
        # You could add validation for supported languages here
        valid_languages = ['en', 'sw']
        if language not in valid_languages:
            abort(400, description=f"Invalid language code. Supported languages are: {', '.join(valid_languages)}")

        return await cls.update_user_settings(user_id, {"language": language})