import React from 'react';
import { Navigate, useParams } from 'react-router-dom';
import Home from './pages/Home';
import SignIn from './pages/SignIn';
import SignUp from './pages/SignUp';
import ForgotPassword from './pages/ForgotPassword';
import OTPVerification from './components/auth/OTPVerification';
import Onboarding from './pages/Onboarding';
import LoaderDemo from './pages/LoaderDemo';
import VerificationSuccess from './pages/VerificationSuccess';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import ProductSearch from './pages/ProductSearch';
import ProductDetail from './pages/ProductDetail';
import TrackedProducts from './pages/TrackedProducts';
import Wishlist from './pages/Wishlist';
import DashboardLayout from './components/dashboard/DashboardLayout';

/**
 * Redirect component for product detail pages
 */
const ProductDetailRedirect = () => {
  const { productId } = useParams();
  return <Navigate to={`/dashboard/products/${productId}`} replace />;
};

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
    path: '/verify-email',
    element: <OTPVerification />,
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
  // Redirect old search route to new dashboard search
  {
    path: '/products/search',
    element: <Navigate to="/dashboard/search" replace />,
    exact: true,
  },
  // Redirect old product detail route to dashboard product detail
  {
    path: '/products/:productId',
    element: <ProductDetailRedirect />,
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
        element: <TrackedProducts />,
        exact: true,
      },
      {
        path: 'search',
        element: <ProductSearch />,
        exact: true,
      },
      {
        path: 'alerts',
        element: <div className="p-4">Price Alerts Page (Coming Soon)</div>,
        exact: true,
      },
      {
        path: 'wishlist',
        element: <Wishlist />,
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
      {
        path: 'products/:productId',
        element: <ProductDetail />,
        exact: true,
      },
    ],
  },
];

export default routes;
