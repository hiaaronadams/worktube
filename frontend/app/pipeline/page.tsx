"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { listOpportunities, updateOpportunity } from "@/lib/api";
import type { Opportunity } from "@/lib/types";
import { PIPELINE_STATUSES } from "@/lib/types";
import { deadlineLabel, titleCase } from "@/lib/format";
import { ScoreBadge } from "@/components/Badges";

// Columns shown on the board (ignored/lost hidden by default to reduce noise).
const COLUMNS = PIPELINE_STATUSES.filter((s) => s !== "ignored");

export default function PipelinePage() {
  const [items, setItems] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listOpportunities({ sort: "-relevance_score", limit: 500 })
      .then((res) => setItems(res.items))
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false));
  }, []);

  async function move(opp: Opportunity, status: string) {
    setItems((prev) =>
      prev.map((x) => (x.id === opp.id ? { ...x, pipeline_status: status } : x))
    );
    try {
      await updateOpportunity(opp.id, { pipeline_status: status });
    } catch {
      // revert on failure
      setItems((prev) =>
        prev.map((x) =>
          x.id === opp.id ? { ...x, pipeline_status: opp.pipeline_status } : x
        )
      );
    }
  }

  if (error)
    return (
      <div className="rounded-md border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
        {error}
      </div>
    );

  return (
    <section>
      <h1 className="mb-4 text-xl font-semibold">Pipeline</h1>
      {loading ? (
        <div className="text-slate-400">Loading…</div>
      ) : (
        <div className="flex gap-3 overflow-x-auto pb-4">
          {COLUMNS.map((col) => {
            const cards = items.filter((o) => o.pipeline_status === col);
            return (
              <div key={col} className="w-64 shrink-0">
                <div className="mb-2 flex items-center justify-between px-1">
                  <span className="text-sm font-semibold">{titleCase(col)}</span>
                  <span className="text-xs text-slate-400">{cards.length}</span>
                </div>
                <div className="space-y-2 rounded-lg bg-slate-100 p-2">
                  {cards.length === 0 && (
                    <p className="px-1 py-4 text-center text-xs text-slate-400">
                      Empty
                    </p>
                  )}
                  {cards.map((o) => (
                    <div
                      key={o.id}
                      className="rounded-md border border-slate-200 bg-white p-2.5 text-sm shadow-sm"
                    >
                      <div className="mb-1 flex items-center justify-between">
                        <ScoreBadge score={o.relevance_score} label="fit" />
                        <span className="text-[11px] text-slate-400">
                          {o.source_name}
                        </span>
                      </div>
                      <Link
                        href={`/opportunities/${o.id}`}
                        className="line-clamp-2 font-medium leading-snug text-slate-800 hover:text-tomato-600"
                      >
                        {o.title}
                      </Link>
                      <div className="mt-1 text-xs text-slate-400">
                        {deadlineLabel(o.deadline)}
                      </div>
                      <select
                        value={o.pipeline_status}
                        onChange={(e) => move(o, e.target.value)}
                        className="mt-2 w-full rounded border border-slate-200 px-1.5 py-1 text-xs text-slate-600"
                      >
                        {PIPELINE_STATUSES.map((s) => (
                          <option key={s} value={s}>
                            Move to: {titleCase(s)}
                          </option>
                        ))}
                      </select>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
