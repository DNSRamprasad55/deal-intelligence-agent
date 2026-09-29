import { api } from './api';
import { HealthStatus } from '../types';

export const healthService = {
  async getStatus(): Promise<HealthStatus> {
    const response = await api.get<HealthStatus>('/health');
    return response.data;
  },
};
