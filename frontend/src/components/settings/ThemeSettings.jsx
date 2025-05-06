import React, { useState, useEffect } from 'react';
import { useTheme, THEME_TYPES } from '../../context/ThemeContext';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { Sun, Moon, Monitor } from 'lucide-react';

const ThemeSettings = () => {
  const { theme, setTheme, resetToSystemTheme, isUserPreference } = useTheme();
  const { user, userProfile, updateUserPreferences } = useAuth();
  const toast = useToast();
  const [isLoading, setIsLoading] = useState(false);

  // Function to update theme with toast notifications and backend sync
  const updateTheme = async (newTheme) => {
    if (isLoading) return;

    setIsLoading(true);

    try {
      // Update theme in context first for immediate feedback
      if (newTheme === THEME_TYPES.SYSTEM) {
        resetToSystemTheme();
      } else {
        setTheme(newTheme);
      }

      // Update theme in backend if user is authenticated
      if (user && user.id) {
        await updateUserPreferences(user.id, { theme: newTheme });
        toast.success(`Theme changed to ${newTheme} mode`);
      }
    } catch (error) {
      console.error('Error updating theme:', error);
      toast.error('Failed to save theme preference');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="font-serif">
      <h2 className="text-xl font-bold mb-4">Appearance</h2>

      <div className="space-y-4">
        <p className="text-sm text-muted-foreground">
          Choose how the application looks to you. Select a light or dark theme, or follow your system settings.
        </p>

        <div className="grid grid-cols-3 gap-4 mt-4">
          {/* Light Theme Option */}
          <button
            onClick={() => updateTheme(THEME_TYPES.LIGHT)}
            disabled={isLoading}
            className={`flex flex-col items-center p-4 border ${
              theme === THEME_TYPES.LIGHT && isUserPreference
                ? 'border-primary'
                : 'border-border'
            } ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
            aria-label="Use light theme"
          >
            <div className="w-full h-24 bg-white border border-gray-200 mb-3 flex items-center justify-center">
              <Sun size={24} className="text-black" />
            </div>
            <span className="text-sm font-medium">Light</span>
          </button>

          {/* Dark Theme Option */}
          <button
            onClick={() => updateTheme(THEME_TYPES.DARK)}
            disabled={isLoading}
            className={`flex flex-col items-center p-4 border ${
              theme === THEME_TYPES.DARK && isUserPreference
                ? 'border-primary'
                : 'border-border'
            } ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
            aria-label="Use dark theme"
          >
            <div className="w-full h-24 bg-gray-900 border border-gray-700 mb-3 flex items-center justify-center">
              <Moon size={24} className="text-white" />
            </div>
            <span className="text-sm font-medium">Dark</span>
          </button>

          {/* System Theme Option */}
          <button
            onClick={() => updateTheme(THEME_TYPES.SYSTEM)}
            disabled={isLoading}
            className={`flex flex-col items-center p-4 border ${
              !isUserPreference
                ? 'border-primary'
                : 'border-border'
            } ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
            aria-label="Use system theme"
          >
            <div className="w-full h-24 bg-gradient-to-r from-white to-gray-900 border border-gray-200 mb-3 flex items-center justify-center">
              <Monitor size={24} className="text-gray-500" />
            </div>
            <span className="text-sm font-medium">System</span>
          </button>
        </div>

        <p className="text-xs text-muted-foreground mt-2">
          Your theme preference will be saved and applied across all your devices when you are logged in.
        </p>
      </div>
    </div>
  );
};

export default ThemeSettings;
