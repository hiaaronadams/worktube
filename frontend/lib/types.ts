export interface Opportunity {
  id: string;
  source_type: string;
  source_name: string;
  source_url: string | null;
  external_id: string | null;
  title: string;
  buyer_name: string | null;
  buyer_type: string | null;
  summary: string | null;
  category_normalized: string[];
  tags: string[];
  location: string | null;
  country: string | null;
  posted_date: string | null;
  deadline: string | null;
  status: string;
  budget_min: number | null;
  budget_max: number | null;
  currency: string | null;
  documents_url: string[];
  contact_email: string | null;
  relevance_score: number;
  design_fit_score: number;
  saved: boolean;
  pipeline_status: string;
  notes: string | null;
  last_seen_at: string;
  created_at: string;
}

export interface OpportunityList {
  total: number;
  limit: number;
  offset: number;
  items: Opportunity[];
}

export interface Facets {
  source_types: string[];
  buyer_types: string[];
  tags: string[];
  countries: string[];
  pipeline_statuses: string[];
}

export interface OpportunityFilters {
  source_type?: string[];
  buyer_type?: string[];
  pipeline_status?: string[];
  saved?: boolean;
  min_score?: number;
  deadline_within_days?: number;
  tags?: string[];
  country?: string;
  q?: string;
  sort?: string;
  limit?: number;
  offset?: number;
}

export const PIPELINE_STATUSES = [
  "new",
  "reviewing",
  "maybe",
  "pitched",
  "submitted",
  "won",
  "lost",
  "ignored",
] as const;
