'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ChatInterface from '@/components/chat/ChatInterface';
import { getTasks } from '@/services/api/taskService';

// Simple JWT utility functions
const getAuthToken = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth-token');
  }
  return null;
};

const getUserIdFromToken = () => {
  const token = getAuthToken();
  if (!token) return null;

  try {
    const payload = token.split('.')[1];
    const decodedPayload = atob(payload);
    const parsedPayload = JSON.parse(decodedPayload);
    return parsedPayload.userId || parsedPayload.sub || parsedPayload.id;
  } catch (error) {
    console.error('Error decoding JWT:', error);
    return null;
  }
};

export default function ChatPage() {
  const router = useRouter();
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState<string | null>(null);
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    const checkAuthAndLoadData = async () => {
      const token = getAuthToken();
      if (!token) {
        router.push('/login');
        setAuthChecked(true);
        return;
      }

      const id = getUserIdFromToken();
      if (id) {
        setUserId(id);
        await fetchUserTodos(id);
      } else {
        router.push('/login');
      }
      setAuthChecked(true);
    };

    checkAuthAndLoadData();

    // Listen for storage changes (when login/logout occurs in another tab)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'auth-token') {
        checkAuthAndLoadData();
      }
    };

    window.addEventListener('storage', handleStorageChange);

    // Cleanup
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [router]);

  const fetchUserTodos = async (userId: string) => {
    try {
      const userTodos = await getTasks();
      setTodos(userTodos);
    } catch (error) {
      console.error('Error fetching user todos:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!authChecked) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!userId) {
    return null; // Redirect happens in useEffect
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Todo Chat Assistant</h1>
          <p className="text-gray-600 mt-2">
            Interact with your todo list using natural language
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-700">Your Tasks</h2>
            <span className="bg-blue-100 text-blue-800 text-sm font-medium px-3 py-1 rounded-full">
              {todos.length} tasks
            </span>
          </div>

          {loading ? (
            <div className="text-center py-4">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            </div>
          ) : todos.length === 0 ? (
            <p className="text-gray-500 italic">No tasks yet. Add some tasks or chat with the assistant!</p>
          ) : (
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {todos.slice(0, 5).map((todo: any) => (
                <div
                  key={todo.id}
                  className={`p-3 rounded-md border ${
                    todo.status === 'completed'
                      ? 'bg-green-50 border-green-200'
                      : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex justify-between">
                    <span className={`${todo.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-800'}`}>
                      {todo.title}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      todo.status === 'completed'
                        ? 'bg-green-200 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {todo.status}
                    </span>
                  </div>
                  {todo.description && (
                    <p className="text-sm text-gray-600 mt-1">{todo.description}</p>
                  )}
                </div>
              ))}
              {todos.length > 5 && (
                <p className="text-sm text-gray-500 mt-2">+ {todos.length - 5} more tasks</p>
              )}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <ChatInterface
            userId={userId}
            onTaskUpdate={() => fetchUserTodos(userId)}
          />
        </div>
      </div>
    </div>
  );
}