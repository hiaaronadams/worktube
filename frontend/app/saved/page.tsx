"use client";

import { useEffect, useState } from "react";
import OpportunityCard from "@/components/OpportunityCard";
import { listOpportunities } from "@/lib/api";
import type { Opportunity } from "@/lib/types";

export default function SavedPage() {
  const [items, setItems] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  function load() {
    setLoading(true);
    listOpportunities({ saved: true, sort: "-relevance_score", limit: 200 })
      .then((res) => setItems(res.items))
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  return (
    <section>
      <h1 className="mb-4 text-xl font-semibold">
        Saved opportunities{" "}
        <span className="text-sm font-normal text-slate-400">
          {loading ? "…" : items.length}
        </span>
      </h1>

      {error && (
        <div className="rounded-md border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {error}
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <div className="rounded-md border border-slate-200 bg-white p-8 text-center text-slate-500">
          Nothing saved yet. Hit ★ Save on an opportunity to keep it here.
        </div>
      )}

      <div className="space-y-3">
        {items.map((o) => (
          <OpportunityCard
            key={o.id}
            opportunity={o}
            onChange={(u) => {
              // drop it from the list if it was un-saved
              if (!u.saved) setItems((prev) => prev.filter((x) => x.id !== u.id));
            }}
          />
        ))}
      </div>
    </section>
  );
}
