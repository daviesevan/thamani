import React from 'react';
import toast from 'react-hot-toast';

const SimpleToastTest = () => {
  const showBasicToast = () => {
    toast('This is a basic toast notification');
  };

  return (
    <div className="mt-8 p-4 border border-gray-200">
      <h2 className="text-lg font-serif mb-3">Basic Toast Test</h2>
      <p className="text-sm text-gray-600 mb-4">
        This tests the basic toast functionality without any custom components.
      </p>
      <button 
        onClick={showBasicToast}
        className="px-4 py-2 bg-gray-800 text-white font-serif text-sm"
      >
        Show Basic Toast
      </button>
    </div>
  );
};

export default SimpleToastTest;
