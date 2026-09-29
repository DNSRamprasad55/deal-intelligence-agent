import { api } from './api';
import { Deal, DealStage, DealStatus, DashboardMetrics } from '../types';

export interface CreateDealPayload {
  company_id: string;
  name: string;
  description?: string;
  stage?: DealStage;
  value?: number;
  currency?: string;
  probability?: number;
  expected_close_date?: string;
  status?: DealStatus;
}

export interface UpdateDealPayload {
  name?: string;
  description?: string;
  stage?: DealStage;
  value?: number;
  currency?: string;
  probability?: number;
  expected_close_date?: string;
  status?: DealStatus;
  owner_id?: string;
}

export const dealsService = {
  async getDeals(params?: { stage?: string; status?: string }): Promise<Deal[]> {
    const response = await api.get<Deal[]>('/api/deals', { params });
    return response.data;
  },

  async getDealById(id: string): Promise<Deal> {
    const response = await api.get<Deal>(`/api/deals/${id}`);
    return response.data;
  },

  async createDeal(payload: CreateDealPayload): Promise<Deal> {
    const response = await api.post<Deal>('/api/deals', payload);
    return response.data;
  },

  async updateDeal(id: string, payload: UpdateDealPayload): Promise<Deal> {
    const response = await api.put<Deal>(`/api/deals/${id}`, payload);
    return response.data;
  },

  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const response = await api.get<DashboardMetrics>('/api/deals/dashboard');
    return response.data;
  },
};
