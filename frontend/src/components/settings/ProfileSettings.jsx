import React, { useState, useEffect } from 'react';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import { User, Camera } from 'lucide-react';
import AuthService from '../../services/auth';
import api from '../../services/api';

const ProfileSettings = () => {
  const toast = useToast();
  const { user, userProfile, updateUserProfile, refreshUserProfile } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const [formData, setFormData] = useState({
    full_name: '',
    username: '',
    profile_image_url: ''
  });

  useEffect(() => {
    // Initialize form data from user profile
    if (userProfile) {
      setFormData({
        full_name: userProfile.full_name || '',
        username: userProfile.username || '',
        profile_image_url: userProfile.profile_image_url || ''
      });
    } else if (user) {
      // If we don't have the full profile yet, use what we have from the user object
      setFormData(prevData => ({
        ...prevData,
        full_name: user.full_name || '',
      }));

      // Refresh the user profile
      refreshUserProfile().catch(error => {
        console.error('Error refreshing user profile:', error);
      });
    }
  }, [user, userProfile, refreshUserProfile]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (!user || !user.id) {
        throw new Error('User not authenticated');
      }

      // Use the updateUserProfile method from AuthContext
      await updateUserProfile(user.id, formData);
      toast.success('Profile updated successfully');
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error(error.toString() || 'Failed to update profile');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="font-serif">
      <h2 className="text-xl font-bold mb-4">Profile Information</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Profile Image */}
        <div className="flex items-center space-x-4">
          <div className="relative">
            {formData.profile_image_url ? (
              <img
                src={formData.profile_image_url}
                alt="Profile"
                className="w-20 h-20 rounded-full object-cover"
              />
            ) : (
              <div className="w-20 h-20 rounded-full bg-secondary flex items-center justify-center">
                <User size={32} className="text-muted-foreground" />
              </div>
            )}
            <button
              type="button"
              className="absolute bottom-0 right-0 bg-primary text-white dark:text-black p-1 rounded-full"
              title="Upload image"
            >
              <Camera size={16} />
            </button>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">
              Upload a profile picture (coming soon)
            </p>
          </div>
        </div>

        {/* Full Name */}
        <div>
          <label htmlFor="full_name" className="block text-sm font-medium mb-1">
            Full Name
          </label>
          <input
            type="text"
            id="full_name"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            className="w-full p-2 border border-border bg-background focus:outline-none focus:ring-1 focus:ring-primary"
            placeholder="Your full name"
          />
        </div>

        {/* Username */}
        <div>
          <label htmlFor="username" className="block text-sm font-medium mb-1">
            Username
          </label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            className="w-full p-2 border border-border bg-background focus:outline-none focus:ring-1 focus:ring-primary"
            placeholder="Your username"
          />
          <p className="text-xs text-muted-foreground mt-1">
            This will be used for your public profile.
          </p>
        </div>

        {/* Email (read-only) */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium mb-1">
            Email
          </label>
          <input
            type="email"
            id="email"
            value={(userProfile && userProfile.email) || (user && user.email) || ''}
            readOnly
            className="w-full p-2 border border-border bg-secondary focus:outline-none cursor-not-allowed"
          />
          <p className="text-xs text-muted-foreground mt-1">
            Your email address cannot be changed.
          </p>
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
            {isLoading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProfileSettings;
