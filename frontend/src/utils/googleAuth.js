import AuthService from '../services/auth';
import { useToast } from '../context/ToastContext';

/**
 * Initialize Google OAuth
 * This function should be called when the Google OAuth script is loaded
 */
export const initGoogleAuth = () => {
  // Check if Google OAuth is already initialized
  if (window.google) {
    window.google.accounts.id.initialize({
      client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      callback: handleGoogleCallback,
      auto_select: false,
      cancel_on_tap_outside: true,
    });
  } else {
    console.error('Google OAuth not loaded');
  }
};

/**
 * Handle Google OAuth callback
 * @param {Object} response - Google OAuth response
 */
export const handleGoogleCallback = async (response) => {
  try {
    if (response.credential) {
      // Call the authentication service with the Google token
      await AuthService.loginWithGoogle(response.credential);
      
      // Get user data to check onboarding status
      const user = AuthService.getCurrentUser();
      
      // Show success toast through a custom event since we can't use hooks here
      window.dispatchEvent(new CustomEvent('auth-toast', { 
        detail: { type: 'success', message: 'Successfully signed in with Google!' }
      }));

      // Redirect based on onboarding status
      if (user && !user.onboarding_completed) {
        window.location.href = '/onboarding';
      } else {
        window.location.href = '/dashboard';
      }
    }
  } catch (error) {
    console.error('Google authentication error:', error);
    window.dispatchEvent(new CustomEvent('auth-toast', { 
      detail: { type: 'error', message: error.toString() || 'Failed to sign in with Google' }
    }));
  }
};

/**
 * Custom render function for Google Sign-In button
 * @param {string} elementId - DOM element ID where the button should be rendered
 * @param {string} type - Either 'signin' or 'signup'
 */
export const renderCustomGoogleButton = (elementId, type = 'signin') => {
  const container = document.getElementById(elementId);
  if (!container || !window.google) return;

  // Create custom button
  const button = document.createElement('button');
  button.className = 'w-full py-2 px-4 border border-border font-serif text-sm hover:bg-secondary transition-colors flex items-center justify-center gap-2';
  
  // Create Google icon (using SVG)
  const googleIcon = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  googleIcon.setAttribute('viewBox', '0 0 24 24');
  googleIcon.setAttribute('width', '18');
  googleIcon.setAttribute('height', '18');
  googleIcon.innerHTML = `
    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
  `;

  // Add text
  const text = document.createElement('span');
  text.textContent = type === 'signin' ? 'Google' : 'Google';

  button.appendChild(googleIcon);
  button.appendChild(text);

  // Add click handler
  button.addEventListener('click', () => {
    window.google.accounts.id.prompt();
  });

  // Clear container and append custom button
  container.innerHTML = '';
  container.appendChild(button);
};

/**
 * Load Google OAuth script
 */
export const loadGoogleScript = () => {
  // Check if script is already loaded
  if (document.getElementById('google-oauth')) {
    return;
  }
  
  const script = document.createElement('script');
  script.src = 'https://accounts.google.com/gsi/client';
  script.id = 'google-oauth';
  script.async = true;
  script.defer = true;
  script.onload = initGoogleAuth;
  document.body.appendChild(script);
};
