import React from 'react';
import { AlertCircle } from 'lucide-react';

const FormInput = ({
  label,
  type = 'text',
  id,
  name,
  value,
  onChange,
  placeholder,
  error,
  required = false,
  autoComplete,
  className = '',
}) => {
  return (
    <div className={`mb-4 ${className}`}>
      {label && (
        <label 
          htmlFor={id} 
          className="block font-serif text-sm mb-2"
        >
          {label}
          {required && <span className="text-error ml-1">*</span>}
        </label>
      )}
      <input
        type={type}
        id={id}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        autoComplete={autoComplete}
        className={`w-full p-3 font-serif text-sm border ${
          error ? 'border-error' : 'border-border'
        } bg-background focus:outline-none focus:ring-1 focus:ring-primary`}
      />
      {error && (
        <div className="flex items-center mt-1 text-error text-xs">
          <AlertCircle size={12} className="mr-1" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};

export default FormInput;
