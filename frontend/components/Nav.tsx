"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/opportunities", label: "Opportunities" },
  { href: "/saved", label: "Saved" },
  { href: "/pipeline", label: "Pipeline" },
];

export default function Nav() {
  const pathname = usePathname();
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center gap-6 px-6 py-3">
        <Link href="/opportunities" className="flex items-center gap-2">
          <span className="grid h-7 w-7 place-items-center rounded-md bg-tomato-500 text-sm font-bold text-white">
            W
          </span>
          <span className="text-lg font-semibold tracking-tight">Worktube</span>
        </Link>
        <nav className="flex items-center gap-1 text-sm">
          {LINKS.map((l) => {
            const active = pathname === l.href || pathname.startsWith(l.href + "/");
            return (
              <Link
                key={l.href}
                href={l.href}
                className={`rounded-md px-3 py-1.5 font-medium transition ${
                  active
                    ? "bg-tomato-50 text-tomato-700"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                {l.label}
              </Link>
            );
          })}
        </nav>
        <div className="ml-auto text-xs text-slate-400">RFP Aggregator</div>
      </div>
    </header>
  );
}
