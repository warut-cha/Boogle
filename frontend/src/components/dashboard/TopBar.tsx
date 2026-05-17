import { KPIS } from "@/lib/incidents-data";

export function TopBar() {
  return (
    <header data-annotate="topbar" className="h-14 border-b border-border-dim bg-background flex items-center justify-between px-6 shrink-0 relative">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2.5">
          <div className="size-6 grid place-items-center bg-foreground text-background font-mono font-bold text-[11px] rounded-sm">
            S
          </div>
          <span className="font-mono text-[11px] uppercase tracking-[0.18em] font-bold">Sentinel</span>
        </div>

        <div className="flex items-center text-[11px] font-mono">
          <KPI label="Critical" value={KPIS.critical.toString()} tone="critical" />
          <Divider />
          <KPI label="Total findings" value={KPIS.total_findings.toString()} />
          <Divider />
          <KPI label="Avg confidence" value={`${KPIS.avg_confidence}%`} tone="success" />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button className="px-3 py-1.5 text-[10px] font-mono uppercase tracking-widest text-muted-foreground hover:text-foreground border border-border-dim hover:border-border transition-colors">
          Export Case
        </button>
        <button className="px-3 py-1.5 text-[10px] font-mono uppercase tracking-widest bg-foreground text-background hover:bg-foreground/90 transition-colors">
          Scan Infra
        </button>
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
