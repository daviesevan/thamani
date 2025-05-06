import React, { createContext, useContext, useState, useEffect } from 'react';
import AuthService from '../services/auth';

// Define theme types
export const THEME_TYPES = {
  LIGHT: 'light',
  DARK: 'dark',
  SYSTEM: 'system',
};

// Create the theme context
const ThemeContext = createContext(null);

// Custom hook to use the theme context
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Theme provider component
export const ThemeProvider = ({ children }) => {
  // State to track current theme
  const [theme, setTheme] = useState(() => {
    // Try to get theme from localStorage first (for persistence between page reloads)
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      return savedTheme;
    }

    // If no saved theme, check user's system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return THEME_TYPES.DARK;
    }

    // Default to light theme
    return THEME_TYPES.LIGHT;
  });

  // State to track if theme is from user settings (will be used when auth is implemented)
  const [isUserPreference, setIsUserPreference] = useState(false);

  // Function to toggle theme
  const toggleTheme = () => {
    setTheme(prevTheme =>
      prevTheme === THEME_TYPES.LIGHT ? THEME_TYPES.DARK : THEME_TYPES.LIGHT
    );
    setIsUserPreference(true);
  };

  // Function to set theme explicitly
  const setThemeExplicitly = (newTheme) => {
    if (newTheme === THEME_TYPES.SYSTEM) {
      resetToSystemTheme();
    } else if (newTheme === THEME_TYPES.LIGHT || newTheme === THEME_TYPES.DARK) {
      setTheme(newTheme);
      setIsUserPreference(true);
    }
  };

  // Function to reset theme to system preference
  const resetToSystemTheme = () => {
    const systemTheme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      ? THEME_TYPES.DARK
      : THEME_TYPES.LIGHT;

    setTheme(systemTheme);
    setIsUserPreference(false);
  };

  // Update localStorage when theme changes
  useEffect(() => {
    localStorage.setItem('theme', theme);

    // Apply theme to document
    if (theme === THEME_TYPES.DARK) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  // Listen for system theme changes if not using user preference
  useEffect(() => {
    if (!isUserPreference) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

      const handleChange = (e) => {
        setTheme(e.matches ? THEME_TYPES.DARK : THEME_TYPES.LIGHT);
      };

      mediaQuery.addEventListener('change', handleChange);

      return () => {
        mediaQuery.removeEventListener('change', handleChange);
      };
    }
  }, [isUserPreference]);

  // Initialize theme from user preferences if available
  useEffect(() => {
    // Check if user is authenticated
    if (AuthService.isAuthenticated()) {
      // Get user from localStorage
      const user = AuthService.getCurrentUser();
      if (user && user.preferences && user.preferences.theme) {
        // If user has a theme preference, use it
        syncWithUserPreference(user.preferences.theme);
      }
    }
  }, []);

  // This function will be used when auth is implemented
  // to sync theme with user's database preference
  const syncWithUserPreference = (userTheme) => {
    if (userTheme) {
      setTheme(userTheme);
      setIsUserPreference(true);
    } else {
      resetToSystemTheme();
    }
  };

  // Value to be provided by the context
  const contextValue = {
    theme,
    isUserPreference,
    isDarkMode: theme === THEME_TYPES.DARK,
    toggleTheme,
    setTheme: setThemeExplicitly,
    resetToSystemTheme,
    syncWithUserPreference,
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
};
