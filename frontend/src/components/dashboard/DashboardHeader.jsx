import React, { useState } from 'react';
import { Bell, User } from 'lucide-react';
import ThemeToggle from '../common/ThemeToggle';
import SearchBar from '../common/SearchBar';
import { motion } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';

const DashboardHeader = () => {
  const { user, userProfile } = useAuth();

  const handleSearch = (query) => {
    // Implement search functionality here
    console.log('Searching for:', query);
  };

  return (
    <header className="bg-background border-b border-border py-3 px-4 md:px-8">
      <div className="flex items-center justify-between">
        {/* Search Bar */}
        <div className="flex-1 max-w-xl">
          <SearchBar
            placeholder="Search for products, retailers..."
            onSearch={handleSearch}
          />
        </div>

        {/* Right Side - User Menu, Notifications, Theme Toggle */}
        <div className="flex items-center ml-4 space-x-4">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 text-muted-foreground hover:text-foreground transition-colors relative"
          >
            <Bell size={20} />
            <span className="absolute top-1 right-1 w-2 h-2 bg-primary rounded-full"></span>
          </motion.button>

          <ThemeToggle />

          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white dark:text-black font-serif">
              {userProfile && userProfile.full_name
                ? userProfile.full_name.charAt(0)
                : user && user.full_name
                  ? user.full_name.charAt(0)
                  : 'U'}
            </div>
            <span className="hidden md:inline-block font-serif text-sm">
              {userProfile && userProfile.full_name
                ? userProfile.full_name
                : user && user.full_name
                  ? user.full_name
                  : 'User'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default DashboardHeader;
