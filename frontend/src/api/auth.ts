import apiClient from './client';

export interface LoginParams {
  username: string;
  password: string;
}

export interface RegisterParams {
  username: string;
  password: string;
}

export interface UserInfo {
  id: string;
  username: string;
  role: string;
  is_active: number;
  created_at: string;
}

export const authAPI = {
  login: (params: LoginParams) =>
    apiClient.post('/auth/login', params),
  register: (params: RegisterParams) =>
    apiClient.post('/auth/register', params),
  refresh: (refreshToken: string) =>
    apiClient.post('/auth/refresh', { refresh_token: refreshToken }),
  changePassword: (oldPassword: string, newPassword: string) =>
    apiClient.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword }),
  me: () => apiClient.get<UserInfo>('/auth/me'),
};
