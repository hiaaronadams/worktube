"use client";

import Link from "next/link";
import { useState } from "react";
import type { Opportunity } from "@/lib/types";
import { PIPELINE_STATUSES } from "@/lib/types";
import { deadlineLabel, daysUntil, titleCase } from "@/lib/format";
import { updateOpportunity } from "@/lib/api";
import { ScoreBadge, StatusBadge, Tag } from "./Badges";

export default function OpportunityCard({
  opportunity,
  onChange,
}: {
  opportunity: Opportunity;
  onChange?: (o: Opportunity) => void;
}) {
  const [opp, setOpp] = useState(opportunity);
  const [busy, setBusy] = useState(false);

  async function patch(payload: {
    saved?: boolean;
    pipeline_status?: string;
  }) {
    setBusy(true);
    try {
      const updated = await updateOpportunity(opp.id, payload);
      setOpp(updated);
      onChange?.(updated);
    } catch (e) {
      console.error(e);
      alert("Update failed — is the API running?");
    } finally {
      setBusy(false);
    }
  }

  const days = daysUntil(opp.deadline);
  const urgent = days !== null && days >= 0 && days <= 14;

  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition hover:shadow-md">
      <div className="flex items-start gap-3">
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex flex-wrap items-center gap-2">
            <ScoreBadge score={opp.relevance_score} label="fit" />
            <ScoreBadge score={opp.design_fit_score} label="design" />
            <StatusBadge status={opp.pipeline_status} />
            <span className="text-xs uppercase tracking-wide text-slate-400">
              {opp.source_name}
            </span>
          </div>
          <Link
            href={`/opportunities/${opp.id}`}
            className="block text-base font-semibold leading-snug text-slate-900 hover:text-tomato-600"
          >
            {opp.title}
          </Link>
          <div className="mt-1 text-sm text-slate-500">
            {opp.buyer_name || "Unknown buyer"}
            {opp.buyer_type ? ` · ${titleCase(opp.buyer_type)}` : ""}
            {opp.country ? ` · ${opp.country}` : ""}
          </div>
          {opp.summary && (
            <p className="mt-2 line-clamp-2 text-sm text-slate-600">
              {opp.summary}
            </p>
          )}
          {opp.tags.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {opp.tags.slice(0, 6).map((t) => (
                <Tag key={t}>{t}</Tag>
              ))}
            </div>
          )}
        </div>

        <div className="flex flex-col items-end gap-2">
          <span
            className={`whitespace-nowrap text-xs font-medium ${
              urgent ? "text-rose-600" : "text-slate-400"
            }`}
          >
            {deadlineLabel(opp.deadline)}
          </span>
          <button
            onClick={() => patch({ saved: !opp.saved })}
            disabled={busy}
            className={`rounded-md border px-2.5 py-1 text-xs font-medium transition disabled:opacity-50 ${
              opp.saved
                ? "border-tomato-200 bg-tomato-50 text-tomato-700"
                : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
            }`}
          >
            {opp.saved ? "★ Saved" : "☆ Save"}
          </button>
          <select
            value={opp.pipeline_status}
            disabled={busy}
            onChange={(e) => patch({ pipeline_status: e.target.value })}
            className="rounded-md border border-slate-200 bg-white px-2 py-1 text-xs text-slate-700 disabled:opacity-50"
          >
            {PIPELINE_STATUSES.map((s) => (
              <option key={s} value={s}>
                {titleCase(s)}
              </option>
            ))}
          </select>
        </div>
      </div>
    </article>
  );
}
