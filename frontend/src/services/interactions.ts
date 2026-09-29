import { api } from './api';
import { Interaction, InteractionType } from '../types';

export interface CreateInteractionPayload {
  contact_id?: string;
  type: InteractionType;
  title: string;
  content: string;
  occurred_at?: string;
}

export const interactionsService = {
  async getInteractions(dealId: string): Promise<Interaction[]> {
    const response = await api.get<Interaction[]>(`/api/deals/${dealId}/interactions`);
    return response.data;
  },

  async createInteraction(dealId: string, payload: CreateInteractionPayload): Promise<Interaction> {
    const response = await api.post<Interaction>(`/api/deals/${dealId}/interactions`, payload);
    return response.data;
  },
};
