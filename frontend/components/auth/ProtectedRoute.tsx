'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  fallback = <div className="flex justify-center items-center h-screen">Redirecting to login...</div>
}) => {
  const { state } = useAuth();
  const router = useRouter();

  React.useEffect(() => {
    if (!state.isAuthenticated && !state.isLoading) {
      router.push('/login');
    }
  }, [state.isAuthenticated, state.isLoading, router]);

  if (!state.isAuthenticated && !state.isLoading) {
    return <>{fallback}</>;
  }

  if (state.isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;