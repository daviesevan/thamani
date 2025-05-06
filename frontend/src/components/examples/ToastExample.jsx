import React from 'react';
import { useToast } from '../../context/ToastContext';
import toast from 'react-hot-toast';

const ToastExample = () => {
  const customToast = useToast();

  const handleContextClick = () => {
    customToast.success('This toast was triggered from context!');
  };

  const handleDirectClick = () => {
    toast.success('This toast was triggered directly!', {
      style: {
        background: '#f0fdf4',
        color: '#166534',
        border: '1px solid #166534',
        borderRadius: '0',
        padding: '12px 16px',
        fontFamily: 'serif',
      },
    });
  };

  return (
    <div className="mt-8 p-4 border border-gray-200">
      <h2 className="text-lg font-serif mb-3">Nested Component Example</h2>
      <p className="text-sm text-gray-600 mb-4">
        This demonstrates how to use toast notifications from any component in the application.
      </p>
      <div className="space-y-2">
        <button
          onClick={handleContextClick}
          className="w-full px-4 py-2 bg-gray-800 text-white font-serif text-sm"
        >
          Trigger Toast from Context
        </button>

        <button
          onClick={handleDirectClick}
          className="w-full px-4 py-2 bg-gray-600 text-white font-serif text-sm"
        >
          Trigger Toast Directly
        </button>
      </div>
    </div>
  );
};

export default ToastExample;
