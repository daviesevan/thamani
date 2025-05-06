import React from 'react';
import { useTheme } from '../../context/ThemeContext';
import { Sun, Moon } from 'lucide-react';

const ThemeToggle = ({ className = '' }) => {
  const { theme, toggleTheme, isDarkMode } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={`p-2 rounded-none transition-colors ${
        isDarkMode 
          ? 'bg-gray-800 hover:bg-gray-700 text-gray-200' 
          : 'bg-gray-100 hover:bg-gray-200 text-gray-800'
      } ${className}`}
      aria-label={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
    >
      {isDarkMode ? (
        <Sun size={18} className="stroke-current" />
      ) : (
        <Moon size={18} className="stroke-current" />
      )}
    </button>
  );
};

export default ThemeToggle;
