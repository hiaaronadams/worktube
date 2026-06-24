import { scoreColor, statusColor, titleCase } from "@/lib/format";

export function ScoreBadge({
  score,
  label = "fit",
}: {
  score: number;
  label?: string;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-xs font-semibold tabular-nums ${scoreColor(
        score
      )}`}
      title={`${label} score`}
    >
      {Math.round(score)}
      <span className="font-normal opacity-70">{label}</span>
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${statusColor(
        status
      )}`}
    >
      {titleCase(status)}
    </span>
  );
}

export function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center rounded bg-slate-100 px-1.5 py-0.5 text-[11px] font-medium text-slate-600">
      {typeof children === "string" ? titleCase(children) : children}
    </span>
  );
}
