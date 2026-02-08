import { Task } from '@/types/task';
import axios, { AxiosResponse } from 'axios';

// Create axios instance with base configuration for tasks
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001',  // Use Phase-3 backend which extends Phase-2
  headers: {
    'Content-Type': 'application/json',
  },
});

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

// Note: Using the axios instance configured above with appropriate baseURL

// Get all tasks with optional filters
export const getTasks = async (
  status?: 'all' | 'completed' | 'pending',
  priority?: 'all' | 'low' | 'medium' | 'high',
  sort?: 'created_at' | 'due_date' | 'priority' | 'title',
  order?: 'asc' | 'desc',
  limit: number = 50,
  offset: number = 0
): Promise<Task[]> => {
  const params = new URLSearchParams();
  if (status && status !== 'all') params.append('status', status);
  if (priority && priority !== 'all') params.append('priority', priority);
  if (sort) params.append('sort', sort);
  if (order) params.append('order', order);
  params.append('limit', limit.toString());
  params.append('offset', offset.toString());

  const response = await api.get(`/tasks?${params.toString()}`);

  return response.data.tasks as Task[];
};

// Get a single task by ID
export const getTaskById = async (id: string): Promise<Task> => {
  const response = await api.get(`/tasks/${id}`);
  return response.data;
};

// Create a new task
export const createTask = async (
  taskData: Omit<Task, 'id' | 'created_at' | 'updated_at' | 'user_id'>
): Promise<Task> => {
  const response = await api.post('/tasks', taskData);
  return response.data;
};

// Update an existing task
export const updateTask = async (
  id: string,
  taskData: Partial<Omit<Task, 'id' | 'created_at' | 'updated_at' | 'user_id'>>
): Promise<Task> => {
  const response = await api.put(`/tasks/${id}`, taskData);
  return response.data;
};

// Delete a task
export const deleteTask = async (id: string): Promise<void> => {
  await api.delete(`/tasks/${id}`);
};

// Toggle task completion status
export const toggleTaskStatus = async (id: string): Promise<{ id: string; is_completed: boolean }> => {
  const response = await api.patch(`/tasks/${id}/toggle-status`);
  return response.data;
};