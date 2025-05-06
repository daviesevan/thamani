import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/layout/Navbar';
import HeroSection from '../components/home/HeroSection';
import HowItWorks from '../components/home/HowItWorks';
import SupportedRetailers from '../components/home/SupportedRetailers';
import KeyFeatures from '../components/home/KeyFeatures';
import Testimonials from '../components/home/Testimonials';
import CtaSection from '../components/home/CtaSection';
import Footer from '../components/layout/Footer';
import AuthService from '../services/auth';

const Home = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // If user is authenticated, redirect to appropriate page
    if (AuthService.isAuthenticated()) {
      if (AuthService.hasCompletedOnboarding()) {
        // If onboarding is completed, go to dashboard
        navigate('/dashboard');
      } else {
        // If onboarding is not completed, go to onboarding
        navigate('/onboarding');
      }
    }
  }, [navigate]);

  return (
    <div className="min-h-screen">
      <Navbar />
      <HeroSection />
      <HowItWorks />
      <SupportedRetailers />
      <KeyFeatures />
      <Testimonials />
      <CtaSection />
      <Footer />
    </div>
  );
};

export default Home;
