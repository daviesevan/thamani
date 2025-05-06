import api from './api';

/**
 * Authentication service for handling user authentication
 */
const AuthService = {
  /**
   * Register a new user with email and password
   *
   * @param {Object} userData - User registration data
   * @param {string} userData.email - User's email
   * @param {string} userData.password - User's password
   * @param {string} userData.fullName - User's full name
   * @returns {Promise} Promise with registration result
   */
  signup: async (userData) => {
    try {
      const response = await api.post('/auth/signup', userData);
      if (response.data.session) {
        localStorage.setItem('auth_token', response.data.session.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      return response.data;
    } catch (error) {
      throw error.response?.data?.error || error.message || 'Registration failed';
    }
  },

  /**
   * Authenticate a user with email and password
   *
   * @param {Object} credentials - User login credentials
   * @param {string} credentials.email - User's email
   * @param {string} credentials.password - User's password
   * @returns {Promise} Promise with login result
   */
  login: async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials);
      if (response.data.session) {
        localStorage.setItem('auth_token', response.data.session.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      return response.data;
    } catch (error) {
      throw error.response?.data?.error || error.message || 'Login failed';
    }
  },

  /**
   * Authenticate a user with Google OAuth
   *
   * @param {string} accessToken - Google OAuth access token
   * @returns {Promise} Promise with login result
   */
  loginWithGoogle: async (accessToken) => {
    try {
      const response = await api.post('/auth/google', { access_token: accessToken });
      if (response.data.session) {
        localStorage.setItem('auth_token', response.data.session.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      return response.data;
    } catch (error) {
      throw error.response?.data?.error || error.message || 'Google login failed';
    }
  },

  /**
   * Log out a user and invalidate their session
   *
   * @returns {Promise} Promise with logout result
   */
  logout: async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (token) {
        await api.post('/auth/logout', { access_token: token });
      }
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      return { success: true };
    } catch (error) {
      // Still remove local storage items even if the API call fails
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      throw error.response?.data?.error || error.message || 'Logout failed';
    }
  },

  /**
   * Request a password reset for a user
   *
   * @param {string} email - User's email address
   * @returns {Promise} Promise with reset request result
   */
  forgotPassword: async (email) => {
    try {
      const response = await api.post('/auth/forgot-password', { email });
      return response.data;
    } catch (error) {
      throw error.response?.data?.error || error.message || 'Password reset request failed';
    }
  },

  /**
   * Change a user's password
   *
   * @param {string} userId - User's ID
   * @param {string} currentPassword - User's current password
   * @param {string} newPassword - User's new password
   * @returns {Promise} Promise with password change result
   */
  changePassword: async (userId, currentPassword, newPassword) => {
    try {
      const response = await api.post('/auth/change-password', {
        user_id: userId,
        current_password: currentPassword,
        new_password: newPassword
      });
      return response.data;
    } catch (error) {
      throw error.response?.data?.error || error.message || 'Password change failed';
    }
  },

  /**
   * Update a user's notification settings
   *
   * @param {string} userId - User's ID
   * @param {Object} settings - Notification settings
   * @param {boolean} settings.email - Email notification setting
   * @param {boolean} settings.push - Push notification setting
   * @returns {Promise} Promise with update result
   */
  updateNotificationSettings: async (userId, settings) => {
    try {
      const response = await api.post('/auth/update-notification-settings', {
        user_id: userId,
        notification_settings: settings
      });

      // Update the user in localStorage with the updated settings
      if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }

      return response.data;
    } catch (error) {
      throw error.response?.data?.error || error.message || 'Failed to update notification settings';
    }
  },

  /**
   * Get the current authenticated user
   *
   * @returns {Object|null} User object or null if not authenticated
   */
  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch (e) {
        return null;
      }
    }
    return null;
  },

  /**
   * Check if a user is authenticated
   *
   * @returns {boolean} True if authenticated, false otherwise
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('auth_token');
  },

  /**
   * Check if a user has completed onboarding
   *
   * @returns {boolean} True if onboarding is completed, false otherwise
   */
  hasCompletedOnboarding: () => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        return !!user.onboarding_completed;
      } catch (e) {
        return false;
      }
    }
    return false;
  },

  /**
   * Complete the onboarding process for a user
   *
   * @returns {Promise} Promise with onboarding completion result
   */
  completeOnboarding: async () => {
    try {
      const user = AuthService.getCurrentUser();
      if (!user || !user.id) {
        throw new Error('User not authenticated');
      }

      const response = await api.post(`/auth/onboarding/${user.id}/complete`);

      // Update the user in localStorage with the updated onboarding status
      if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }

      return response.data;
    } catch (error) {
      console.error('Error completing onboarding:', error);

      // Even if the API call fails, we'll mark onboarding as completed locally
      // This is a fallback for when the backend can't update the database
      try {
        const user = AuthService.getCurrentUser();
        if (user) {
          user.onboarding_completed = true;
          localStorage.setItem('user', JSON.stringify(user));
        }

        return {
          message: "Onboarding completed (local only)",
          user: user
        };
      } catch (localError) {
        console.error('Error updating local user data:', localError);
        throw error.response?.data?.error || error.message || 'Failed to complete onboarding';
      }
    }
  },

  /**
   * Handle email verification from Supabase redirect
   *
   * @param {Object} params - URL parameters from the redirect
   * @returns {Object} Verification result
   */
  handleVerification: (params) => {
    const accessToken = params.get('access_token');
    const type = params.get('type');
    const expiresIn = params.get('expires_in');
    const refreshToken = params.get('refresh_token');
    const tokenType = params.get('token_type');

    if (accessToken && type === 'signup') {
      // Store auth data
      localStorage.setItem('auth_token', accessToken);

      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
      }

      // Extract user information from JWT token
      try {
        // Parse the JWT token to get user info
        const base64Url = accessToken.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));

        const payload = JSON.parse(jsonPayload);

        // Create a user object from the token payload
        const user = {
          id: payload.sub,
          email: payload.email,
          full_name: payload.user_metadata?.full_name || '',
          email_verified: payload.user_metadata?.email_verified || true
        };

        // Store user data
        localStorage.setItem('user', JSON.stringify(user));
      } catch (error) {
        console.error('Error parsing JWT token:', error);
      }

      return {
        success: true,
        message: 'Email verified successfully'
      };
    }

    return {
      success: false,
      message: 'Invalid verification link'
    };
  }
};

export default AuthService;
