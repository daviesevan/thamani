import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
import FormInput from '../components/auth/FormInput';
import AuthLayout from '../components/auth/AuthLayout';
import { ButtonLoader } from '../components/common/Loader';
import { useToast } from '../context/ToastContext';
import AuthService from '../services/auth';
import { loadGoogleScript, renderCustomGoogleButton } from '../utils/googleAuth';

const SignIn = () => {
  const toast = useToast();
  const location = useLocation();
  const googleButtonRef = useRef(null);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showFacebookTooltip, setShowFacebookTooltip] = useState(false);

  // Listen for auth toasts from Google callback
  useEffect(() => {
    const handleAuthToast = (event) => {
      const { type, message } = event.detail;
      if (type === 'success') {
        toast.success(message);
      } else if (type === 'error') {
        toast.error(message);
      }
    };

    window.addEventListener('auth-toast', handleAuthToast);
    return () => window.removeEventListener('auth-toast', handleAuthToast);
  }, [toast]);

  useEffect(() => {
    // Check if user is coming from verification
    const searchParams = new URLSearchParams(location.search);
    const verified = searchParams.get('verified');
    const toastShown = searchParams.get('toast_shown');

    if (verified === 'true') {
      // Get user data from localStorage to pre-fill email
      const userStr = localStorage.getItem('user');
      if (userStr) {
        try {
          const user = JSON.parse(userStr);
          if (user && user.email) {
            setFormData(prev => ({
              ...prev,
              email: user.email
            }));
          }
        } catch (e) {
          console.error('Error parsing user data:', e);
        }
      }

      // Only show the toast if it hasn't been shown already
      if (toastShown !== 'true' && sessionStorage.getItem('verification_shown') !== 'true') {
        toast.success('Email verified successfully! You can now sign in with your credentials.');
        // Mark that we've shown the toast
        sessionStorage.setItem('verification_shown', 'true');
      }
    }

    // Load Google OAuth script and render custom button
    loadGoogleScript();
    const timerId = setTimeout(() => {
      renderCustomGoogleButton('google-signin-button', 'signin');
    }, 1000); // Small delay to ensure Google script is loaded

    return () => clearTimeout(timerId);
  }, [location, toast]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    // Clear error when user types
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: '',
      });
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Call the authentication service to login
      await AuthService.login({
        email: formData.email,
        password: formData.password
      });

      toast.success('Successfully signed in!');

      // Check if user has completed onboarding
      const user = AuthService.getCurrentUser();
      if (user && !user.onboarding_completed) {
        // Redirect to onboarding if not completed
        window.location.href = '/onboarding';
      } else {
        // Redirect to dashboard if onboarding is completed
        window.location.href = '/dashboard';
      }
    } catch (error) {
      console.error('Login error:', error);
      toast.error(error.toString() || 'Invalid email or password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Sign in to your account"
      subtitle="Or"
      link="/signup"
      linkText="create a new account"
    >
      <form className="space-y-6" onSubmit={handleSubmit}>
        <FormInput
          label="Email address"
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          autoComplete="email"
          required
          error={errors.email}
        />

        <div className="relative">
          <FormInput
            label="Password"
            type={showPassword ? 'text' : 'password'}
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            autoComplete="current-password"
            required
            error={errors.password}
          />
          <button
            type="button"
            className="absolute right-3 top-9 text-muted-foreground"
            onClick={togglePasswordVisibility}
          >
            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <input
              id="remember-me"
              name="remember-me"
              type="checkbox"
              className="h-4 w-4 border-border"
            />
            <label htmlFor="remember-me" className="ml-2 block text-sm font-serif">
              Remember me
            </label>
          </div>

          <div className="text-sm">
            <a href="/forgot-password" className="font-serif text-primary hover:underline">
              Forgot your password?
            </a>
          </div>
        </div>

        <div>
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full py-3 px-4 border border-transparent font-serif font-medium text-sm bg-primary text-white dark:text-black hover:bg-primary/90 focus:outline-none focus:ring-1 focus:ring-primary flex items-center justify-center ${
              isLoading ? 'opacity-70 cursor-not-allowed' : ''
            }`}
          >
            {isLoading && (
              <span className="mr-2">
                <ButtonLoader />
              </span>
            )}
            {isLoading ? 'Signing in...' : 'Sign in'}
          </button>
        </div>
      </form>

      <div className="mt-6">
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-border"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-background text-muted-foreground font-serif">
              Or continue with
            </span>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-3">
          <div
            id="google-signin-button"
            ref={googleButtonRef}
            className="w-full flex justify-center"
          />
          <div className="relative">
            <button
              type="button"
              className="w-full py-2 px-4 border border-border font-serif text-sm hover:bg-secondary transition-colors flex items-center justify-center gap-2 opacity-50 cursor-not-allowed"
              onMouseEnter={() => setShowFacebookTooltip(true)}
              onMouseLeave={() => setShowFacebookTooltip(false)}
              disabled
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="#1877F2">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              Facebook
            </button>
            {showFacebookTooltip && (
              <div className="absolute -top-10 left-1/2 transform -translate-x-1/2 px-2 py-1 bg-black/90 dark:bg-white/90 text-white dark:text-black text-xs rounded whitespace-nowrap">
                Coming soon
              </div>
            )}
          </div>
        </div>
      </div>
    </AuthLayout>
  );
};

export default SignIn;
