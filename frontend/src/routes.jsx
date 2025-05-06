import React from 'react';
import Home from './pages/Home';
import SignIn from './pages/SignIn';
import SignUp from './pages/SignUp';
import ForgotPassword from './pages/ForgotPassword';
import Onboarding from './pages/Onboarding';
import LoaderDemo from './pages/LoaderDemo';
import VerificationSuccess from './pages/VerificationSuccess';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import DashboardLayout from './components/dashboard/DashboardLayout';

/**
 * Application routes configuration
 */
const routes = [
  {
    path: '/',
    element: <Home />,
    exact: true,
  },
  {
    path: '/signin',
    element: <SignIn />,
    exact: true,
  },
  {
    path: '/signup',
    element: <SignUp />,
    exact: true,
  },
  {
    path: '/forgot-password',
    element: <ForgotPassword />,
    exact: true,
  },
  {
    path: '/onboarding',
    element: <Onboarding />,
    exact: true,
  },
  {
    path: '/loader-demo',
    element: <LoaderDemo />,
    exact: true,
  },
  {
    path: '/verify-success',
    element: <VerificationSuccess />,
    exact: true,
  },
  // Dashboard routes
  {
    path: '/dashboard',
    element: <DashboardLayout />,
    exact: false,
    children: [
      {
        path: '',
        element: <Dashboard />,
        exact: true,
      },
      {
        path: 'products',
        element: <div className="p-4">Products Page (Coming Soon)</div>,
        exact: true,
      },
      {
        path: 'alerts',
        element: <div className="p-4">Price Alerts Page (Coming Soon)</div>,
        exact: true,
      },
      {
        path: 'wishlist',
        element: <div className="p-4">Wishlist Page (Coming Soon)</div>,
        exact: true,
      },
      {
        path: 'analytics',
        element: <div className="p-4">Analytics Page (Coming Soon)</div>,
        exact: true,
      },
      {
        path: 'settings',
        element: <Settings />,
        exact: true,
      },
    ],
  },
];

export default routes;
