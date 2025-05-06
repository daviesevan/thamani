import React, { createContext, useContext } from 'react';
import { Toaster } from 'react-hot-toast';
import showToast from '../components/common/CustomToast';

// Create a context for toast functionality
const ToastContext = createContext(null);

// Custom hook to use the toast context
export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastContextProvider');
  }
  return context;
};

// Toast context provider component
export const ToastContextProvider = ({ children }) => {
  return (
    <ToastContext.Provider value={showToast}>
      {children}
      <Toaster
        position="top-center"
        gutter={8}
        toastOptions={{
          duration: 3000,
          style: {
            maxWidth: '420px',
            width: '100%',
            fontFamily: 'serif',
          },
        }}
        // Prevent duplicate toasts with the same message
        containerStyle={{}}
      />
    </ToastContext.Provider>
  );
};
