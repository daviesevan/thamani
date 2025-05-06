import React, { useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import DashboardHeader from './DashboardHeader';
import AuthService from '../../services/auth';

const DashboardLayout = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is authenticated
    if (!AuthService.isAuthenticated()) {
      navigate('/signin');
      return;
    }

    // Check if user has completed onboarding
    if (!AuthService.hasCompletedOnboarding()) {
      navigate('/onboarding');
    }
  }, [navigate]);

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 md:ml-[240px] overflow-hidden flex flex-col">
        <DashboardHeader />
        <div className="flex-1 overflow-auto">
          <main className="p-4 md:p-6 lg:p-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
};

export default DashboardLayout;
