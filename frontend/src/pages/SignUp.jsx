import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Eye, EyeOff, CheckCircle, XCircle } from 'lucide-react';
import FormInput from '../components/auth/FormInput';
import { useToast } from '../context/ToastContext';
import AuthService from '../services/auth';
import { loadGoogleScript, renderCustomGoogleButton } from '../utils/googleAuth';

const SignUp = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const googleButtonRef = useRef(null);
  const [formData, setFormData] = useState({
    email: '',
    fullName: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [step, setStep] = useState(1);
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
    // Load Google OAuth script and render custom button when on step 1
    if (step === 1) {
      loadGoogleScript();
      const timerId = setTimeout(() => {
        renderCustomGoogleButton('google-signup-button', 'signup');
      }, 1000);

      return () => clearTimeout(timerId);
    }
  }, [step]);

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

  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };

  const validateStep1 = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.fullName) {
      newErrors.fullName = 'Full name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = () => {
    const newErrors = {};

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNextStep = () => {
    if (validateStep1()) {
      setStep(2);
    }
  };

  const handlePrevStep = () => {
    setStep(1);
  };

  const [signupSuccess, setSignupSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateStep2()) {
      return;
    }

    setIsLoading(true);

    try {
      // Call the authentication service to register
      const result = await AuthService.signup({
        email: formData.email,
        password: formData.password,
        fullName: formData.fullName
      });

      // Show success message
      toast.success('Account created successfully! Please check your email for verification code.');

      // Redirect to OTP verification with user data
      navigate('/verify-email', {
        state: {
          user: result.user || {
            user_id: result.user_id,
            email: formData.email,
            full_name: formData.fullName,
            email_verified: false
          }
        }
      });
    } catch (error) {
      console.error('Registration error:', error);
      toast.error(error.toString() || 'Failed to create account. Please try again.');
      setIsLoading(false);
    }
  };

  // Password strength indicators
  const passwordStrength = {
    length: formData.password.length >= 8,
    uppercase: /[A-Z]/.test(formData.password),
    lowercase: /[a-z]/.test(formData.password),
    number: /[0-9]/.test(formData.password),
    special: /[^A-Za-z0-9]/.test(formData.password),
  };

  const passwordStrengthScore = Object.values(passwordStrength).filter(Boolean).length;

  const getPasswordStrengthText = () => {
    if (passwordStrengthScore === 0) return '';
    if (passwordStrengthScore <= 2) return 'Weak';
    if (passwordStrengthScore <= 4) return 'Medium';
    return 'Strong';
  };

  const getPasswordStrengthColor = () => {
    if (passwordStrengthScore === 0) return '';
    if (passwordStrengthScore <= 2) return 'text-error';
    if (passwordStrengthScore <= 4) return 'text-warning';
    return 'text-success';
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
          {!signupSuccess ? (
            <>
              <h2 className="mt-6 text-center text-2xl font-serif">Create your account</h2>
              <p className="mt-2 text-center text-sm text-muted-foreground">
                Already have an account?{' '}
                <a href="/signin" className="font-medium text-primary hover:underline">
                  Sign in
                </a>
              </p>
            </>
          ) : (
            <h2 className="mt-6 text-center text-2xl font-serif">Verify your email</h2>
          )}
        </motion.div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        {!signupSuccess ? (
          <motion.div
            className="bg-background py-8 px-4 border border-border sm:rounded-none sm:px-10"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            {/* Step indicator */}
            <div className="mb-8">
              <div className="flex items-center justify-between">
                <div className="flex flex-col items-center">
                  <div className={`w-8 h-8 flex items-center justify-center rounded-full border ${
                    step >= 1 ? 'bg-primary text-white dark:text-black' : 'border-border'
                  }`}>
                    1
                  </div>
                  <span className="mt-1 text-xs font-serif">Account</span>
                </div>
                <div className="flex-1 h-px bg-border mx-2"></div>
                <div className="flex flex-col items-center">
                  <div className={`w-8 h-8 flex items-center justify-center rounded-full border ${
                    step >= 2 ? 'bg-primary text-white dark:text-black' : 'border-border'
                  }`}>
                    2
                  </div>
                  <span className="mt-1 text-xs font-serif">Password</span>
                </div>
              </div>
            </div>

            <form onSubmit={handleSubmit}>
              {step === 1 && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
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

                  <FormInput
                    label="Full name"
                    type="text"
                    id="fullName"
                    name="fullName"
                    value={formData.fullName}
                    onChange={handleChange}
                    autoComplete="name"
                    required
                    error={errors.fullName}
                  />

                  <div className="mt-6">
                    <button
                      type="button"
                      onClick={handleNextStep}
                      className="w-full py-3 px-4 border border-transparent font-serif font-medium text-sm bg-primary text-white dark:text-black hover:bg-primary/90 focus:outline-none focus:ring-1 focus:ring-primary"
                    >
                      Continue
                    </button>
                  </div>
                </motion.div>
              )}

              {step === 2 && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="relative">
                    <FormInput
                      label="Password"
                      type={showPassword ? 'text' : 'password'}
                      id="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      autoComplete="new-password"
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

                  {formData.password && (
                    <div className="mt-2 mb-4">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-xs font-serif">Password strength:</span>
                        <span className={`text-xs font-serif font-medium ${getPasswordStrengthColor()}`}>
                          {getPasswordStrengthText()}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="flex items-center">
                          {passwordStrength.length ? (
                            <CheckCircle size={12} className="text-success mr-1" />
                          ) : (
                            <XCircle size={12} className="text-muted-foreground mr-1" />
                          )}
                          <span>At least 8 characters</span>
                        </div>
                        <div className="flex items-center">
                          {passwordStrength.uppercase ? (
                            <CheckCircle size={12} className="text-success mr-1" />
                          ) : (
                            <XCircle size={12} className="text-muted-foreground mr-1" />
                          )}
                          <span>Uppercase letter</span>
                        </div>
                        <div className="flex items-center">
                          {passwordStrength.lowercase ? (
                            <CheckCircle size={12} className="text-success mr-1" />
                          ) : (
                            <XCircle size={12} className="text-muted-foreground mr-1" />
                          )}
                          <span>Lowercase letter</span>
                        </div>
                        <div className="flex items-center">
                          {passwordStrength.number ? (
                            <CheckCircle size={12} className="text-success mr-1" />
                          ) : (
                            <XCircle size={12} className="text-muted-foreground mr-1" />
                          )}
                          <span>Number</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="relative">
                    <FormInput
                      label="Confirm password"
                      type={showConfirmPassword ? 'text' : 'password'}
                      id="confirmPassword"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      autoComplete="new-password"
                      required
                      error={errors.confirmPassword}
                    />
                    <button
                      type="button"
                      className="absolute right-3 top-9 text-muted-foreground"
                      onClick={toggleConfirmPasswordVisibility}
                    >
                      {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>

                  <div className="flex items-center mt-4">
                    <input
                      id="terms"
                      name="terms"
                      type="checkbox"
                      className="h-4 w-4 border-border"
                      required
                    />
                    <label htmlFor="terms" className="ml-2 block text-sm font-serif">
                      I agree to the{' '}
                      <a href="/terms" className="text-primary hover:underline">
                        Terms of Service
                      </a>{' '}
                      and{' '}
                      <a href="/privacy" className="text-primary hover:underline">
                        Privacy Policy
                      </a>
                    </label>
                  </div>

                  <div className="mt-6 flex space-x-3">
                    <button
                      type="button"
                      onClick={handlePrevStep}
                      className="flex-1 py-3 px-4 border border-border font-serif font-medium text-sm bg-background hover:bg-secondary focus:outline-none focus:ring-1 focus:ring-primary"
                    >
                      Back
                    </button>
                    <button
                      type="submit"
                      disabled={isLoading}
                      className={`flex-1 py-3 px-4 border border-transparent font-serif font-medium text-sm bg-primary text-white dark:text-black hover:bg-primary/90 focus:outline-none focus:ring-1 focus:ring-primary ${
                        isLoading ? 'opacity-70 cursor-not-allowed' : ''
                      }`}
                    >
                      {isLoading ? 'Creating account...' : 'Create account'}
                    </button>
                  </div>
                </motion.div>
              )}
            </form>

            {step === 1 && (
              <div className="mt-6">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-border"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-background text-muted-foreground font-serif">
                      Or sign up with
                    </span>
                  </div>
                </div>

                <div className="mt-6 grid grid-cols-2 gap-3">
                  <div
                    id="google-signup-button"
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
            )}
          </motion.div>
        ) : (
          <motion.div
            className="bg-background py-8 px-4 border border-border sm:rounded-none sm:px-10"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="text-center">
              <div className="flex justify-center mb-4">
                <CheckCircle className="h-16 w-16 text-green-500" />
              </div>
              <h3 className="text-xl font-serif font-medium mb-2">Check your email</h3>
              <p className="text-muted-foreground mb-6">
                We've sent a verification link to <strong>{formData.email}</strong>
              </p>
              <p className="text-sm text-muted-foreground mb-6">
                Please check your email and click the verification link to activate your account.
                If you don't see the email, check your spam folder.
              </p>
              <div className="mt-6">
                <a
                  href="/signin"
                  className="w-full inline-block py-3 px-4 border border-transparent font-serif font-medium text-sm bg-primary text-white dark:text-black hover:bg-primary/90 focus:outline-none focus:ring-1 focus:ring-primary text-center"
                >
                  Go to Sign In
                </a>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default SignUp;
