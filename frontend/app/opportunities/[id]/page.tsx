"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getOpportunity, updateOpportunity } from "@/lib/api";
import type { Opportunity } from "@/lib/types";
import { PIPELINE_STATUSES } from "@/lib/types";
import {
  deadlineLabel,
  formatDate,
  titleCase,
} from "@/lib/format";
import { ScoreBadge, StatusBadge, Tag } from "@/components/Badges";

export default function OpportunityDetail({
  params,
}: {
  params: { id: string };
}) {
  const [opp, setOpp] = useState<Opportunity | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notes, setNotes] = useState("");
  const [savingNotes, setSavingNotes] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    getOpportunity(params.id)
      .then((o) => {
        setOpp(o);
        setNotes(o.notes || "");
      })
      .catch((e) => setError((e as Error).message));
  }, [params.id]);

  async function patch(payload: {
    saved?: boolean;
    pipeline_status?: string;
    notes?: string;
  }) {
    if (!opp) return;
    const updated = await updateOpportunity(opp.id, payload);
    setOpp(updated);
  }

  async function saveNotes() {
    setSavingNotes(true);
    try {
      await patch({ notes });
    } finally {
      setSavingNotes(false);
    }
  }

  function copySummary() {
    if (!opp) return;
    const text = [
      opp.title,
      opp.buyer_name ? `Buyer: ${opp.buyer_name}` : "",
      opp.deadline ? `Deadline: ${formatDate(opp.deadline)}` : "",
      opp.source_url ? `Link: ${opp.source_url}` : "",
      "",
      opp.summary || "",
    ]
      .filter(Boolean)
      .join("\n");
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  }

  if (error)
    return (
      <div className="rounded-md border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
        {error}
      </div>
    );
  if (!opp) return <div className="text-slate-400">Loading…</div>;

  return (
    <div>
      <Link
        href="/opportunities"
        className="text-sm text-slate-500 hover:text-tomato-600"
      >
        ← Back to opportunities
      </Link>

      <div className="mt-3 grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Main */}
        <div className="lg:col-span-2">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <ScoreBadge score={opp.relevance_score} label="fit" />
            <ScoreBadge score={opp.design_fit_score} label="design" />
            <StatusBadge status={opp.pipeline_status} />
            <span className="text-xs uppercase tracking-wide text-slate-400">
              {opp.source_name}
            </span>
          </div>
          <h1 className="text-2xl font-semibold leading-tight">{opp.title}</h1>
          <p className="mt-1 text-slate-500">
            {opp.buyer_name || "Unknown buyer"}
            {opp.buyer_type ? ` · ${titleCase(opp.buyer_type)}` : ""}
          </p>

          {opp.tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1">
              {opp.tags.map((t) => (
                <Tag key={t}>{t}</Tag>
              ))}
            </div>
          )}

          {opp.summary && (
            <div className="mt-5">
              <h2 className="mb-1 text-sm font-semibold text-slate-700">Summary</h2>
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-700">
                {opp.summary}
              </p>
            </div>
          )}

          {opp.documents_url.length > 0 && (
            <div className="mt-5">
              <h2 className="mb-1 text-sm font-semibold text-slate-700">Documents</h2>
              <ul className="space-y-1 text-sm">
                {opp.documents_url.map((d) => (
                  <li key={d}>
                    <a
                      href={d}
                      target="_blank"
                      rel="noreferrer"
                      className="text-tomato-600 hover:underline"
                    >
                      {d}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="mt-6">
            <h2 className="mb-1 text-sm font-semibold text-slate-700">Notes</h2>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={4}
              placeholder="Internal notes for the studio…"
              className="w-full rounded-md border border-slate-200 p-2.5 text-sm"
            />
            <button
              onClick={saveNotes}
              disabled={savingNotes || notes === (opp.notes || "")}
              className="mt-2 rounded-md bg-slate-900 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-40"
            >
              {savingNotes ? "Saving…" : "Save notes"}
            </button>
          </div>
        </div>

        {/* Sidebar */}
        <aside className="space-y-4">
          <div className="rounded-lg border border-slate-200 bg-white p-4">
            <div className="flex gap-2">
              <button
                onClick={() => patch({ saved: !opp.saved })}
                className={`flex-1 rounded-md border px-3 py-2 text-sm font-medium ${
                  opp.saved
                    ? "border-tomato-200 bg-tomato-50 text-tomato-700"
                    : "border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
                }`}
              >
                {opp.saved ? "★ Saved" : "☆ Save"}
              </button>
              <button
                onClick={copySummary}
                className="flex-1 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                {copied ? "Copied!" : "Copy summary"}
              </button>
            </div>

            <label className="mt-4 block text-xs font-semibold text-slate-500">
              Pipeline status
            </label>
            <select
              value={opp.pipeline_status}
              onChange={(e) => patch({ pipeline_status: e.target.value })}
              className="mt-1 w-full rounded-md border border-slate-200 px-2 py-1.5 text-sm"
            >
              {PIPELINE_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {titleCase(s)}
                </option>
              ))}
            </select>

            {opp.source_url && (
              <a
                href={opp.source_url}
                target="_blank"
                rel="noreferrer"
                className="mt-4 block rounded-md bg-tomato-500 px-3 py-2 text-center text-sm font-medium text-white hover:bg-tomato-600"
              >
                Open source listing ↗
              </a>
            )}
          </div>

          <dl className="rounded-lg border border-slate-200 bg-white p-4 text-sm">
            <Row label="Deadline" value={`${formatDate(opp.deadline)} · ${deadlineLabel(opp.deadline)}`} />
            <Row label="Posted" value={formatDate(opp.posted_date)} />
            <Row label="Country" value={opp.country || "—"} />
            <Row label="Location" value={opp.location || "—"} />
            <Row label="Status" value={titleCase(opp.status)} />
            <Row
              label="Budget"
              value={
                opp.budget_min || opp.budget_max
                  ? `${opp.budget_min ?? "?"}–${opp.budget_max ?? "?"} ${opp.currency || ""}`
                  : "—"
              }
            />
            <Row label="Contact" value={opp.contact_email || "—"} />
            <Row label="External ID" value={opp.external_id || "—"} />
          </dl>
        </aside>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 border-b border-slate-100 py-1.5 last:border-0">
      <dt className="text-slate-400">{label}</dt>
      <dd className="text-right font-medium text-slate-700">{value}</dd>
    </div>
  );
}
