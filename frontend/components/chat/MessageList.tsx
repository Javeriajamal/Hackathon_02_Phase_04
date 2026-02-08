import React from 'react';
import { ChatMessage } from '@/types/chat';

interface MessageListProps {
  messages: ChatMessage[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  return (
    <div className="space-y-4">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[80%] rounded-2xl px-4 py-2 ${
              message.role === 'user'
                ? 'bg-purple-700 text-white rounded-br-none neon-glow-purple'
                : message.role === 'assistant'
                ? 'bg-gray-800 text-gray-200 rounded-bl-none border border-gray-700'
                : 'bg-yellow-900/30 text-yellow-300 border border-yellow-700/50'
            }`}
          >
            <div className="whitespace-pre-wrap break-words">
              {message.content}
            </div>
            <div
              className={`text-xs mt-1 ${
                message.role === 'user' ? 'text-purple-200' : 'text-gray-400'
              }`}
            >
              {new Date(message.timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default MessageList;