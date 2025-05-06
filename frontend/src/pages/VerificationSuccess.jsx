import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle } from 'lucide-react';
import { useToast } from '../context/ToastContext';
import AuthService from '../services/auth';

const VerificationSuccess = () => {
  const toast = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const [countdown, setCountdown] = useState(5);

  const [userData, setUserData] = useState(null);

  useEffect(() => {
    // Check if this is the first time we're showing the verification success page
    // to prevent duplicate toasts
    const isFirstVerification = sessionStorage.getItem('verification_shown') !== 'true';

    // Parse the hash fragment to extract the access token and other data
    const hashParams = new URLSearchParams(location.hash.substring(1));

    // Check if we have the necessary parameters
    const accessToken = hashParams.get('access_token');
    const type = hashParams.get('type');

    if (!accessToken || type !== 'signup') {
      // If not a valid verification, redirect to sign in
      toast.error('Invalid verification link');
      navigate('/signin');
      return;
    }

    // Use the auth service to handle verification
    const verificationResult = AuthService.handleVerification(hashParams);

    if (verificationResult.success) {
      // Mark that we've shown the verification page
      sessionStorage.setItem('verification_shown', 'true');

      // Only show the toast if this is the first time
      if (isFirstVerification) {
        toast.success('Email verified successfully! You can now sign in.');
      }

      // Get user data from localStorage
      const userStr = localStorage.getItem('user');
      if (userStr) {
        try {
          const user = JSON.parse(userStr);
          setUserData(user);
        } catch (e) {
          console.error('Error parsing user data:', e);
        }
      }

      // Start countdown to redirect
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            // Pass a parameter to indicate we've already shown the verification toast
            navigate('/signin?verified=true&toast_shown=true');
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(timer);
    } else {
      // If verification handling failed, redirect to sign in
      toast.error('Invalid verification link');
      navigate('/signin');
    }
  }, [location, navigate, toast]);

  return (
    <div className="min-h-screen flex flex-col justify-center items-center py-12 sm:px-6 lg:px-8 bg-background">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="sm:mx-auto sm:w-full sm:max-w-md text-center"
      >
        <CheckCircle className="mx-auto h-16 w-16 text-green-500" />
        <h1 className="mt-6 text-center text-3xl font-serif font-bold">Email Verified!</h1>
        <p className="mt-2 text-center text-lg text-muted-foreground">
          Your email has been successfully verified.
        </p>

        {userData && (
          <div className="mt-4 p-4 border border-border rounded-md bg-background/50">
            <h3 className="text-lg font-serif font-medium mb-2">Welcome, {userData.full_name || userData.email}</h3>
            <p className="text-sm text-muted-foreground">
              Your account is now active and ready to use.
            </p>
          </div>
        )}

        <p className="mt-4 text-center text-muted-foreground">
          Redirecting to sign in page in {countdown} seconds...
        </p>
        <div className="mt-6">
          <button
            onClick={() => navigate('/signin?verified=true&toast_shown=true')}
            className="w-full py-3 px-4 border border-transparent font-serif font-medium text-sm bg-primary text-white dark:text-black hover:bg-primary/90 focus:outline-none focus:ring-1 focus:ring-primary"
          >
            Sign In Now
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default VerificationSuccess;
