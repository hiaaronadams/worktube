export function formatDate(value: string | null): string {
  if (!value) return "—";
  const d = new Date(value);
  if (isNaN(d.getTime())) return value;
  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function daysUntil(value: string | null): number | null {
  if (!value) return null;
  const d = new Date(value);
  if (isNaN(d.getTime())) return null;
  const ms = d.getTime() - new Date().setHours(0, 0, 0, 0);
  return Math.round(ms / 86400000);
}

export function deadlineLabel(value: string | null): string {
  const days = daysUntil(value);
  if (days === null) return "No deadline";
  if (days < 0) return "Closed";
  if (days === 0) return "Due today";
  if (days === 1) return "1 day left";
  return `${days} days left`;
}

export function scoreColor(score: number): string {
  if (score >= 70) return "bg-emerald-100 text-emerald-800 border-emerald-200";
  if (score >= 40) return "bg-amber-100 text-amber-800 border-amber-200";
  return "bg-slate-100 text-slate-600 border-slate-200";
}

const STATUS_COLORS: Record<string, string> = {
  new: "bg-slate-100 text-slate-700",
  reviewing: "bg-blue-100 text-blue-700",
  maybe: "bg-indigo-100 text-indigo-700",
  pitched: "bg-violet-100 text-violet-700",
  submitted: "bg-amber-100 text-amber-700",
  won: "bg-emerald-100 text-emerald-700",
  lost: "bg-rose-100 text-rose-700",
  ignored: "bg-slate-200 text-slate-500",
};

export function statusColor(status: string): string {
  return STATUS_COLORS[status] || "bg-slate-100 text-slate-700";
}

export function titleCase(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
