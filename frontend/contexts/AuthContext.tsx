'use client';

import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { login, register, logout, getCurrentUser } from '../services/api/authService';
import { User, LoginCredentials, RegisterData } from '../types/auth';

type AuthState = {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;
};

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGIN_FAILURE'; payload: string }
  | { type: 'REGISTER_START' }
  | { type: 'REGISTER_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'REGISTER_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_ERROR' }
  | { type: 'CHECK_AUTH_STATUS'; payload: { user: User | null; token: string | null } };

type AuthDispatch = React.Dispatch<AuthAction>;

// Define the full context type
type AuthContextType = {
  state: AuthState;
  dispatch: AuthDispatch;
  handleLogin: (credentials: LoginCredentials) => Promise<{ success: boolean; error?: string }>;
  handleRegister: (userData: RegisterData) => Promise<{ success: boolean; error?: string }>;
  handleLogout: () => Promise<void>;
  clearError: () => void;
};

const initialState: AuthState = {
  user: null,
  token: null,
  isLoading: false,
  error: null,
  isAuthenticated: false,
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isLoading: false,
        error: null,
        isAuthenticated: true,
      };
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isLoading: false,
        error: action.payload,
        isAuthenticated: false,
      };
    case 'REGISTER_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    case 'REGISTER_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isLoading: false,
        error: null,
        isAuthenticated: true,
      };
    case 'REGISTER_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isLoading: false,
        error: action.payload,
        isAuthenticated: false,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    case 'CHECK_AUTH_STATUS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: !!action.payload.token,
      };
    default:
      return state;
  }
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);
  const router = useRouter();

  // Check authentication status on initial load
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const token = localStorage.getItem('token');

        if (token) {
          // Validate the token by fetching user data using the authService
          // getCurrentUser will use the token from localStorage via axios interceptors
          const user = await getCurrentUser();

          // Only update state if we got a valid user response
          if (user && user.id) {
            dispatch({
              type: 'CHECK_AUTH_STATUS',
              payload: { user, token }
            });
          } else {
            // If user data is not valid, treat as invalid token
            localStorage.removeItem('token');
            dispatch({
              type: 'CHECK_AUTH_STATUS',
              payload: { user: null, token: null }
            });
          }
        } else {
          // No token in storage, ensure state is not authenticated
          dispatch({
            type: 'CHECK_AUTH_STATUS',
            payload: { user: null, token: null }
          });
        }
      } catch (error) {
        // Token is invalid or expired, clear it
        localStorage.removeItem('token');
        dispatch({
          type: 'CHECK_AUTH_STATUS',
          payload: { user: null, token: null }
        });
      }
    };

    checkAuthStatus();
  }, []);

  // Login function
  const handleLogin = async (credentials: LoginCredentials) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const response = await login(credentials);
      const { user, access_token } = response;

      // Store token in localStorage
      localStorage.setItem('token', access_token);

      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: { user, token: access_token },
      });

      // Dispatch a custom event to notify other parts of the app about auth change
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('authChanged'));
      }

      router.push('/tasks');
      return { success: true };
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail?.[0]?.msg || error.response?.data?.detail || 'Login failed';
      dispatch({
        type: 'LOGIN_FAILURE',
        payload: errorMessage,
      });
      return { success: false, error: errorMessage };
    }
  };

  // Register function
  const handleRegister = async (userData: RegisterData) => {
    dispatch({ type: 'REGISTER_START' });
    try {
      const response = await register(userData);

      // For registration, the response contains user data and token in the same object
      // Create a user object from the response
      const user = {
        id: response.id,
        email: response.email,
        name: response.username, // Using username as name in the user object
        is_active: true,
        created_at: response.created_at,
        updated_at: response.created_at // Use created_at since updated_at might not be in the response
      };
      const access_token = response.access_token;

      // Store token in localStorage
      localStorage.setItem('token', access_token);

      dispatch({
        type: 'REGISTER_SUCCESS',
        payload: { user, token: access_token },
      });

      router.push('/tasks');
      return { success: true };
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail?.[0]?.msg || error.response?.data?.detail || 'Registration failed';
      dispatch({
        type: 'REGISTER_FAILURE',
        payload: errorMessage,
      });
      return { success: false, error: errorMessage };
    }
  };

  // Logout function
  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      // Even if logout API fails, clear local state
      console.error('Logout API error:', error);
    } finally {
      // Clear token from localStorage
      localStorage.removeItem('token');

      dispatch({ type: 'LOGOUT' });

      // Dispatch a custom event to notify other parts of the app about auth change
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('authChanged'));
      }

      router.push('/login');
    }
  };

  // Clear error
  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  return (
    <AuthContext.Provider value={{
      state,
      dispatch,
      handleLogin,
      handleRegister,
      handleLogout,
      clearError
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};