export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface ToolCall {
  tool_name: string;
  parameters: Record<string, any>;
  result: Record<string, any>;
}

export interface ContextSummary {
  last_intent: string;
  referenced_tasks: string[];
  conversation_state: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  timestamp?: string;
  context_window_size?: number;
  response_format?: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  timestamp: string;
  tool_calls: ToolCall[];
  context_summary: ContextSummary;
}

export interface ConversationHistoryResponse {
  conversation_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface DeleteConversationResponse {
  conversation_id: string;
  deleted_at: string;
  message: string;
}