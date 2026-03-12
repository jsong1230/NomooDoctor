/**
 * 채팅 상태 관리 스토어 (Zustand)
 */

import { create } from 'zustand';
import type { ChatSession, ChatMessage } from '@/types/chat';

interface ChatState {
  sessions: ChatSession[];
  currentSession: ChatSession | null;
  messages: ChatMessage[];
  isStreaming: boolean;
  streamingContent: string;

  // Actions
  setSessions: (sessions: ChatSession[]) => void;
  setCurrentSession: (session: ChatSession | null) => void;
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  setIsStreaming: (streaming: boolean) => void;
  appendStreamingContent: (text: string) => void;
  resetStreamingContent: () => void;
}

export const chatStore = create<ChatState>()((set) => ({
  sessions: [],
  currentSession: null,
  messages: [],
  isStreaming: false,
  streamingContent: '',

  setSessions: (sessions) => set({ sessions }),

  setCurrentSession: (session) => set({ currentSession: session }),

  setMessages: (messages) => set({ messages }),

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  setIsStreaming: (streaming) => set({ isStreaming: streaming }),

  appendStreamingContent: (text) =>
    set((state) => ({
      streamingContent: state.streamingContent + text,
    })),

  resetStreamingContent: () => set({ streamingContent: '' }),
}));
