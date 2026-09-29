import { api } from './api';
import { User, TokenResponse } from '../types';

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
  role?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export const authService = {
  async register(payload: RegisterPayload): Promise<User> {
    const response = await api.post<User>('/api/auth/register', payload);
    return response.data;
  },

  async login(payload: LoginPayload): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/api/auth/login', payload);
    return response.data;
  },

  async getMe(): Promise<User> {
    const response = await api.get<User>('/api/auth/me');
    return response.data;
  },
};
