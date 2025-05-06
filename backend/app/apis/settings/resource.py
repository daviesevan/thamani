import asyncio
import logging
from flask import Blueprint, jsonify, request
from app.services.settings import SettingsService
from app.utils.request_utils import get_request_data

# Set up logger
logger = logging.getLogger(__name__)

# Create the settings blueprint
settings = Blueprint("settings", __name__, url_prefix="/settings")


@settings.route('/<user_id>', methods=['GET'])
def get_user_settings(user_id):
    """
    Get a user's settings and preferences.
    """
    try:
        # Run the async function in the synchronous Flask context
        result = asyncio.run(SettingsService.get_user_settings(user_id))
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error getting user settings: {str(e)}")
        return jsonify({'error': str(e)}), 500


@settings.route('/<user_id>', methods=['PUT'])
def update_user_settings(user_id):
    """
    Update a user's settings and preferences.
    """
    logger.info(f"Received request to update settings for user {user_id}")

    # Log request headers for debugging
    logger.info(f"Request headers: {dict(request.headers)}")

    # Get request data
    data = get_request_data(request)
    logger.info(f"Request data: {data}")

    try:
        # Run the async function in the synchronous Flask context
        result = asyncio.run(SettingsService.update_user_settings(user_id, data))
        logger.info(f"Settings updated successfully for user {user_id}")
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error updating user settings: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'status': 'error',
            'message': f"Failed to update settings: {str(e)}"
        }), 500


@settings.route('/<user_id>/theme', methods=['PUT'])
def update_theme_setting(user_id):
    """
    Update a user's theme preference.
    """
    data = get_request_data(request)
    theme = data.get('theme')

    if not theme:
        return jsonify({'error': 'Theme value is required'}), 400

    try:
        # Run the async function in the synchronous Flask context
        result = asyncio.run(SettingsService.update_theme_setting(user_id, theme))
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error updating theme setting: {str(e)}")
        return jsonify({'error': str(e)}), 500


@settings.route('/<user_id>/notifications', methods=['PUT'])
def update_notification_settings(user_id):
    """
    Update a user's notification settings.
    """
    data = get_request_data(request)
    email_enabled = data.get('email', True)
    push_enabled = data.get('push', True)

    try:
        # Run the async function in the synchronous Flask context
        result = asyncio.run(SettingsService.update_notification_settings(
            user_id, email_enabled, push_enabled))
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error updating notification settings: {str(e)}")
        return jsonify({'error': str(e)}), 500


@settings.route('/<user_id>/currency', methods=['PUT'])
def update_currency_setting(user_id):
    """
    Update a user's currency preference.
    """
    data = get_request_data(request)
    currency = data.get('currency')

    if not currency:
        return jsonify({'error': 'Currency code is required'}), 400

    try:
        # Run the async function in the synchronous Flask context
        result = asyncio.run(SettingsService.update_currency_setting(user_id, currency))
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error updating currency setting: {str(e)}")
        return jsonify({'error': str(e)}), 500


@settings.route('/<user_id>/language', methods=['PUT'])
def update_language_setting(user_id):
    """
    Update a user's language preference.
    """
    data = get_request_data(request)
    language = data.get('language')

    if not language:
        return jsonify({'error': 'Language code is required'}), 400

    try:
        # Run the async function in the synchronous Flask context
        result = asyncio.run(SettingsService.update_language_setting(user_id, language))
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error updating language setting: {str(e)}")
        return jsonify({'error': str(e)}), 500
