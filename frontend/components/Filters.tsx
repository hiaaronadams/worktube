"use client";

import type { Facets, OpportunityFilters } from "@/lib/types";
import { titleCase } from "@/lib/format";

const DEADLINE_WINDOWS = [
  { label: "Any", value: undefined },
  { label: "7 days", value: 7 },
  { label: "14 days", value: 14 },
  { label: "30 days", value: 30 },
  { label: "60 days", value: 60 },
];

function toggle<T>(arr: T[] | undefined, value: T): T[] {
  const set = new Set(arr || []);
  set.has(value) ? set.delete(value) : set.add(value);
  return Array.from(set);
}

export default function Filters({
  facets,
  filters,
  onChange,
}: {
  facets: Facets | null;
  filters: OpportunityFilters;
  onChange: (f: OpportunityFilters) => void;
}) {
  const set = (patch: Partial<OpportunityFilters>) =>
    onChange({ ...filters, ...patch, offset: 0 });

  return (
    <aside className="w-64 shrink-0 space-y-5 text-sm">
      <div>
        <label className="mb-1 block font-semibold text-slate-700">Search</label>
        <input
          type="text"
          value={filters.q || ""}
          onChange={(e) => set({ q: e.target.value })}
          placeholder="Title or summary…"
          className="w-full rounded-md border border-slate-200 px-2.5 py-1.5"
        />
      </div>

      <div>
        <label className="mb-1 block font-semibold text-slate-700">
          Min design/sector fit: {filters.min_score ?? 0}
        </label>
        <input
          type="range"
          min={0}
          max={100}
          step={5}
          value={filters.min_score ?? 0}
          onChange={(e) => set({ min_score: Number(e.target.value) })}
          className="w-full accent-tomato-500"
        />
      </div>

      <div>
        <span className="mb-1 block font-semibold text-slate-700">Deadline</span>
        <div className="flex flex-wrap gap-1">
          {DEADLINE_WINDOWS.map((w) => (
            <button
              key={w.label}
              onClick={() => set({ deadline_within_days: w.value })}
              className={`rounded-md border px-2 py-1 text-xs ${
                filters.deadline_within_days === w.value
                  ? "border-tomato-300 bg-tomato-50 text-tomato-700"
                  : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
              }`}
            >
              {w.label}
            </button>
          ))}
        </div>
      </div>

      <CheckGroup
        title="Source"
        options={facets?.source_types || []}
        selected={filters.source_type}
        onToggle={(v) => set({ source_type: toggle(filters.source_type, v) })}
      />
      <CheckGroup
        title="Buyer type"
        options={facets?.buyer_types || []}
        selected={filters.buyer_type}
        onToggle={(v) => set({ buyer_type: toggle(filters.buyer_type, v) })}
      />
      <CheckGroup
        title="Tags"
        options={facets?.tags || []}
        selected={filters.tags}
        onToggle={(v) => set({ tags: toggle(filters.tags, v) })}
      />

      <div>
        <label className="mb-1 block font-semibold text-slate-700">Country</label>
        <input
          type="text"
          value={filters.country || ""}
          onChange={(e) => set({ country: e.target.value })}
          placeholder="e.g. United States"
          className="w-full rounded-md border border-slate-200 px-2.5 py-1.5"
        />
      </div>

      <button
        onClick={() => onChange({ sort: filters.sort, limit: filters.limit })}
        className="text-xs font-medium text-tomato-600 hover:underline"
      >
        Clear all filters
      </button>
    </aside>
  );
}

function CheckGroup({
  title,
  options,
  selected,
  onToggle,
}: {
  title: string;
  options: string[];
  selected?: string[];
  onToggle: (value: string) => void;
}) {
  if (options.length === 0) return null;
  const sel = new Set(selected || []);
  return (
    <div>
      <span className="mb-1 block font-semibold text-slate-700">{title}</span>
      <div className="max-h-44 space-y-1 overflow-auto pr-1">
        {options.map((o) => (
          <label
            key={o}
            className="flex cursor-pointer items-center gap-2 text-slate-600"
          >
            <input
              type="checkbox"
              checked={sel.has(o)}
              onChange={() => onToggle(o)}
              className="accent-tomato-500"
            />
            {titleCase(o)}
          </label>
        ))}
      </div>
    </div>
  );
}
