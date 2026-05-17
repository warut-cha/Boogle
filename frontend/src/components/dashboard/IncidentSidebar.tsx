import { useState } from "react";
import type { Incident } from "@/lib/incidents-data";
import { severityToken } from "./severity";
import { cn } from "@/lib/utils";

interface Props {
  incidents: Incident[];
  selectedId: string;
  onSelect: (id: string) => void;
  newIds?: Set<string>;
  status?: "connecting" | "connected" | "offline";
  onScan?: (path: string) => void;
  onClear?: () => void;
  scanning?: boolean;
}

export function IncidentSidebar({
  incidents,
  selectedId,
  onSelect,
  newIds,
  status = "connected",
  onScan,
  onClear,
  scanning = false,
}: Props) {
  const [scanPath, setScanPath] = useState(".");
  const newCount = newIds?.size ?? 0;
  const dotColor =
    status === "connected" ? "bg-info" : status === "connecting" ? "bg-medium" : "bg-critical";
  const statusLabel =
    status === "connected" ? "Boogle · live" : status === "connecting" ? "Boogle · linking" : "Boogle · offline";
  return (
    <aside data-annotate="sidebar" className="w-[300px] shrink-0 border-r border-border-dim flex flex-col bg-background">
      <div className="px-5 h-14 border-b border-border-dim flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="relative flex size-2">
            {status === "connected" && (
              <span className={cn("absolute inline-flex h-full w-full rounded-full opacity-60 animate-ping", dotColor)} />
            )}
            <span className={cn("relative inline-flex size-2 rounded-full", dotColor)} />
          </span>
          <span className="font-mono text-[11px] font-bold tracking-[0.18em] text-muted-foreground uppercase">
            {statusLabel}
          </span>
        </div>
        <div className="flex items-center gap-2 font-mono text-[10px] text-muted-foreground/70">
          {newCount > 0 && (
            <span className="px-1.5 py-0.5 bg-info/15 text-info border border-info/30 tracking-widest uppercase animate-pulse">
              +{newCount} new
            </span>
          )}
          <span>{incidents.length}</span>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto">
        {incidents.map((inc) => {
          const sev = severityToken[inc.severity];
          const active = inc.id === selectedId;
          const isNew = newIds?.has(inc.id) ?? false;
          return (
            <button
              key={inc.id}
              onClick={() => onSelect(inc.id)}
              className={cn(
                "relative w-full text-left px-4 py-3.5 border-b border-border-dim border-l-2 transition-colors",
                active
                  ? `bg-surface border-l-critical`
                  : "border-l-transparent hover:bg-white/[0.025]",
                active && inc.severity === "high" && "border-l-high",
                active && inc.severity === "medium" && "border-l-medium",
                active && inc.severity === "low" && "border-l-muted-foreground",
                isNew && "incident-new",
              )}
            >
              {isNew && (
                <span className="absolute top-2 right-3 font-mono text-[8.5px] font-bold tracking-widest text-info bg-info/10 border border-info/40 px-1.5 py-0.5 uppercase">
                  New
                </span>
              )}
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-mono text-[10px] text-muted-foreground tracking-wider">{inc.id}</span>
                {!isNew && (
                  <span
                    className={cn(
                      "px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-tight italic",
                      sev.bg,
                      sev.text,
                    )}
                  >
                    {sev.label}
                  </span>
                )}
              </div>
              <h3
                className={cn(
                  "text-[13px] font-medium leading-snug mb-1",
                  active ? "text-foreground" : "text-foreground/80",
                )}
              >
                {inc.title}
              </h3>
              <p className="text-[11px] text-muted-foreground truncate font-mono">
                {inc.origin}
              </p>
              <div className="mt-2.5 flex items-center text-[10px] text-muted-foreground/70 gap-3 font-mono">
                <span>{inc.ago}</span>
                <span>·</span>
                <span>{Math.round(inc.confidence * 100)}% conf</span>
              </div>
            </button>
          );
        })}
      </nav>

      <div className="p-3 border-t border-border-dim flex flex-col gap-2">
        <div className="flex gap-2">
          <input
            type="text"
            value={scanPath}
            onChange={(e) => setScanPath(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !scanning && onScan?.(scanPath)}
            placeholder="/path/to/repo"
            disabled={scanning}
            className="flex-1 min-w-0 bg-transparent border border-border-dim px-2 py-1.5 text-[11px] font-mono text-foreground placeholder:text-muted-foreground/40 focus:outline-none focus:border-border disabled:opacity-40"
          />
          <button
            onClick={() => onScan?.(scanPath)}
            disabled={scanning}
            className="shrink-0 text-[10px] font-mono tracking-widest uppercase transition-colors px-3 py-1.5 border border-border-dim disabled:opacity-40 disabled:cursor-not-allowed hover:enabled:text-foreground hover:enabled:border-border text-muted-foreground"
          >
            {scanning ? "···" : "Scan"}
          </button>
        </div>
        {scanning && (
          <p className="text-[10px] font-mono text-info animate-pulse tracking-widest">
            scanning {scanPath} …
          </p>
        )}
        <button
          onClick={onClear}
          className="col-span-2 text-[10px] font-mono tracking-widest uppercase text-muted-foreground/50 hover:text-muted-foreground transition-colors py-1.5 border border-border-dim/50 hover:border-border-dim"
        >
          Clear All
        </button>
      </div>

      <style>{`
        @keyframes incident-slide-in {
          0%   { opacity: 0; transform: translateY(-8px); background-color: color-mix(in oklab, var(--severity-info) 18%, transparent); }
          60%  { opacity: 1; transform: translateY(0);    background-color: color-mix(in oklab, var(--severity-info) 10%, transparent); }
          100% { background-color: transparent; }
        }
        .incident-new {
          animation: incident-slide-in 1200ms cubic-bezier(0.16, 1, 0.3, 1);
          box-shadow: inset 2px 0 0 var(--severity-info);
        }
      `}</style>
    </aside>
  );
}
