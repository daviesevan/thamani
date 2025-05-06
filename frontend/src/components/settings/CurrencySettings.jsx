import React, { useState, useEffect } from 'react';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import { DollarSign } from 'lucide-react';
import AuthService from '../../services/auth';
import api from '../../services/api';

const currencies = [
  { code: 'KES', name: 'Kenyan Shilling', symbol: 'KSh' },
  { code: 'USD', name: 'US Dollar', symbol: '$' },
  { code: 'EUR', name: 'Euro', symbol: '€' },
  { code: 'GBP', name: 'British Pound', symbol: '£' }
];

const CurrencySettings = () => {
  const toast = useToast();
  const { user, userProfile, updateUserPreferences } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const [selectedCurrency, setSelectedCurrency] = useState('KES');

  useEffect(() => {
    // Initialize currency from user profile
    if (userProfile && userProfile.preferences && userProfile.preferences.currency) {
      setSelectedCurrency(userProfile.preferences.currency);
    }
  }, [userProfile]);

  const handleCurrencyChange = (e) => {
    setSelectedCurrency(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    console.log('CurrencySettings: Form submitted', { selectedCurrency });

    try {
      if (!user || !user.id) {
        console.error('CurrencySettings: User not authenticated', { user });
        throw new Error('User not authenticated');
      }

      console.log('CurrencySettings: Updating currency preference', { userId: user.id, currency: selectedCurrency });

      // Use the updateUserPreferences method from AuthContext
      await updateUserPreferences(user.id, {
        currency: selectedCurrency
      });

      console.log('CurrencySettings: Currency preference updated successfully');
      toast.success('Currency preference updated successfully');
    } catch (error) {
      console.error('CurrencySettings: Error updating currency preference:', error);

      // Show a more detailed error message
      if (error.message.includes('Network Error')) {
        toast.error('Network error: Please check your connection or the server might be down');
      } else if (error.message.includes('401')) {
        toast.error('Authentication error: Please sign in again');
      } else {
        toast.error(`Failed to update currency preference: ${error.message}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="font-serif">
      <h2 className="text-xl font-bold mb-4">Currency Preferences</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        <p className="text-sm text-muted-foreground">
          Choose your preferred currency for displaying prices across the platform.
        </p>

        <div className="space-y-4">
          <label htmlFor="currency" className="block text-sm font-medium mb-1">
            Display Currency
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-muted-foreground">
              <DollarSign size={18} />
            </div>
            <select
              id="currency"
              value={selectedCurrency}
              onChange={handleCurrencyChange}
              className="w-full pl-10 p-2 border border-border bg-background focus:outline-none focus:ring-1 focus:ring-primary appearance-none"
            >
              {currencies.map(currency => (
                <option key={currency.code} value={currency.code}>
                  {currency.name} ({currency.symbol})
                </option>
              ))}
            </select>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            This will be used as your default currency for all price displays.
          </p>
        </div>

        {/* Submit Button */}
        <div>
          <button
            type="submit"
            disabled={isLoading}
            className={`py-2 px-4 border border-transparent font-medium text-sm bg-primary text-white dark:text-black hover:bg-primary/90 focus:outline-none focus:ring-1 focus:ring-primary ${
              isLoading ? 'opacity-70 cursor-not-allowed' : ''
            }`}
          >
            {isLoading ? 'Saving...' : 'Save Preference'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CurrencySettings;
