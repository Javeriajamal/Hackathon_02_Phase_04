import axios, { AxiosResponse } from 'axios';
import { User, LoginCredentials, RegisterData, LoginResponse, RegisterResponse } from '../../types/auth';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001',  // Use Phase-3 backend for auth
  headers: {
    'Content-Type': 'application/json',
  },
});

// Dynamically update the baseURL if environment changes (for HMR scenarios)
if (typeof window !== 'undefined') {
  const updateBaseUrl = () => {
    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001';
    if (api.defaults.baseURL !== baseUrl) {
      api.defaults.baseURL = baseUrl;
    }
  };

  // Update on module load
  updateBaseUrl();
}

// Request interceptor to add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token might be expired, clear it
      localStorage.removeItem('token');
      // Redirect to login page (this would be handled in the component)
    }
    return Promise.reject(error);
  }
);

// Login function
export const login = async (credentials: LoginCredentials): Promise<LoginResponse> => {
  try {
    const response: AxiosResponse<LoginResponse> = await api.post('/auth/login', credentials);

    // Store the token in localStorage after successful login
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }

    return response.data;
  } catch (error: any) {
    throw error;
  }
};

// Register function
export const register = async (userData: RegisterData): Promise<RegisterResponse> => {
  try {
    const response: AxiosResponse<RegisterResponse> = await api.post('/auth/register', userData);

    // Store the token in localStorage after successful registration
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }

    return response.data;
  } catch (error: any) {
    // Throw the error with proper structure for handling in the UI
    throw error;
  }
};

// Logout function
export const logout = async (): Promise<void> => {
  try {
    await api.post('/auth/logout');
  } catch (error: any) {
    // Even if the logout API fails, we still clear the local token
    console.warn('Logout API call failed:', error);
  } finally {
    // Always remove the token from localStorage regardless of API call outcome
    localStorage.removeItem('token');
  }
};

// Get current user function
export const getCurrentUser = async (token?: string): Promise<User> => {
  try {
    // If token is provided as parameter, use it; otherwise rely on axios interceptor to get from localStorage
    const headers = token ? {
      Authorization: `Bearer ${token}`,
    } : {};

    const response = await api.get('/auth/me', {
      headers,
    });
    return response.data;
  } catch (error: any) {
    throw error;
  }
};

export default api;