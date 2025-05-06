import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { User, Lock, Bell, Palette, DollarSign, LogOut } from 'lucide-react';
import ProfileSettings from '../components/settings/ProfileSettings';
import PasswordSettings from '../components/settings/PasswordSettings';
import NotificationSettings from '../components/settings/NotificationSettings';
import ThemeSettings from '../components/settings/ThemeSettings';
import CurrencySettings from '../components/settings/CurrencySettings';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { useNavigate } from 'react-router-dom';

const Settings = () => {
  const toast = useToast();
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  useEffect(() => {
    // Check if there's a hash in the URL and set the active tab accordingly
    const hash = window.location.hash.replace('#', '');
    if (hash && ['profile', 'password', 'notifications', 'appearance', 'currency'].includes(hash)) {
      setActiveTab(hash);
    }
  }, []);

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    window.location.hash = tab;
  };

  const handleLogout = async () => {
    setIsLoggingOut(true);

    try {
      await logout();
      toast.success('Logged out successfully');
      navigate('/signin');
    } catch (error) {
      console.error('Logout error:', error);
      toast.error('Failed to log out. Please try again.');
    } finally {
      setIsLoggingOut(false);
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return <ProfileSettings />;
      case 'password':
        return <PasswordSettings />;
      case 'notifications':
        return <NotificationSettings />;
      case 'appearance':
        return <ThemeSettings />;
      case 'currency':
        return <CurrencySettings />;
      default:
        return <ProfileSettings />;
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-6"
      >
        <h1 className="text-3xl font-serif font-bold">Settings</h1>
        <p className="text-muted-foreground mt-2">
          Manage your account settings and preferences
        </p>
      </motion.div>

      <div className="flex flex-col md:flex-row gap-8">
        {/* Sidebar */}
        <div className="w-full md:w-64 shrink-0">
          <nav className="space-y-1 border border-border">
            <button
              onClick={() => handleTabChange('profile')}
              className={`flex items-center w-full px-4 py-3 text-sm font-medium ${
                activeTab === 'profile'
                  ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                  : 'text-muted-foreground hover:bg-secondary/50'
              }`}
            >
              <User size={18} className="mr-3" />
              Profile
            </button>

            <button
              onClick={() => handleTabChange('password')}
              className={`flex items-center w-full px-4 py-3 text-sm font-medium ${
                activeTab === 'password'
                  ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                  : 'text-muted-foreground hover:bg-secondary/50'
              }`}
            >
              <Lock size={18} className="mr-3" />
              Password
            </button>

            <button
              onClick={() => handleTabChange('notifications')}
              className={`flex items-center w-full px-4 py-3 text-sm font-medium ${
                activeTab === 'notifications'
                  ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                  : 'text-muted-foreground hover:bg-secondary/50'
              }`}
            >
              <Bell size={18} className="mr-3" />
              Notifications
            </button>

            <button
              onClick={() => handleTabChange('appearance')}
              className={`flex items-center w-full px-4 py-3 text-sm font-medium ${
                activeTab === 'appearance'
                  ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                  : 'text-muted-foreground hover:bg-secondary/50'
              }`}
            >
              <Palette size={18} className="mr-3" />
              Appearance
            </button>

            <button
              onClick={() => handleTabChange('currency')}
              className={`flex items-center w-full px-4 py-3 text-sm font-medium ${
                activeTab === 'currency'
                  ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                  : 'text-muted-foreground hover:bg-secondary/50'
              }`}
            >
              <DollarSign size={18} className="mr-3" />
              Currency
            </button>

            <button
              onClick={handleLogout}
              disabled={isLoggingOut}
              className="flex items-center w-full px-4 py-3 text-sm font-medium text-red-500 hover:bg-red-50 dark:hover:bg-red-900/10"
            >
              <LogOut size={18} className="mr-3" />
              {isLoggingOut ? 'Logging out...' : 'Log out'}
            </button>
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 border border-border p-6">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            {renderTabContent()}
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
