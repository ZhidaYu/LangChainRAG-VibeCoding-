import apiClient from './client';

export interface Conversation {
  id: string;
  title: string;
  is_active: number;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  sources: string;
  created_at: string;
}

export const conversationAPI = {
  list: (page = 1, size = 20) =>
    apiClient.get<Conversation[]>('/conversations', { params: { page, size } }),
  create: (title?: string) =>
    apiClient.post<Conversation>('/conversations', title ? { title } : {}),
  getMessages: (convId: string) =>
    apiClient.get<Message[]>(`/conversations/${convId}`),
  delete: (convId: string) =>
    apiClient.delete(`/conversations/${convId}`),
  updateTitle: (convId: string, title: string) =>
    apiClient.put(`/conversations/${convId}`, { title }),
};
