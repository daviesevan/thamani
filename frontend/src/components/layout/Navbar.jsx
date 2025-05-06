import React, { useState, useEffect } from 'react';
import { Menu, X, LogOut } from 'lucide-react';
import ThemeToggle from '../common/ThemeToggle';
import { motion } from 'framer-motion';
import AuthService from '../../services/auth';
import { useToast } from '../../context/ToastContext';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const toast = useToast();

  // Check authentication status
  useEffect(() => {
    setIsAuthenticated(AuthService.isAuthenticated());
  }, []);

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      const offset = window.scrollY;
      if (offset > 50) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (token) {
        await AuthService.logout(token);
      }
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      toast.success('Successfully logged out');
      window.location.href = '/signin';
    } catch (error) {
      console.error('Logout error:', error);
      toast.error('Failed to log out. Please try again.');
    }
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? 'bg-background/95 backdrop-blur-sm shadow-sm' : 'bg-background'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16 border-b border-border">
          {/* Logo */}
          <div className="flex-shrink-0">
            <a href="/" className="font-serif font-bold text-2xl tracking-tight">
              Thamani
            </a>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#how-it-works" className="font-serif text-sm hover:text-primary transition-colors">
              How It Works
            </a>
            <a href="#supported-shops" className="font-serif text-sm hover:text-primary transition-colors">
              Supported Shops
            </a>
            <a href="#features" className="font-serif text-sm hover:text-primary transition-colors">
              Features
            </a>
            <a href="#testimonials" className="font-serif text-sm hover:text-primary transition-colors">
              Testimonials
            </a>
          </nav>

          {/* Desktop Auth & Theme */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <a href="/dashboard" className="font-serif text-sm hover:text-primary transition-colors">
                  Dashboard
                </a>
                <button
                  onClick={handleLogout}
                  className="font-serif text-sm px-4 py-2 border border-primary bg-black dark:bg-white text-white dark:text-black hover:bg-black/90 dark:hover:bg-white/90 transition-colors flex items-center"
                >
                  <LogOut size={16} className="mr-2" />
                  Logout
                </button>
              </>
            ) : (
              <>
                <a href="/signin" className="font-serif text-sm hover:text-primary transition-colors">
                  Sign In
                </a>
                <a
                  href="/signup"
                  className="font-serif text-sm px-4 py-2 border border-primary bg-black dark:bg-white text-white dark:text-black hover:bg-black/90 dark:hover:bg-white/90 transition-colors"
                >
                  Sign Up
                </a>
              </>
            )}
            <ThemeToggle />
          </div>

          {/* Mobile Menu Button */}
          <div className="flex items-center md:hidden space-x-4">
            <ThemeToggle />
            <button
              onClick={toggleMenu}
              className="p-2 rounded-none text-foreground hover:text-primary transition-colors"
              aria-expanded={isMenuOpen}
              aria-label="Toggle menu"
            >
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <motion.div
        className={`md:hidden overflow-hidden ${isMenuOpen ? 'block' : 'hidden'}`}
        initial={{ height: 0, opacity: 0 }}
        animate={{
          height: isMenuOpen ? 'auto' : 0,
          opacity: isMenuOpen ? 1 : 0
        }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
      >
        <div className="px-4 pt-2 pb-6 space-y-4 bg-background border-b border-border">
          <nav className="flex flex-col space-y-4 mb-6">
            <a
              href="#how-it-works"
              className="font-serif text-base py-2 border-b border-border"
              onClick={() => setIsMenuOpen(false)}
            >
              How It Works
            </a>
            <a
              href="#supported-shops"
              className="font-serif text-base py-2 border-b border-border"
              onClick={() => setIsMenuOpen(false)}
            >
              Supported Shops
            </a>
            <a
              href="#features"
              className="font-serif text-base py-2 border-b border-border"
              onClick={() => setIsMenuOpen(false)}
            >
              Features
            </a>
            <a
              href="#testimonials"
              className="font-serif text-base py-2 border-b border-border"
              onClick={() => setIsMenuOpen(false)}
            >
              Testimonials
            </a>
          </nav>
          <div className="flex flex-col space-y-3">
            {isAuthenticated ? (
              <>
                <a
                  href="/dashboard"
                  className="font-serif text-center text-sm py-2 border border-border hover:bg-secondary transition-colors"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Dashboard
                </a>
                <button
                  onClick={() => {
                    setIsMenuOpen(false);
                    handleLogout();
                  }}
                  className="font-serif text-center text-sm py-2 bg-black dark:bg-white text-white dark:text-black hover:bg-black/90 dark:hover:bg-white/90 transition-colors flex items-center justify-center"
                >
                  <LogOut size={16} className="mr-2" />
                  Logout
                </button>
              </>
            ) : (
              <>
                <a
                  href="/signin"
                  className="font-serif text-center text-sm py-2 border border-border hover:bg-secondary transition-colors"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Sign In
                </a>
                <a
                  href="/signup"
                  className="font-serif text-center text-sm py-2 bg-black dark:bg-white text-white dark:text-black hover:bg-black/90 dark:hover:bg-white/90 transition-colors"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Sign Up
                </a>
              </>
            )}
          </div>
        </div>
      </motion.div>
    </header>
  );
};

export default Navbar;
