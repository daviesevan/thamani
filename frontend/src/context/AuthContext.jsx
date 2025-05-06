import React, { createContext, useState, useEffect, useContext } from 'react';
import AuthService from '../services/auth';
import SettingsService from '../services/settings';
import api from '../services/api';

// Create the auth context
const AuthContext = createContext();

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userProfile, setUserProfile] = useState(null);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      setIsLoading(true);
      try {
        // Check if user is authenticated
        const isAuth = AuthService.isAuthenticated();
        setIsAuthenticated(isAuth);

        if (isAuth) {
          // Get user from localStorage
          const currentUser = AuthService.getCurrentUser();
          setUser(currentUser);

          // Fetch full user profile if we have a user
          if (currentUser && currentUser.id) {
            try {
              const response = await api.get(`/auth/profile/${currentUser.id}`);
              setUserProfile(response.data);
            } catch (error) {
              console.error('Error fetching user profile:', error);
            }
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Update auth state when user logs in
  const login = async (credentials) => {
    setIsLoading(true);
    try {
      const response = await AuthService.login(credentials);
      setUser(response.user);
      setIsAuthenticated(true);

      // Fetch full user profile
      if (response.user && response.user.id) {
        try {
          const profileResponse = await api.get(`/auth/profile/${response.user.id}`);
          setUserProfile(profileResponse.data);
        } catch (profileError) {
          console.error('Error fetching user profile after login:', profileError);
        }
      }

      return response;
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Update auth state when user logs out
  const logout = async () => {
    setIsLoading(true);
    try {
      await AuthService.logout();
      setUser(null);
      setUserProfile(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Error during logout:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Update user profile in context
  const updateUserProfile = async (userId, profileData) => {
    try {
      const response = await api.put(`/auth/profile/${userId}`, profileData);

      // Update local storage
      const updatedUser = {
        ...user,
        ...response.data
      };
      localStorage.setItem('user', JSON.stringify(updatedUser));

      // Update context state
      setUser(updatedUser);
      setUserProfile(response.data);

      return response.data;
    } catch (error) {
      console.error('Error updating user profile:', error);
      throw error;
    }
  };

  // Update user preferences in context
  const updateUserPreferences = async (userId, preferences) => {
    console.log('AuthContext: Updating user preferences', { userId, preferences });

    try {
      if (!userId) {
        throw new Error('User ID is required to update preferences');
      }

      // Use the settings service to update preferences
      const response = await SettingsService.updateUserSettings(userId, preferences);
      console.log('AuthContext: Preferences updated successfully', response);

      // Update userProfile in context
      setUserProfile(prev => {
        const updatedProfile = {
          ...prev,
          preferences: {
            ...(prev?.preferences || {}),
            ...preferences
          }
        };
        console.log('AuthContext: Updated user profile', updatedProfile);
        return updatedProfile;
      });

      // Update user in localStorage if needed
      const currentUser = AuthService.getCurrentUser();
      if (currentUser) {
        currentUser.preferences = {
          ...(currentUser.preferences || {}),
          ...preferences
        };
        localStorage.setItem('user', JSON.stringify(currentUser));
        console.log('AuthContext: Updated user in localStorage', currentUser);
      } else {
        console.warn('AuthContext: No user found in localStorage');
      }

      return response;
    } catch (error) {
      console.error('AuthContext: Error updating user preferences:', error);
      // Rethrow with more context
      throw new Error(`Failed to update preferences: ${error.message}`);
    }
  };

  // Refresh user profile data
  const refreshUserProfile = async () => {
    if (!user || !user.id) return;

    try {
      const response = await api.get(`/auth/profile/${user.id}`);
      setUserProfile(response.data);
      return response.data;
    } catch (error) {
      console.error('Error refreshing user profile:', error);
      throw error;
    }
  };

  // Value to be provided by the context
  const value = {
    user,
    userProfile,
    isAuthenticated,
    isLoading,
    login,
    logout,
    updateUserProfile,
    updateUserPreferences,
    refreshUserProfile
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
