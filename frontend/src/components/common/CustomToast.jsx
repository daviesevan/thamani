import React from 'react';
import { toast, Toaster } from 'react-hot-toast';
import { X, AlertCircle, CheckCircle, Info } from 'lucide-react';

// Simplified version of the cn utility
const cn = (...classes) => classes.filter(Boolean).join(' ');

// Custom Toast Component
export const CustomToast = ({ message, type, onDismiss }) => {
  // Define icon based on toast type
  const Icon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle size={16} className="text-green-800" />;
      case 'error':
        return <AlertCircle size={16} className="text-red-800" />;
      case 'warning':
        return <AlertCircle size={16} className="text-amber-800" />;
      default:
        return <Info size={16} className="text-gray-800" />;
    }
  };

  // Define styling based on toast type
  const getToastStyles = () => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-t border-green-800';
      case 'error':
        return 'bg-red-50 border-t border-red-800';
      case 'warning':
        return 'bg-amber-50 border-t border-amber-800';
      default:
        return 'bg-gray-50 border-t border-gray-800';
    }
  };

  return (
    <div
      className={cn(
        'flex items-center justify-between py-2 px-3 shadow-sm',
        getToastStyles()
      )}
    >
      <div className="flex items-center gap-2">
        <Icon />
        <p className="text-sm font-serif text-gray-900">{message}</p>
      </div>
      <button
        onClick={onDismiss}
        className="ml-4 p-1 hover:bg-gray-200/50 rounded-full transition-colors"
        aria-label="Dismiss notification"
      >
        <X size={12} className="text-gray-600" />
      </button>
    </div>
  );
};

// Custom Toast Provider
export const ToastProvider = () => {
  return (
    <Toaster
      position="top-center"
      gutter={8}
      toastOptions={{
        duration: 3000,
        style: {
          background: 'transparent',
          boxShadow: 'none',
          padding: 0,
          maxWidth: '420px',
          width: '100%',
        },
      }}
    />
  );
};

// Keep track of active toasts to prevent duplicates
const activeToasts = new Set();

// Toast utility functions
export const showToast = {
  success: (message) => {
    // Check if this exact message is already being shown
    if (activeToasts.has(message)) {
      return null;
    }

    // Add message to active toasts
    activeToasts.add(message);

    return toast.success(message, {
      duration: 3000,
      style: {
        background: '#f0fdf4',
        color: '#166534',
        border: '1px solid #166534',
        borderRadius: '0',
        padding: '12px 16px',
      },
      icon: <CheckCircle size={16} />,
      onClose: () => {
        // Remove message from active toasts when it's closed
        activeToasts.delete(message);
      }
    });
  },
  error: (message) => {
    // Check if this exact message is already being shown
    if (activeToasts.has(message)) {
      return null;
    }

    // Add message to active toasts
    activeToasts.add(message);

    return toast.error(message, {
      duration: 4000,
      style: {
        background: '#fef2f2',
        color: '#991b1b',
        border: '1px solid #991b1b',
        borderRadius: '0',
        padding: '12px 16px',
      },
      icon: <AlertCircle size={16} />,
      onClose: () => {
        // Remove message from active toasts when it's closed
        activeToasts.delete(message);
      }
    });
  },
  warning: (message) => {
    // Check if this exact message is already being shown
    if (activeToasts.has(message)) {
      return null;
    }

    // Add message to active toasts
    activeToasts.add(message);

    return toast(message, {
      duration: 3500,
      icon: <AlertCircle size={16} className="text-amber-800" />,
      style: {
        background: '#fffbeb',
        color: '#92400e',
        border: '1px solid #92400e',
        borderRadius: '0',
        padding: '12px 16px',
      },
      onClose: () => {
        // Remove message from active toasts when it's closed
        activeToasts.delete(message);
      }
    });
  },
  info: (message) => {
    // Check if this exact message is already being shown
    if (activeToasts.has(message)) {
      return null;
    }

    // Add message to active toasts
    activeToasts.add(message);

    return toast(message, {
      duration: 3000,
      icon: <Info size={16} className="text-gray-800" />,
      style: {
        background: '#f9fafb',
        color: '#1f2937',
        border: '1px solid #1f2937',
        borderRadius: '0',
        padding: '12px 16px',
      },
      onClose: () => {
        // Remove message from active toasts when it's closed
        activeToasts.delete(message);
      }
    });
  }
};

export default showToast;
