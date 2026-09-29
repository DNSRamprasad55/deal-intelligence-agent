import { api } from './api';
import { Company, Contact } from '../types';

export interface CreateCompanyPayload {
  name: string;
  industry?: string;
  size?: string;
  website?: string;
  description?: string;
}

export interface CreateContactPayload {
  name: string;
  job_title?: string;
  email?: string;
  role_in_deal?: string;
}

export const companiesService = {
  async getCompanies(): Promise<Company[]> {
    const response = await api.get<Company[]>('/api/companies');
    return response.data;
  },

  async getCompanyById(id: string): Promise<Company> {
    const response = await api.get<Company>(`/api/companies/${id}`);
    return response.data;
  },

  async createCompany(payload: CreateCompanyPayload): Promise<Company> {
    const response = await api.post<Company>('/api/companies', payload);
    return response.data;
  },

  async addContact(companyId: string, payload: CreateContactPayload): Promise<Contact> {
    const response = await api.post<Contact>(`/api/companies/${companyId}/contacts`, payload);
    return response.data;
  },
};
