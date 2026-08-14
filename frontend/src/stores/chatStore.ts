import { create } from 'zustand';
import { conversationAPI } from '../api/chat';
import type { Conversation, Message } from '../api/chat';

interface ChatState {
  conversations: Conversation[];
  currentConvId: string | null;
  messages: Message[];
  streaming: boolean;
  streamingContent: string;
  sources: SourceMeta[];
  loadConversations: () => Promise<void>;
  createConversation: () => Promise<string>;
  selectConversation: (id: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  addMessage: (msg: Message) => void;
  setStreaming: (v: boolean) => void;
  appendStreamToken: (token: string) => void;
  setSources: (sources: SourceMeta[]) => void;
  resetStream: () => void;
  reset: () => void;
}

export interface SourceMeta {
  source_id: number;
  file: string;
  chunk_text: string;
  score: number;
}

export const useChatStore = create<ChatState>((set, get) => ({
  conversations: [],
  currentConvId: null,
  messages: [],
  streaming: false,
  streamingContent: '',
  sources: [],

  loadConversations: async () => {
    const res = await conversationAPI.list();
    set({ conversations: res.data });
  },

  createConversation: async () => {
    const res = await conversationAPI.create();
    const conv = res.data;
    set((s) => ({
      conversations: [conv, ...s.conversations],
      currentConvId: conv.id,
      messages: [],
      sources: [],
    }));
    return conv.id;
  },

  selectConversation: async (id) => {
    const res = await conversationAPI.getMessages(id);
    set({
      currentConvId: id,
      messages: res.data,
      streamingContent: '',
      sources: [],
    });
  },

  deleteConversation: async (id) => {
    await conversationAPI.delete(id);
    set((s) => {
      const convs = s.conversations.filter((c) => c.id !== id);
      return {
        conversations: convs,
        currentConvId: s.currentConvId === id ? null : s.currentConvId,
        messages: s.currentConvId === id ? [] : s.messages,
      };
    });
  },

  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),

  setStreaming: (v) => set({ streaming: v }),

  appendStreamToken: (token) =>
    set((s) => ({ streamingContent: s.streamingContent + token })),

  setSources: (sources) => set({ sources }),

  resetStream: () => set({ streaming: false, streamingContent: '' }),

  reset: () => set({
    conversations: [],
    currentConvId: null,
    messages: [],
    streaming: false,
    streamingContent: '',
    sources: [],
  }),
}));
