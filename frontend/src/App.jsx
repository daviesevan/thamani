import React, { useEffect } from 'react'
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import routes from './routes'
import { AuthProvider } from './context/AuthContext'

// Component to handle hash redirects
const HashRedirectHandler = () => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Check if we have a hash that looks like a Supabase auth redirect
    if (location.hash && location.hash.includes('access_token') && location.hash.includes('type=signup')) {
      // Set a flag in sessionStorage to prevent duplicate toasts
      sessionStorage.setItem('verification_redirect', 'true');

      // Redirect to the verification success page with the hash intact
      navigate({
        pathname: '/verify-success',
        hash: location.hash
      });
    }
  }, [location, navigate]);

  return null;
};

const AppRoutes = () => {
  return (
    <>
      <HashRedirectHandler />
      <Routes>
        {routes.map((route, index) => {
          // Handle nested routes
          if (route.children) {
            return (
              <Route
                key={index}
                path={route.path}
                element={route.element}
                exact={route.exact}
              >
                {route.children.map((childRoute, childIndex) => (
                  <Route
                    key={`${index}-${childIndex}`}
                    path={childRoute.path}
                    element={childRoute.element}
                    exact={childRoute.exact}
                  />
                ))}
              </Route>
            );
          }

          // Regular routes
          return (
            <Route
              key={index}
              path={route.path}
              element={route.element}
              exact={route.exact}
            />
          );
        })}
      </Routes>
    </>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App