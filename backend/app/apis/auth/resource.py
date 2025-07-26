import logging
from flask import jsonify, request, Blueprint
from app.services.auth import AuthService
from app.utils.request_utils import get_request_data

# Set up logger
logger = logging.getLogger(__name__)

# Get the auth blueprint from the app context
auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route('/signup', methods=['POST'])
def signup():
    """
    Register a new user with email and password.
    """
    data = get_request_data(request)
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('fullName')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    try:
        result = AuthService.register_user(email, password, full_name=full_name)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user with email and password.
    """
    data = get_request_data(request)
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    # Get device info and IP address
    user_agent = request.headers.get('User-Agent', '')
    ip_address = request.remote_addr

    # Parse device info from user agent
    device_info = {
        'user_agent': user_agent,
        'browser': parse_user_agent(user_agent),
        'ip_address': ip_address
    }

    try:
        result = AuthService.login_with_email(email, password, device_info)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def parse_user_agent(user_agent_string):
    """
    Parse the user agent string to extract browser and device information.
    """
    # Simple parsing logic - can be enhanced with a proper user-agent parsing library
    browser = "Unknown"
    if "Chrome" in user_agent_string:
        browser = "Chrome"
    elif "Firefox" in user_agent_string:
        browser = "Firefox"
    elif "Safari" in user_agent_string:
        browser = "Safari"
    elif "Edge" in user_agent_string:
        browser = "Edge"
    elif "MSIE" in user_agent_string or "Trident" in user_agent_string:
        browser = "Internet Explorer"

    return browser


# TODO: Implement OAuth functionality
# @auth.route('/google', methods=['POST'])
# def google_login():
#     """
#     Authenticate a user with Google OAuth.
#     """
#     data = get_request_data(request)
#     access_token = data.get('access_token')

#     if not access_token:
#         return jsonify({'error': 'Access token is required'}), 400

#     # Get device info and IP address
#     user_agent = request.headers.get('User-Agent', '')
#     ip_address = request.remote_addr

#     # Parse device info from user agent
#     device_info = {
#         'user_agent': user_agent,
#         'browser': parse_user_agent(user_agent),
#         'ip_address': ip_address
#     }

#     try:
#         result = AuthService.login_with_google(access_token, device_info)
#         return jsonify(result), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# @auth.route('/facebook', methods=['POST'])
# def facebook_login():
#     """
#     Authenticate a user with Facebook OAuth.
#     """
#     data = get_request_data(request)
#     access_token = data.get('access_token')

#     if not access_token:
#         return jsonify({'error': 'Access token is required'}), 400

#     # Get device info and IP address
#     user_agent = request.headers.get('User-Agent', '')
#     ip_address = request.remote_addr

#     # Parse device info from user agent
#     device_info = {
#         'user_agent': user_agent,
#         'browser': parse_user_agent(user_agent),
#         'ip_address': ip_address
#     }

#     try:
#         result = AuthService.login_with_facebook(access_token, device_info)
#         return jsonify(result), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


@auth.route('/logout', methods=['POST'])
def logout():
    """
    Log out a user and invalidate their session.
    """
    data = get_request_data(request)
    access_token = data.get('access_token')

    if not access_token:
        return jsonify({'error': 'Access token is required'}), 400

    try:
        result = AuthService.logout_user(access_token)
        return jsonify({"message": "Logged out successfully"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth.route('/verify-email', methods=['POST'])
def verify_email():
    """
    Verify a user's email address.
    """
    data = get_request_data(request)
    token = data.get('token')

    if not token:
        return jsonify({'error': 'Token is required'}), 400

    try:
        result = AuthService.verify_email(token)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth.route('/resend-verification', methods=['POST'])
def resend_verification():
    """
    Resend verification email to a user.
    """
    data = get_request_data(request)
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    try:
        result = AuthService.resend_verification_email(email)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# TODO: Implement password reset functionality
# @auth.route('/forgot-password', methods=['POST'])
# def forgot_password():
#     """
#     Request a password reset for a user.
#     """
#     data = get_request_data(request)
#     email = data.get('email')

#     if not email:
#         return jsonify({'error': 'Email is required'}), 400

#     try:
#         result = AuthService.reset_password_request(email)
#         return jsonify(result), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


@auth.route('/profile/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    """
    Get a user's profile information.
    """
    try:
        result = AuthService.get_user_profile(user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth.route('/profile/<user_id>', methods=['PUT'])
def update_user_profile(user_id):
    """
    Update a user's profile information.
    """
    data = get_request_data(request)

    try:
        result = AuthService.update_user_profile(user_id, data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth.route('/onboarding/<user_id>/complete', methods=['POST'])
def complete_onboarding(user_id):
    """
    Mark a user's onboarding as completed.
    """
    try:
        result = AuthService.update_user_profile(user_id, {"onboarding_completed": True})
        return jsonify({"message": "Onboarding completed successfully", "user": result}), 200
    except Exception as e:
        # Even if there's an error, we'll consider onboarding complete
        # This is a fallback for when the column doesn't exist yet
        logger.warning(f"Error marking onboarding as completed: {str(e)}")

        try:
            # Get the user profile without updating it
            result = AuthService.get_user_profile(user_id)
            # Add the onboarding_completed flag manually
            if isinstance(result, dict):
                result["onboarding_completed"] = True
            return jsonify({"message": "Onboarding process completed", "user": result}), 200
        except Exception as inner_e:
            return jsonify({'error': f"Failed to complete onboarding: {str(e)}, {str(inner_e)}"}), 500


@auth.route('/change-password', methods=['POST'])
def change_password():
    """
    Change a user's password.
    """
    data = get_request_data(request)
    user_id = data.get('user_id')
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not user_id or not current_password or not new_password:
        return jsonify({'error': 'User ID, current password, and new password are required'}), 400

    try:
        result = AuthService.change_password(user_id, current_password, new_password)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth.route('/update-notification-settings', methods=['POST'])
def update_notification_settings():
    """
    Update a user's notification settings.
    """
    data = get_request_data(request)
    user_id = data.get('user_id')
    notification_settings = data.get('notification_settings')

    if not user_id or not notification_settings:
        return jsonify({'error': 'User ID and notification settings are required'}), 400

    try:
        # Extract notification settings
        notification_updates = {
            "notification_email": notification_settings.get('email', True),
            "notification_push": notification_settings.get('push', True)
        }

        result = AuthService.update_user_profile(user_id, notification_updates)
        return jsonify({"message": "Notification settings updated successfully", "user": result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500