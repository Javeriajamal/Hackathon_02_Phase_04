'use client';

import React, { useState, useRef, useEffect } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { ChatMessage } from '@/types/chat';

// Simple JWT utility functions
const getAuthToken = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token'); // Use 'token' as per AuthContext
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

interface ChatInterfaceProps {
  userId?: string;
  onTaskUpdate?: () => void; // Callback to trigger task list refresh after task operations
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ userId: userIdProp, onTaskUpdate }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initialize user ID
    const initializeUserId = () => {
      // Use the userId from props if provided, otherwise get from JWT
      if (userIdProp) {
        setUserId(userIdProp);
      } else {
        const jwtUserId = getUserIdFromToken();
        if (jwtUserId) {
          setUserId(jwtUserId);
        } else {
          setUserId(null);
        }
      }
      setIsCheckingAuth(false);
    };

    initializeUserId();

    // Listen for storage changes (when login/logout occurs in another tab or same tab)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'auth-token') {
        // Token changed, recheck authentication
        const newUserId = getUserIdFromToken();
        if (newUserId) {
          setUserId(newUserId);
        } else {
          setUserId(null);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);

    // Also listen for custom events in case of programmatic login/logout
    const handleAuthChange = () => {
      const newUserId = getUserIdFromToken();
      if (newUserId) {
        setUserId(newUserId);
      } else {
        setUserId(null);
      }
    };

    window.addEventListener('authChanged', handleAuthChange);

    // Cleanup
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('authChanged', handleAuthChange);
    };
  }, [userIdProp]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (messageText: string) => {
    if (!messageText.trim() || isLoading || !userId) return;

    // Get the auth token
    const token = getAuthToken();

    // Add user message to the list
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send message to ChatKit API using fetch
      const response = await fetch('/api/chatkit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage], // Send the full conversation context
          userId: userId,
          authToken: token, // Pass the auth token for task operations
          content: messageText
        })
      });

      // Check the x-task-operation header for task updates
      const taskOperation = response.headers.get('x-task-operation');
      if (taskOperation && ['add_task', 'update_task', 'delete_task', 'complete_task'].includes(taskOperation)) {
        if (onTaskUpdate) {
          onTaskUpdate();
        }
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Add AI response to the list
      const aiMessage: ChatMessage = {
        id: data.id || `ai-${Date.now()}`,
        role: data.role || 'assistant',
        content: data.content,
        timestamp: data.timestamp || new Date().toISOString(),
      };

      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message to the list
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'system',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  if (isCheckingAuth) {
    return (
      <div className="flex flex-col h-[600px] border border-gray-700 rounded-lg bg-gray-900 glass">
        <div className="flex-1 flex items-center justify-center bg-gray-900">
          <div className="text-center text-gray-400">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 neon-glow-purple"></div>
            <p className="mt-2">Checking authentication...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!userId) {
    return (
      <div className="flex flex-col h-[600px] border border-gray-700 rounded-lg bg-gray-900 glass">
        <div className="flex-1 overflow-y-auto p-4 bg-gray-900">
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
            <div className="mb-4">
              <div className="mx-auto bg-purple-900/30 text-purple-300 rounded-full w-16 h-16 flex items-center justify-center neon-glow-purple">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
            </div>
            <h3 className="text-lg font-medium text-gray-300 mb-2">Please Log In</h3>
            <p className="text-sm mb-4">You need to be logged in to use the chat assistant.</p>
            <button
              onClick={() => window.location.href = '/login'}
              className="bg-purple-700 hover:bg-purple-600 text-white py-2 px-4 rounded-md transition-colors btn-neon neon-glow-purple"
            >
              Go to Login
            </button>
          </div>
        </div>
        <div className="border-t border-gray-700 p-4 bg-gray-900">
          <div className="text-center text-gray-400 italic">
            Please log in to send messages
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[600px] border border-gray-700 rounded-lg bg-gray-900 glass">
      <div className="flex-1 overflow-y-auto p-4 bg-gray-900">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
            <div className="mb-4">
              <div className="mx-auto bg-purple-900/30 text-purple-300 rounded-full w-16 h-16 flex items-center justify-center neon-glow-purple">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
            </div>
            <h3 className="text-lg font-medium text-gray-300 mb-2">Welcome to Todo Chat Assistant!</h3>
            <p className="text-sm max-w-md">
              You can interact with your todo list using natural language. Try commands like:<br />
              <span className="font-mono bg-purple-900/30 p-1 rounded mt-2 block text-left text-purple-300 border border-purple-700/50">"Add a task to buy groceries"</span>
              <span className="font-mono bg-purple-900/30 p-1 rounded mt-1 block text-left text-purple-300 border border-purple-700/50">"Show my tasks"</span>
              <span className="font-mono bg-purple-900/30 p-1 rounded mt-1 block text-left text-purple-300 border border-purple-700/50">"Complete task #1"</span>
            </p>
          </div>
        ) : (
          <MessageList messages={messages} />
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-gray-700 p-4 bg-gray-900">
        <MessageInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
};

export default ChatInterface;