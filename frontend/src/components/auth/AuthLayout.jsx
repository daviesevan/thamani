import React from 'react';
import { motion } from 'framer-motion';
import ThemeToggle from '../common/ThemeToggle';

const AuthLayout = ({ children, title, subtitle, link, linkText }) => {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <a href="/" className="text-2xl font-serif font-bold">Thamani</a>
          <ThemeToggle />
        </div>
      </header>

      {/* Main content */}
      <div className="flex-grow flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h2 className="mt-6 text-center text-2xl font-serif">{title}</h2>
            {subtitle && (
              <p className="mt-2 text-center text-sm text-muted-foreground">
                {subtitle}{' '}
                {link && (
                  <a href={link} className="font-medium text-primary hover:underline">
                    {linkText}
                  </a>
                )}
              </p>
            )}
          </motion.div>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <motion.div 
            className="bg-background py-8 px-4 border border-border sm:rounded-none sm:px-10"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            {children}
          </motion.div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border py-4">
        <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center">
          <p className="text-xs text-muted-foreground mb-2 md:mb-0">
            © {new Date().getFullYear()} Thamani. All rights reserved.
          </p>
          <div className="flex space-x-4">
            <a href="/terms" className="text-xs text-muted-foreground hover:text-primary">
              Terms of Service
            </a>
            <a href="/privacy" className="text-xs text-muted-foreground hover:text-primary">
              Privacy Policy
            </a>
            <a href="/contact" className="text-xs text-muted-foreground hover:text-primary">
              Contact
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default AuthLayout;
