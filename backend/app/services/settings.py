import logging
from typing import Dict, Any, Optional
from flask import abort
from datetime import datetime, timezone
from app.extensions.extensions import db
from app.models.user import UserPreference

# Set up logger
logger = logging.getLogger(__name__)

class SettingsService:
    """
    Service for managing user settings and preferences using SQLAlchemy
    """

    @classmethod
    def get_user_settings(cls, user_id: str) -> Dict[str, Any]:
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
            # Get user preferences from database
            preferences = UserPreference.query.filter_by(user_id=user_id).first()

            if not preferences:
                # Create default preferences if they don't exist
                preferences = UserPreference(
                    user_id=user_id,
                    currency="KES",
                    language="en",
                    theme="light",
                    notification_email=True,
                    notification_push=True,
                    onboarding_completed=False
                )
                db.session.add(preferences)
                db.session.commit()

            # Convert to dictionary
            return {
                "user_id": preferences.user_id,
                "currency": preferences.currency,
                "language": preferences.language,
                "theme": preferences.theme,
                "notification_email": preferences.notification_email,
                "notification_push": preferences.notification_push,
                "onboarding_completed": preferences.onboarding_completed,
                "created_at": preferences.created_at.isoformat() if preferences.created_at else None,
                "updated_at": preferences.updated_at.isoformat() if preferences.updated_at else None
            }

        except Exception as e:
            logger.error(f"Error retrieving user settings: {str(e)}")
            db.session.rollback()
            abort(500, description=f"Error retrieving user settings: {str(e)}")

    @classmethod
    def update_user_settings(cls, user_id: str, settings_data: Dict[str, Any]) -> Dict[str, Any]:
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
            # Fields that can be updated in the user_preferences table
            allowed_fields = [
                "currency",
                "language",
                "theme",
                "notification_email",
                "notification_push",
                "onboarding_completed"
            ]

            # Filter out fields that are not allowed to be updated
            updates = {k: v for k, v in settings_data.items() if k in allowed_fields}

            logger.info(f"Filtered updates: {updates}")

            if updates:
                # Get or create user preferences
                preferences = UserPreference.query.filter_by(user_id=user_id).first()

                if not preferences:
                    # Create new preferences if they don't exist
                    logger.info(f"Creating new preferences for user {user_id}")
                    preferences = UserPreference(user_id=user_id)
                    db.session.add(preferences)

                # Update the preferences
                logger.info(f"Updating preferences for user {user_id}")
                for field, value in updates.items():
                    setattr(preferences, field, value)

                # Update timestamp
                preferences.updated_at = datetime.now(timezone.utc)

                db.session.commit()
                logger.info(f"Successfully updated preferences for user {user_id}")
            else:
                logger.warning(f"No valid fields to update for user {user_id}")

            # Get updated settings
            updated_settings = cls.get_user_settings(user_id)
            logger.info(f"Updated settings: {updated_settings}")
            return updated_settings

        except Exception as e:
            logger.error(f"Error updating user settings: {str(e)}", exc_info=True)
            db.session.rollback()
            abort(500, description=f"Error updating user settings: {str(e)}")

    @classmethod
    def update_theme_setting(cls, user_id: str, theme: str) -> Dict[str, Any]:
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

        return cls.update_user_settings(user_id, {"theme": theme})

    @classmethod
    def update_notification_settings(cls, user_id: str, email_enabled: bool, push_enabled: bool) -> Dict[str, Any]:
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

        return cls.update_user_settings(user_id, updates)

    @classmethod
    def update_currency_setting(cls, user_id: str, currency: str) -> Dict[str, Any]:
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

        return cls.update_user_settings(user_id, {"currency": currency})

    @classmethod
    def update_language_setting(cls, user_id: str, language: str) -> Dict[str, Any]:
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

        return cls.update_user_settings(user_id, {"language": language})