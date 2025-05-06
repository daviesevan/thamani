import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import FormInput from '../components/auth/FormInput';
import { useToast } from '../context/ToastContext';
import AuthService from '../services/auth';

const ForgotPassword = () => {
  const toast = useToast();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleChange = (e) => {
    setEmail(e.target.value);
    setError('');
  };

  const validateForm = () => {
    if (!email) {
      setError('Email is required');
      return false;
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      setError('Email is invalid');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Call the authentication service to request password reset
      await AuthService.forgotPassword(email);

      setIsSubmitted(true);
      toast.success('Password reset instructions sent to your email.');
    } catch (error) {
      console.error('Password reset error:', error);
      toast.error(error.toString() || 'Failed to send password reset email. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8 bg-background">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-center text-3xl font-serif font-bold">Thamani</h1>
          <h2 className="mt-6 text-center text-2xl font-serif">Reset your password</h2>
          <p className="mt-2 text-center text-sm text-muted-foreground">
            Enter your email address and we'll send you instructions to reset your password.
          </p>
        </motion.div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <motion.div
          className="bg-background py-8 px-4 border border-border sm:rounded-none sm:px-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          {!isSubmitted ? (
            <form className="space-y-6" onSubmit={handleSubmit}>
              <FormInput
                label="Email address"
                type="email"
                id="email"
                name="email"
                value={email}
                onChange={handleChange}
                autoComplete="email"
                required
                error={error}
              />

              <div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className={`w-full py-3 px-4 border border-transparent font-serif font-medium text-sm bg-primary text-white dark:text-black hover:bg-primary/90 focus:outline-none focus:ring-1 focus:ring-primary ${
                    isLoading ? 'opacity-70 cursor-not-allowed' : ''
                  }`}
                >
                  {isLoading ? 'Sending...' : 'Send reset instructions'}
                </button>
              </div>
            </form>
          ) : (
            <div className="text-center">
              <div className="mb-4 text-success">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-serif font-medium mb-2">Check your email</h3>
              <p className="text-sm text-muted-foreground mb-6">
                We've sent password reset instructions to <strong>{email}</strong>
              </p>
              <p className="text-xs text-muted-foreground mb-6">
                If you don't see the email, check your spam folder or try another email address.
              </p>
              <button
                type="button"
                onClick={() => setIsSubmitted(false)}
                className="text-sm font-serif text-primary hover:underline"
              >
                Try another email
              </button>
            </div>
          )}

          <div className="mt-6">
            <a
              href="/signin"
              className="flex items-center justify-center font-serif text-sm text-primary hover:underline"
            >
              <ArrowLeft size={16} className="mr-1" />
              Back to sign in
            </a>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ForgotPassword;
