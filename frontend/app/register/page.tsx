'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';
import RegisterForm from '../../components/auth/RegisterForm';

// Add this type to fix TypeScript error
interface ErrorState {
  msg?: string;
}

interface AuthState {
  isAuthenticated: boolean;
  error?: string | ErrorState;
}

const RegisterPage = () => {
  const { state } = useAuth() as { state: AuthState };
  const router = useRouter();

  // If user is already authenticated, redirect to tasks page
  React.useEffect(() => {
    if (state.isAuthenticated) {
      router.push('/tasks');
    }
  }, [state.isAuthenticated, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-900 to-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full glass backdrop-blur-lg rounded-2xl p-8 space-y-8 border border-violet-500/30 shadow-lg shadow-violet-500/20 dark:shadow-violet-500/30">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 rounded-full glass backdrop-blur-md flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-white">
            Create Account
          </h2>
          <p className="mt-2 text-gray-300">
            Join us today to manage your tasks efficiently
          </p>
        </div>

        <RegisterForm />

        {state.error && (
          <div className="rounded-md glass backdrop-blur-sm p-4 border border-red-500/30">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-400">
                  {typeof state.error === 'string'
                    ? state.error
                    : state.error?.msg || 'Registration failed'}
                </h3>
              </div>
            </div>
          </div>
        )}

        <div className="text-center">
          <p className="text-sm text-gray-300">
            Already have an account?{' '}
            <Link href="/login" className="font-medium text-purple-400 hover:text-indigo-500 transition duration-200">
              Sign in here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
