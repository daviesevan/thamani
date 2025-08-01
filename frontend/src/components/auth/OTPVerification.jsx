import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import AuthService from '../../services/auth';
import { useToast } from '../../context/ToastContext';
import { Button } from '../ui/button';

const OTPVerification = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { showToast } = useToast();
  
  // Get user data from location state or localStorage
  const userData = location.state?.user || AuthService.getCurrentUser();
  
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [timeLeft, setTimeLeft] = useState(600); // 10 minutes in seconds
  const [canResend, setCanResend] = useState(false);
  
  const inputRefs = useRef([]);

  useEffect(() => {
    // Redirect if no user data
    if (!userData || !userData.user_id || !userData.email) {
      navigate('/signin');
      return;
    }

    // Redirect if email is already verified
    if (userData.email_verified) {
      navigate('/dashboard');
      return;
    }

    // Start countdown timer
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          setCanResend(true);
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [userData, navigate]);

  const handleOtpChange = (index, value) => {
    // Only allow digits
    if (!/^\d*$/.test(value)) return;

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    // Handle backspace
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    const newOtp = [...otp];
    
    for (let i = 0; i < pastedData.length && i < 6; i++) {
      newOtp[i] = pastedData[i];
    }
    
    setOtp(newOtp);
    
    // Focus the next empty input or the last input
    const nextIndex = Math.min(pastedData.length, 5);
    inputRefs.current[nextIndex]?.focus();
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    
    const otpCode = otp.join('');
    if (otpCode.length !== 6) {
      showToast('Please enter the complete 6-digit code', 'error');
      return;
    }

    setLoading(true);
    try {
      const result = await AuthService.verifyEmailOTP(
        userData.user_id,
        userData.email,
        otpCode
      );

      showToast('Email verified successfully! Please sign in to continue.', 'success');

      // Redirect to sign in page after successful verification
      navigate('/signin');
    } catch (error) {
      console.error('OTP verification error:', error);
      showToast(error || 'Verification failed. Please try again.', 'error');
      
      // Clear OTP on error
      setOtp(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    if (!canResend) return;

    setResending(true);
    try {
      await AuthService.resendVerificationOTP(userData.email);
      showToast('New verification code sent!', 'success');
      
      // Reset timer
      setTimeLeft(600);
      setCanResend(false);
      
      // Clear current OTP
      setOtp(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
    } catch (error) {
      console.error('Resend error:', error);
      showToast(error || 'Failed to resend code. Please try again.', 'error');
    } finally {
      setResending(false);
    }
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (!userData) {
    return null; // Will redirect in useEffect
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
            Verify Your Email
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            We've sent a 6-digit verification code to
          </p>
          <p className="font-medium text-blue-600 dark:text-blue-400">
            {userData.email}
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleVerify}>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Enter verification code
            </label>
            <div className="flex justify-center space-x-2">
              {otp.map((digit, index) => (
                <input
                  key={index}
                  ref={(el) => (inputRefs.current[index] = el)}
                  type="text"
                  maxLength="1"
                  value={digit}
                  onChange={(e) => handleOtpChange(index, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(index, e)}
                  onPaste={handlePaste}
                  className="w-12 h-12 text-center text-xl font-bold border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
                  disabled={loading}
                />
              ))}
            </div>
          </div>

          <div>
            <Button
              type="submit"
              className="w-full"
              disabled={loading || otp.join('').length !== 6}
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  Verifying...
                </div>
              ) : (
                'Verify Email'
              )}
            </Button>
          </div>

          <div className="text-center">
            {timeLeft > 0 ? (
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Code expires in {formatTime(timeLeft)}
              </p>
            ) : (
              <p className="text-sm text-red-600 dark:text-red-400">
                Code has expired
              </p>
            )}
            
            <div className="mt-2">
              {canResend ? (
                <button
                  type="button"
                  onClick={handleResend}
                  disabled={resending}
                  className="text-blue-600 dark:text-blue-400 hover:text-blue-500 text-sm font-medium disabled:opacity-50"
                >
                  {resending ? 'Sending...' : 'Send new code'}
                </button>
              ) : (
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  Resend available in {formatTime(timeLeft)}
                </span>
              )}
            </div>
          </div>

          <div className="text-center">
            <button
              type="button"
              onClick={() => navigate('/signin')}
              className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-500"
            >
              Back to Sign In
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default OTPVerification;
