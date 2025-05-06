import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, Search, Bell, TrendingDown } from 'lucide-react';
import { useToast } from '../context/ToastContext';
import retailers from '../data/retailers';
import AuthService from '../services/auth';

const Onboarding = () => {
  const toast = useToast();
  const [step, setStep] = useState(1);
  const [selectedRetailers, setSelectedRetailers] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Check if user is authenticated and has already completed onboarding
  useEffect(() => {
    if (!AuthService.isAuthenticated()) {
      // Redirect to sign in if not authenticated
      window.location.href = '/signin';
      return;
    }

    // If user has already completed onboarding, redirect to dashboard
    if (AuthService.hasCompletedOnboarding()) {
      window.location.href = '/dashboard';
    }
  }, []);

  // Get all unique categories
  const allCategories = (() => {
    const categoriesSet = new Set();
    retailers.forEach(retailer => {
      retailer.categories.forEach(category => {
        categoriesSet.add(category);
      });
    });
    return Array.from(categoriesSet).sort();
  })();

  const handleRetailerToggle = (retailerId) => {
    if (selectedRetailers.includes(retailerId)) {
      setSelectedRetailers(selectedRetailers.filter(id => id !== retailerId));
    } else {
      setSelectedRetailers([...selectedRetailers, retailerId]);
    }
  };

  const handleCategoryToggle = (category) => {
    if (selectedCategories.includes(category)) {
      setSelectedCategories(selectedCategories.filter(c => c !== category));
    } else {
      setSelectedCategories([...selectedCategories, category]);
    }
  };

  const handleNextStep = () => {
    if (step < 3) {
      setStep(step + 1);
    } else {
      handleFinish();
    }
  };

  const handlePrevStep = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleSkip = () => {
    if (step < 3) {
      setStep(step + 1);
    } else {
      handleFinish();
    }
  };

  const handleFinish = async () => {
    setIsLoading(true);

    try {
      // Save selected retailers and categories
      // This would be an API call to save user preferences
      // For now, we'll just simulate a successful save
      await new Promise(resolve => setTimeout(resolve, 500));

      try {
        // Try to mark onboarding as completed in the backend
        await AuthService.completeOnboarding();
        toast.success('Preferences saved successfully!');
      } catch (onboardingError) {
        // If backend update fails, we'll still proceed but show a warning
        console.warn('Onboarding completion warning:', onboardingError);
        toast.warning('Preferences saved with limited functionality. Some features may not be available.');
      }

      // Redirect to dashboard regardless of backend success
      // The completeOnboarding method will handle local storage updates
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Onboarding error:', error);
      toast.error('Failed to save preferences. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-serif font-bold">Thamani</h1>
          <button
            onClick={handleSkip}
            className="text-sm font-serif underline"
          >
            Skip
          </button>
        </div>
      </header>

      {/* Progress bar */}
      <div className="max-w-4xl mx-auto px-4 pt-8">
        <div className="flex items-center justify-between mb-8">
          <div className="flex flex-col items-center">
            <div className={`w-10 h-10 flex items-center justify-center rounded-full border ${
              step >= 1 ? 'bg-primary text-white dark:text-black' : 'border-border'
            }`}>
              {step > 1 ? <Check size={18} /> : 1}
            </div>
            <span className="mt-1 text-sm font-serif">Welcome</span>
          </div>
          <div className="flex-1 h-px bg-border mx-4"></div>
          <div className="flex flex-col items-center">
            <div className={`w-10 h-10 flex items-center justify-center rounded-full border ${
              step >= 2 ? 'bg-primary text-white dark:text-black' : 'border-border'
            }`}>
              {step > 2 ? <Check size={18} /> : 2}
            </div>
            <span className="mt-1 text-sm font-serif">Retailers</span>
          </div>
          <div className="flex-1 h-px bg-border mx-4"></div>
          <div className="flex flex-col items-center">
            <div className={`w-10 h-10 flex items-center justify-center rounded-full border ${
              step >= 3 ? 'bg-primary text-white dark:text-black' : 'border-border'
            }`}>
              3
            </div>
            <span className="mt-1 text-sm font-serif">Categories</span>
          </div>
        </div>
      </div>

      {/* Step content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {step === 1 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="text-center"
          >
            <h2 className="text-3xl font-serif font-bold mb-4">Welcome to Thamani</h2>
            <p className="text-muted-foreground mb-10 max-w-2xl mx-auto text-lg">
              Let's set up your account to help you track prices and save money on your online purchases.
            </p>

            <div className="grid md:grid-cols-3 gap-10 mb-12">
              <div className="flex flex-col items-center text-center p-6">
                <div className="w-16 h-16 flex items-center justify-center mb-6 text-primary">
                  <Search size={32} />
                </div>
                <h3 className="text-xl font-serif font-bold mb-3">Track Products</h3>
                <p className="text-muted-foreground font-serif">Add products you're interested in by pasting links or searching</p>
              </div>

              <div className="flex flex-col items-center text-center p-6">
                <div className="w-16 h-16 flex items-center justify-center mb-6 text-primary">
                  <Bell size={32} />
                </div>
                <h3 className="text-xl font-serif font-bold mb-3">Get Alerts</h3>
                <p className="text-muted-foreground font-serif">Set your target price and get notified when prices drop</p>
              </div>

              <div className="flex flex-col items-center text-center p-6">
                <div className="w-16 h-16 flex items-center justify-center mb-6 text-primary">
                  <TrendingDown size={32} />
                </div>
                <h3 className="text-xl font-serif font-bold mb-3">Save Money</h3>
                <p className="text-muted-foreground font-serif">Save money by buying at the right time</p>
              </div>
            </div>

            <button
              onClick={handleNextStep}
              className="w-full md:w-auto py-3 px-10 border border-transparent font-serif font-medium text-base bg-primary text-white dark:text-black hover:bg-primary/90 focus:outline-none focus:ring-1 focus:ring-primary"
            >
              Get Started
            </button>
          </motion.div>
        )}

        {step === 2 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h2 className="text-3xl font-serif font-bold mb-4">Select your favorite retailers</h2>
            <p className="text-muted-foreground mb-10 max-w-2xl mx-auto text-lg">
              Choose the online shops you frequently use. We'll track prices across these retailers.
            </p>

            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-5 mb-12">
              {retailers.map(retailer => (
                <div
                  key={retailer.id}
                  onClick={() => handleRetailerToggle(retailer.id)}
                  className={`p-5 border cursor-pointer transition-colors ${
                    selectedRetailers.includes(retailer.id)
                      ? 'border-primary bg-secondary'
                      : 'border-border hover:bg-secondary/50'
                  }`}
                >
                  <div className="flex items-center justify-center h-14 mb-3">
                    {/* This would be an actual logo in production */}
                    <div className="w-10 h-10 flex items-center justify-center text-primary text-lg">
                      {retailer.name.charAt(0)}
                    </div>
                  </div>
                  <p className="text-center font-serif">{retailer.name}</p>
                </div>
              ))}
            </div>

            <div className="flex justify-between">
              <button
                onClick={handlePrevStep}
                className="py-3 px-8 border border-border font-serif font-medium text-base bg-background hover:bg-secondary focus:outline-none focus:ring-1 focus:ring-primary"
              >
                Back
              </button>
              <button
                onClick={handleNextStep}
                className="py-3 px-8 border border-transparent font-serif font-medium text-base bg-primary text-white dark:text-black hover:bg-primary/90 focus:outline-none focus:ring-1 focus:ring-primary"
              >
                Continue
              </button>
            </div>
          </motion.div>
        )}

        {step === 3 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h2 className="text-3xl font-serif font-bold mb-4">What are you interested in?</h2>
            <p className="text-muted-foreground mb-10 max-w-2xl mx-auto text-lg">
              Select categories you're interested in. We'll personalize your experience based on your preferences.
            </p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-5 mb-12">
              {allCategories.map(category => (
                <div
                  key={category}
                  onClick={() => handleCategoryToggle(category)}
                  className={`p-5 border cursor-pointer transition-colors ${
                    selectedCategories.includes(category)
                      ? 'border-primary bg-secondary'
                      : 'border-border hover:bg-secondary/50'
                  }`}
                >
                  <p className="text-center font-serif py-2">{category}</p>
                </div>
              ))}
            </div>

            <div className="flex justify-between">
              <button
                onClick={handlePrevStep}
                className="py-3 px-8 border border-border font-serif font-medium text-base bg-background hover:bg-secondary focus:outline-none focus:ring-1 focus:ring-primary"
              >
                Back
              </button>
              <button
                onClick={handleFinish}
                disabled={isLoading}
                className={`py-3 px-8 border border-transparent font-serif font-medium text-base bg-primary text-white dark:text-black hover:bg-primary/90 focus:outline-none focus:ring-1 focus:ring-primary ${
                  isLoading ? 'opacity-70 cursor-not-allowed' : ''
                }`}
              >
                {isLoading ? 'Finishing...' : 'Finish Setup'}
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default Onboarding;
