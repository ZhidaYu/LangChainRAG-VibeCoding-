import { create } from 'zustand';
import { authAPI } from '../api/auth';
import type { UserInfo } from '../api/auth';
import { setTokens, clearTokens, getAccessToken } from '../utils/token';
import { useChatStore } from './chatStore';

interface AuthState {
  user: UserInfo | null;
  init: () => Promise<void>;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
  changePassword: (oldPassword: string, newPassword: string) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,

  init: async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const res = await authAPI.me();
      set({ user: res.data });
    } catch {
      clearTokens();
    }
  },

  login: async (username, password) => {
    const res = await authAPI.login({ username, password });
    setTokens(res.data.access_token, res.data.refresh_token);
    const me = await authAPI.me();
    set({ user: me.data });
    useChatStore.getState().reset();  // 清空上一个用户的聊天状态
  },

  register: async (username, password) => {
    const res = await authAPI.register({ username, password });
    setTokens(res.data.access_token, res.data.refresh_token);
    const me = await authAPI.me();
    set({ user: me.data });
    useChatStore.getState().reset();  // 清空上一个用户的聊天状态
  },

  logout: () => {
    clearTokens();
    set({ user: null });
    useChatStore.getState().reset();  // 清空聊天状态
  },

  changePassword: async (oldPassword, newPassword) => {
    await authAPI.changePassword(oldPassword, newPassword);
  },
}));
