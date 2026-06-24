"use client";

import { useCallback, useEffect, useState } from "react";
import Filters from "@/components/Filters";
import OpportunityCard from "@/components/OpportunityCard";
import { getFacets, listOpportunities } from "@/lib/api";
import type { Facets, Opportunity, OpportunityFilters } from "@/lib/types";

const SORTS = [
  { label: "Best fit", value: "-relevance_score" },
  { label: "Design fit", value: "-design_fit_score" },
  { label: "Deadline (soonest)", value: "deadline" },
  { label: "Newest", value: "-created_at" },
];

export default function OpportunitiesPage() {
  const [filters, setFilters] = useState<OpportunityFilters>({
    sort: "-relevance_score",
    limit: 50,
  });
  const [items, setItems] = useState<Opportunity[]>([]);
  const [total, setTotal] = useState(0);
  const [facets, setFacets] = useState<Facets | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getFacets().then(setFacets).catch(() => setFacets(null));
  }, []);

  const load = useCallback(async (f: OpportunityFilters) => {
    setLoading(true);
    setError(null);
    try {
      const res = await listOpportunities(f);
      setItems(res.items);
      setTotal(res.total);
    } catch (e) {
      setError((e as Error).message);
      setItems([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(filters);
  }, [filters, load]);

  return (
    <div className="flex gap-8">
      <Filters facets={facets} filters={filters} onChange={setFilters} />

      <section className="min-w-0 flex-1">
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold">
            Opportunities{" "}
            <span className="text-sm font-normal text-slate-400">
              {loading ? "…" : `${total} match`}
            </span>
          </h1>
          <select
            value={filters.sort}
            onChange={(e) => setFilters({ ...filters, sort: e.target.value })}
            className="rounded-md border border-slate-200 bg-white px-2.5 py-1.5 text-sm"
          >
            {SORTS.map((s) => (
              <option key={s.value} value={s.value}>
                Sort: {s.label}
              </option>
            ))}
          </select>
        </div>

        {error && (
          <div className="rounded-md border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
            Could not reach the API ({error}). Make sure the backend is running at{" "}
            <code>{process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"}</code>.
          </div>
        )}

        {!error && !loading && items.length === 0 && (
          <div className="rounded-md border border-slate-200 bg-white p-8 text-center text-slate-500">
            No opportunities match these filters.
          </div>
        )}

        <div className="space-y-3">
          {items.map((o) => (
            <OpportunityCard key={o.id} opportunity={o} />
          ))}
        </div>
      </section>
    </div>
  );
}
