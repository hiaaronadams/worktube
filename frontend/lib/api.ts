import type {
  Facets,
  Opportunity,
  OpportunityFilters,
  OpportunityList,
} from "./types";

function resolveApiBase(): string {
  const raw = process.env.NEXT_PUBLIC_API_BASE?.trim() || "http://localhost:8000";
  const base = raw.replace(/\/$/, "");
  // "/api" (relative, same-origin) and absolute http(s) URLs pass through.
  // A bare hostname (e.g. "api.example.com") is assumed https.
  if (base.startsWith("/") || /^https?:\/\//.test(base)) return base;
  return `https://${base}`;
}

const API_BASE = resolveApiBase();

function buildQuery(filters: OpportunityFilters): string {
  const params = new URLSearchParams();
  const append = (key: string, value: unknown) => {
    if (value === undefined || value === null || value === "") return;
    if (Array.isArray(value)) {
      value.forEach((v) => params.append(key, String(v)));
    } else {
      params.append(key, String(value));
    }
  };
  append("source_type", filters.source_type);
  append("buyer_type", filters.buyer_type);
  append("pipeline_status", filters.pipeline_status);
  append("saved", filters.saved);
  append("min_score", filters.min_score);
  append("deadline_within_days", filters.deadline_within_days);
  append("tags", filters.tags);
  append("country", filters.country);
  append("q", filters.q);
  append("sort", filters.sort);
  append("limit", filters.limit);
  append("offset", filters.offset);
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${text || res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export async function listOpportunities(
  filters: OpportunityFilters = {}
): Promise<OpportunityList> {
  const res = await fetch(`${API_BASE}/opportunities${buildQuery(filters)}`, {
    cache: "no-store",
  });
  return handle<OpportunityList>(res);
}

export async function getOpportunity(id: string): Promise<Opportunity> {
  const res = await fetch(`${API_BASE}/opportunities/${id}`, {
    cache: "no-store",
  });
  return handle<Opportunity>(res);
}

export async function getFacets(): Promise<Facets> {
  const res = await fetch(`${API_BASE}/opportunities/facets`, {
    cache: "no-store",
  });
  return handle<Facets>(res);
}

export async function updateOpportunity(
  id: string,
  payload: { saved?: boolean; pipeline_status?: string; notes?: string }
): Promise<Opportunity> {
  const res = await fetch(`${API_BASE}/opportunities/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handle<Opportunity>(res);
}
