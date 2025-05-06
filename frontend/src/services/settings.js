import api from './api';

/**
 * Service for managing user settings
 */
const SettingsService = {
  /**
   * Get user settings
   *
   * @param {string} userId - User ID
   * @returns {Promise} Promise with user settings
   */
  getUserSettings: async (userId) => {
    try {
      const response = await api.get(`/settings/${userId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data?.error || error.message || 'Failed to get user settings';
    }
  },

  /**
   * Update user settings
   *
   * @param {string} userId - User ID
   * @param {Object} settings - Settings to update
   * @returns {Promise} Promise with updated user settings
   */
  updateUserSettings: async (userId, settings) => {
    try {
      console.log('Updating user settings:', { userId, settings });
      const response = await api.put(`/settings/${userId}`, settings);
      console.log('Settings update response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Settings update error:', error);
      // Create a more detailed error message
      const errorMessage = error.response?.data?.error || error.message || 'Failed to update user settings';
      throw new Error(`Settings update failed: ${errorMessage}`);
    }
  },

  /**
   * Update theme setting
   *
   * @param {string} userId - User ID
   * @param {string} theme - Theme preference ('light', 'dark', or 'system')
   * @returns {Promise} Promise with updated user settings
   */
  updateThemeSetting: async (userId, theme) => {
    try {
      const response = await api.put(`/settings/${userId}/theme`, { theme });
      return response.data;
    } catch (error) {
      throw error.response?.data?.error || error.message || 'Failed to update theme setting';
    }
  },

  /**
   * Update notification settings
   *
   * @param {string} userId - User ID
   * @param {boolean} emailEnabled - Whether email notifications are enabled
   * @param {boolean} pushEnabled - Whether push notifications are enabled
   * @returns {Promise} Promise with updated user settings
   */
  updateNotificationSettings: async (userId, emailEnabled, pushEnabled) => {
    try {
      const response = await api.put(`/settings/${userId}/notifications`, {
        email: emailEnabled,
        push: pushEnabled
      });
      return response.data;
    } catch (error) {
      throw error.response?.data?.error || error.message || 'Failed to update notification settings';
    }
  },

  /**
   * Update currency setting
   *
   * @param {string} userId - User ID
   * @param {string} currency - Currency code (e.g., 'KES', 'USD')
   * @returns {Promise} Promise with updated user settings
   */
  updateCurrencySetting: async (userId, currency) => {
    try {
      const response = await api.put(`/settings/${userId}/currency`, { currency });
      return response.data;
    } catch (error) {
      throw error.response?.data?.error || error.message || 'Failed to update currency setting';
    }
  },

  /**
   * Update language setting
   *
   * @param {string} userId - User ID
   * @param {string} language - Language code (e.g., 'en', 'sw')
   * @returns {Promise} Promise with updated user settings
   */
  updateLanguageSetting: async (userId, language) => {
    try {
      const response = await api.put(`/settings/${userId}/language`, { language });
      return response.data;
    } catch (error) {
      throw error.response?.data?.error || error.message || 'Failed to update language setting';
    }
  }
};

export default SettingsService;
