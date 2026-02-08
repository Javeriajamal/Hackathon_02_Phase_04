'use client';

import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import ChatInterface from './ChatInterface';

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

const ChatButton: React.FC = () => {
  const [showChat, setShowChat] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    setIsClient(true);

    // Check auth status and update state
    const checkAuth = () => {
      const token = getAuthToken();
      if (token) {
        const id = getUserIdFromToken();
        if (id) {
          setUserId(id);
        } else {
          // Token exists but user ID extraction failed, redirect to login
          window.location.href = '/login';
        }
      } else {
        // No token, set userId to null but don't redirect yet
        setUserId(null);
      }
      setAuthChecked(true);
    };

    // Check immediately
    checkAuth();

    // Listen for storage changes (when login/logout occurs in another tab)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'auth-token') {
        checkAuth();
      }
    };

    window.addEventListener('storage', handleStorageChange);

    // Cleanup
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const toggleChat = () => {
    // Always allow opening the chat interface, but handle authentication inside
    if (!userId) {
      // If not authenticated, we'll still open the chat but show auth prompt
      if (authChecked && !getAuthToken()) {
        // We know for sure the user is not logged in
        // Still open the chat but the ChatInterface will handle the auth requirement
      }
    }
    setShowChat(!showChat);
  };

  if (!isClient) {
    return null; // Don't render on the server
  }

  // Don't render the button until auth is checked
  if (!authChecked) {
    return null;
  }

  // Create the chat button component
  const chatButtonElement = (
    <div className="fixed bottom-6 right-6 z-50">
      <button
        onClick={toggleChat}
        className={`${
          userId ? 'bg-purple-600 hover:bg-purple-500' : 'bg-purple-500 hover:bg-purple-400'
        } text-white p-4 rounded-full shadow-lg transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-opacity-50 neon-glow-purple btn-neon`}
        aria-label="Open chatbot assistant"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9a1 1 0 012 0v6a1 1 0 11-2 0V9z"
          />
        </svg>
      </button>
    </div>
  );

  // If chat is open, create a modal overlay with ChatInterface
  if (showChat) {
    const chatModalElement = (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
        <div className="bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col glass border border-gray-700">
          <div className="flex justify-between items-center p-4 border-b border-gray-700">
            <h2 className="text-xl font-semibold text-purple-300 flex items-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 mr-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9a1 1 0 012 0v6a1 1 0 11-2 0V9z"
                />
              </svg>
              Todo Chat Assistant
            </h2>
            <button
              onClick={() => setShowChat(false)}
              className="text-gray-400 hover:text-gray-200"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
          <div className="flex-1 overflow-auto p-4">
            <ChatInterface userId={userId} />
          </div>
        </div>
      </div>
    );

    // Render both the button and the modal using portals
    return (
      <>
        {chatButtonElement}
        {createPortal(chatModalElement, document.body)}
      </>
    );
  }

  // Only render the button when chat is closed
  return chatButtonElement;
};

export default ChatButton;