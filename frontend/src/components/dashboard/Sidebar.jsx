import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Home,
  ShoppingBag,
  Bell,
  Heart,
  Settings,
  LogOut,
  Menu,
  X,
  BarChart3,
  Search
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';

const Sidebar = () => {
  const location = useLocation();
  const toast = useToast();
  const { logout } = useAuth();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('Successfully logged out');
      window.location.href = '/signin';
    } catch (error) {
      console.error('Logout error:', error);
      toast.error('Failed to log out. Please try again.');
    }
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: <Home size={20} /> },
    { name: 'Search Products', path: '/dashboard/search', icon: <Search size={20} /> },
    { name: 'Tracked Products', path: '/dashboard/products', icon: <ShoppingBag size={20} /> },
    { name: 'Price Alerts', path: '/dashboard/alerts', icon: <Bell size={20} /> },
    { name: 'Wishlist', path: '/dashboard/wishlist', icon: <Heart size={20} /> },
    { name: 'Analytics', path: '/dashboard/analytics', icon: <BarChart3 size={20} /> },
    { name: 'Settings', path: '/dashboard/settings', icon: <Settings size={20} /> },
  ];

  const isActive = (path) => {
    if (path === '/dashboard') {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const toggleMobileSidebar = () => {
    setIsMobileOpen(!isMobileOpen);
  };

  const sidebarVariants = {
    expanded: { width: '240px' },
    collapsed: { width: '70px' }
  };

  const mobileSidebarVariants = {
    open: { x: 0 },
    closed: { x: '-100%' }
  };

  return (
    <>
      {/* Mobile menu button */}
      <button
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-background border border-border rounded-md"
        onClick={toggleMobileSidebar}
      >
        {isMobileOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Mobile sidebar overlay */}
      {isMobileOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-40"
          onClick={toggleMobileSidebar}
        />
      )}

      {/* Mobile sidebar */}
      <motion.div
        className="md:hidden fixed top-0 left-0 h-full w-[240px] bg-background border-r border-border z-40 flex flex-col"
        initial="closed"
        animate={isMobileOpen ? "open" : "closed"}
        variants={mobileSidebarVariants}
        transition={{ duration: 0.3, ease: "easeInOut" }}
      >
        <div className="p-4 border-b border-border">
          <h1 className="text-2xl font-serif font-bold">Thamani</h1>
        </div>
        <div className="flex-1 overflow-y-auto py-4">
          <nav className="space-y-1 px-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-3 py-2 text-sm font-medium ${
                  isActive(item.path)
                    ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                    : 'text-muted-foreground hover:bg-secondary/50'
                }`}
                onClick={() => setIsMobileOpen(false)}
              >
                <span className="mr-3">{item.icon}</span>
                <span>{item.name}</span>
              </Link>
            ))}
          </nav>
        </div>
        <div className="p-4 border-t border-border">
          <button
            onClick={handleLogout}
            className="flex items-center w-full px-3 py-2 text-sm font-medium rounded-md hover:bg-secondary transition-colors"
          >
            <LogOut size={20} className="mr-3" />
            <span>Logout</span>
          </button>
        </div>
      </motion.div>

      {/* Desktop sidebar */}
      <motion.div
        className="hidden md:flex h-screen fixed left-0 top-0 flex-col border-r border-border bg-background z-40"
        initial="expanded"
        animate={isCollapsed ? "collapsed" : "expanded"}
        variants={sidebarVariants}
        transition={{ duration: 0.3, ease: "easeInOut" }}
      >
        <div className="p-4 border-b border-border flex items-center justify-between">
          {!isCollapsed && <h1 className="text-2xl font-serif font-bold">Thamani</h1>}
          <button
            onClick={toggleSidebar}
            className={`p-1 rounded-md hover:bg-secondary transition-colors ${isCollapsed ? 'mx-auto' : ''}`}
          >
            {isCollapsed ? <Menu size={20} /> : <X size={20} />}
          </button>
        </div>
        <div className="flex-1 overflow-y-auto py-4">
          <nav className="space-y-1 px-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-3 py-2 text-sm font-medium ${
                  isActive(item.path)
                    ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                    : 'text-muted-foreground hover:bg-secondary/50'
                } ${isCollapsed ? 'justify-center' : ''}`}
              >
                <span className={isCollapsed ? '' : 'mr-3'}>{item.icon}</span>
                {!isCollapsed && <span>{item.name}</span>}
              </Link>
            ))}
          </nav>
        </div>
        <div className="p-4 border-t border-border">
          <button
            onClick={handleLogout}
            className={`flex items-center w-full px-3 py-2 text-sm font-medium rounded-md hover:bg-secondary transition-colors ${
              isCollapsed ? 'justify-center' : ''
            }`}
          >
            <LogOut size={20} className={isCollapsed ? '' : 'mr-3'} />
            {!isCollapsed && <span>Logout</span>}
          </button>
        </div>
      </motion.div>
    </>
  );
};

export default Sidebar;
