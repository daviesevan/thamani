import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, TrendingUp, TrendingDown, Clock, AlertCircle } from 'lucide-react';

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Get user data from localStorage
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        const userData = JSON.parse(userStr);
        setUser(userData);
      } catch (e) {
        console.error('Error parsing user data:', e);
      }
    }
    setIsLoading(false);
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-serif font-bold">
          Welcome{user?.full_name ? `, ${user.full_name}` : ''}
        </h1>
        <p className="text-muted-foreground mt-2">
          Track prices, set alerts, and save money on your favorite products.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          className="bg-background border border-border p-4 rounded-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <div className="flex items-center justify-between">
            <h3 className="font-serif font-medium">Tracked Products</h3>
            <div className="p-2 bg-primary/10 rounded-full">
              <Search size={18} className="text-primary" />
            </div>
          </div>
          <p className="text-3xl font-serif font-bold mt-2">0</p>
          <p className="text-sm text-muted-foreground mt-1">Products you're tracking</p>
        </motion.div>

        <motion.div
          className="bg-background border border-border p-4 rounded-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          <div className="flex items-center justify-between">
            <h3 className="font-serif font-medium">Price Drops</h3>
            <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-full">
              <TrendingDown size={18} className="text-green-600 dark:text-green-400" />
            </div>
          </div>
          <p className="text-3xl font-serif font-bold mt-2">0</p>
          <p className="text-sm text-muted-foreground mt-1">Products with price drops</p>
        </motion.div>

        <motion.div
          className="bg-background border border-border p-4 rounded-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
        >
          <div className="flex items-center justify-between">
            <h3 className="font-serif font-medium">Price Increases</h3>
            <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-full">
              <TrendingUp size={18} className="text-red-600 dark:text-red-400" />
            </div>
          </div>
          <p className="text-3xl font-serif font-bold mt-2">0</p>
          <p className="text-sm text-muted-foreground mt-1">Products with price increases</p>
        </motion.div>

        <motion.div
          className="bg-background border border-border p-4 rounded-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.4 }}
        >
          <div className="flex items-center justify-between">
            <h3 className="font-serif font-medium">Active Alerts</h3>
            <div className="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-full">
              <AlertCircle size={18} className="text-amber-600 dark:text-amber-400" />
            </div>
          </div>
          <p className="text-3xl font-serif font-bold mt-2">0</p>
          <p className="text-sm text-muted-foreground mt-1">Price alerts you've set</p>
        </motion.div>
      </div>

      <motion.div
        className="bg-background border border-border p-6 rounded-md"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.5 }}
      >
        <h2 className="text-xl font-serif font-bold mb-4">Recent Price Changes</h2>
        <div className="text-center py-8">
          <Clock size={48} className="mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No recent price changes to display.</p>
          <p className="text-sm text-muted-foreground mt-2">
            Start tracking products to see price changes here.
          </p>
          <button className="mt-4 px-4 py-2 bg-primary text-white dark:text-black font-serif hover:bg-primary/90 transition-colors rounded-md">
            Track a Product
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;
