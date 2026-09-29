export type UserRole = 'sales_rep' | 'manager' | 'admin';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Contact {
  id: string;
  company_id: string;
  name: string;
  job_title?: string;
  email?: string;
  role_in_deal?: string;
  created_at: string;
  updated_at: string;
}

export interface Company {
  id: string;
  name: string;
  industry?: string;
  size?: string;
  website?: string;
  description?: string;
  created_at: string;
  updated_at: string;
  contacts?: Contact[];
}

export type DealStage =
  | 'DISCOVERY'
  | 'QUALIFICATION'
  | 'TECHNICAL_EVALUATION'
  | 'PROPOSAL'
  | 'NEGOTIATION'
  | 'CLOSED_WON'
  | 'CLOSED_LOST';

export type DealStatus = 'OPEN' | 'WON' | 'LOST';

export type InteractionType =
  | 'CALL'
  | 'MEETING'
  | 'EMAIL'
  | 'NOTE'
  | 'DEMO'
  | 'TECHNICAL_REVIEW';

export interface Interaction {
  id: string;
  deal_id: string;
  contact_id?: string;
  type: InteractionType;
  title: string;
  content: string;
  occurred_at: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
  hindsight_memory_status: string;
}

export interface Deal {
  id: string;
  company_id: string;
  owner_id?: string;
  name: string;
  description?: string;
  stage: DealStage;
  value: number;
  currency: string;
  probability: number;
  expected_close_date?: string;
  status: DealStatus;
  created_at: string;
  updated_at: string;
  company?: Company;
  owner?: User;
  interactions?: Interaction[];
}

export interface DashboardMetrics {
  total_active_deals: number;
  open_pipeline_value: number;
  won_deals: number;
  lost_deals: number;
  recent_deals: Deal[];
  recent_interactions: Interaction[];
}

export interface HealthStatus {
  status: string;
  application: string;
  environment: string;
  database: string;
  hindsight: string;
}
