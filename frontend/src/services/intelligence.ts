import { api } from './api';

export interface EvidenceItem {
  memory_id: string;
  content: string;
  context?: string;
  type?: string;
  metadata?: Record<string, unknown>;
  tags?: string[];
  outcome_hint?: 'WON' | 'LOST' | 'UNKNOWN';
}

export interface Recommendation {
  id: string;
  deal_id: string;
  title: string;
  description: string;
  reasoning?: string;
  confidence: number;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'COMPLETED';
  action_id?: string;
  created_at: string;
  updated_at: string;
}

export type OutcomeType = 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL' | 'UNKNOWN';

export interface CreateOutcomePayload {
  outcome_type: OutcomeType;
  description: string;
  impact?: string;
}

export interface OutcomeResponse {
  id: string;
  action_id?: string;
  deal_id: string;
  recommendation_id?: string;
  outcome_type: OutcomeType;
  description: string;
  impact?: string;
  hindsight: {
    status: 'stored' | 'unavailable' | 'not_configured' | 'error';
    bank_id?: string;
    message?: string;
  };
  created_at: string;
}

export interface DealRecallResponse {
  deal_id: string;
  query: string;
  results: EvidenceItem[];
  count: number;
  status: 'success' | 'not_configured' | 'unavailable' | 'error';
  message?: string;
}

export interface DealAnalysisResponse {
  deal_id: string;
  recommendation?: Recommendation;
  situation: string;
  observed_pattern: string;
  risks: string[];
  recommendation_title: string;
  recommendation_description: string;
  reasoning: string;
  alternative_actions: string[];
  unknowns: string[];
  evidence: EvidenceItem[];
  status: 'success' | 'no_evidence' | 'not_configured' | 'unavailable' | 'error';
  message?: string;
}

export const intelligenceService = {
  async recallDealIntelligence(dealId: string, query?: string): Promise<DealRecallResponse> {
    const response = await api.post<DealRecallResponse>(
      `/api/deals/${dealId}/intelligence/recall`,
      { query, limit: 10 }
    );
    return response.data;
  },

  async analyzeDealIntelligence(dealId: string, query?: string): Promise<DealAnalysisResponse> {
    const response = await api.post<DealAnalysisResponse>(
      `/api/deals/${dealId}/intelligence/analyze`,
      { query, limit: 10 }
    );
    return response.data;
  },

  async actOnRecommendation(recommendationId: string, actionStatus: 'ACCEPTED' | 'REJECTED'): Promise<Recommendation> {
    const response = await api.post<Recommendation>(
      `/api/recommendations/${recommendationId}/action`,
      { status: actionStatus }
    );
    return response.data;
  },

  async recordActionOutcome(actionId: string, payload: CreateOutcomePayload): Promise<OutcomeResponse> {
    const response = await api.post<OutcomeResponse>(
      `/api/actions/${actionId}/outcome`,
      payload
    );
    return response.data;
  },
};
