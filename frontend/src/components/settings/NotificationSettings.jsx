import React, { useState, useEffect } from 'react';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import { Bell, Mail } from 'lucide-react';
import AuthService from '../../services/auth';
import api from '../../services/api';

const NotificationSettings = () => {
  const toast = useToast();
  const { user, userProfile, updateUserPreferences } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const [settings, setSettings] = useState({
    email: true,
    push: true
  });

  useEffect(() => {
    // Initialize settings from user profile
    if (userProfile && userProfile.preferences) {
      const preferences = userProfile.preferences;
      setSettings({
        email: preferences.notification_email !== false,
        push: preferences.notification_push !== false
      });
    }
  }, [userProfile]);

  const handleToggle = (setting) => {
    setSettings(prev => ({
      ...prev,
      [setting]: !prev[setting]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (!user || !user.id) {
        throw new Error('User not authenticated');
      }

      // Convert settings to the format expected by the API
      const notificationPreferences = {
        notification_email: settings.email,
        notification_push: settings.push
      };

      // Use the updateUserPreferences method from AuthContext
      await updateUserPreferences(user.id, notificationPreferences);
      toast.success('Notification settings updated successfully');
    } catch (error) {
      console.error('Error updating notification settings:', error);
      toast.error(error.toString() || 'Failed to update notification settings');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="font-serif">
      <h2 className="text-xl font-bold mb-4">Notification Settings</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        <p className="text-sm text-muted-foreground">
          Choose how you want to receive notifications about price drops, deals, and other updates.
        </p>

        <div className="space-y-4">
          {/* Email Notifications */}
          <div className="flex items-center justify-between p-4 border border-border">
            <div className="flex items-center space-x-3">
              <div className="text-primary">
                <Mail size={20} />
              </div>
              <div>
                <h3 className="text-sm font-medium">Email Notifications</h3>
                <p className="text-xs text-muted-foreground">
                  Receive price alerts and updates via email
                </p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={settings.email}
                onChange={() => handleToggle('email')}
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
            </label>
          </div>

          {/* Push Notifications */}
          <div className="flex items-center justify-between p-4 border border-border">
            <div className="flex items-center space-x-3">
              <div className="text-primary">
                <Bell size={20} />
              </div>
              <div>
                <h3 className="text-sm font-medium">Push Notifications</h3>
                <p className="text-xs text-muted-foreground">
                  Receive real-time alerts on your device
                </p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={settings.push}
                onChange={() => handleToggle('push')}
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
            </label>
          </div>
        </div>

        {/* Submit Button */}
        <div>
          <button
            type="submit"
            disabled={isLoading}
            className={`py-2 px-4 border border-transparent font-medium text-sm bg-primary text-white dark:text-black hover:bg-primary/90 focus:outline-none focus:ring-1 focus:ring-primary ${
              isLoading ? 'opacity-70 cursor-not-allowed' : ''
            }`}
          >
            {isLoading ? 'Saving...' : 'Save Preferences'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default NotificationSettings;
