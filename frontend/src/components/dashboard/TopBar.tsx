import { KPIS } from "@/lib/incidents-data";

export function TopBar() {
  return (
    <header data-annotate="topbar" className="h-14 border-b border-border-dim bg-background flex items-center justify-between px-6 shrink-0 relative">
      <div className="flex items-center gap-6">
        <div
          className="px-2.5 py-1 font-mono font-bold text-[13px] rounded-sm tracking-[0.12em] uppercase text-background logo-shimmer"
        >
          Boogle
        </div>
        <style>{`
          .logo-shimmer {
            background: linear-gradient(
              105deg,
              #ffffff 0%,
              #ffffff 35%,
              #c0c0c0 45%,
              #f8f8f8 50%,
              #ffffff 55%,
              #ffffff 100%
            );
            background-size: 300% 100%;
            animation: shimmer 2.4s ease-in-out infinite;
          }
          @keyframes shimmer {
            0%   { background-position: 200% center; }
            100% { background-position: -200% center; }
          }
        `}</style>

        <div className="flex items-center text-[11px] font-mono">
          <KPI label="Critical" value={KPIS.critical.toString()} tone="critical" />
          <Divider />
          <KPI label="Total findings" value={KPIS.total_findings.toString()} />
          <Divider />
          <KPI label="Avg confidence" value={`${KPIS.avg_confidence}%`} tone="success" />
        </div>
      </div>

    </header>
  );
}

function KPI({ label, value, tone }: { label: string; value: string; tone?: "critical" | "success" }) {
  const toneClass = tone === "critical" ? "text-critical" : tone === "success" ? "text-success" : "text-foreground";
  return (
    <div className="flex items-center gap-2.5">
      <span className="uppercase tracking-widest text-[10px] text-muted-foreground/80">{label}</span>
      <span className={`font-bold ${toneClass}`}>{value}</span>
    </div>
  );
}

function Divider() {
  return <span className="mx-5 h-3 w-px bg-border-dim" />;
}
