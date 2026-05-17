import type { Incident } from "@/lib/incidents-data";
import { severityToken } from "./severity";
import { cn } from "@/lib/utils";

export function EvidenceTable({ incident }: { incident: Incident }) {
  const findings = incident.findings;
  return (
    <section data-annotate="evidence" className="border border-border-dim bg-surface/40 flex flex-col min-h-0">
      <header className="px-5 h-11 border-b border-border-dim flex items-center justify-between shrink-0">
        <h2 className="text-[11px] font-bold uppercase tracking-[0.18em] text-muted-foreground font-mono">
          Evidence Artifacts
        </h2>
        <span className="text-[10px] font-mono text-muted-foreground/70">{findings.length} events</span>
      </header>

      <div className="flex-1 overflow-y-auto">
        <table className="w-full text-left">
          <thead className="bg-background/60 border-b border-border-dim sticky top-0">
            <tr>
              <th className="px-4 py-2.5 font-mono text-[9px] uppercase tracking-widest text-muted-foreground/80 font-bold">Time</th>
              <th className="px-4 py-2.5 font-mono text-[9px] uppercase tracking-widest text-muted-foreground/80 font-bold">Source</th>
              <th className="px-4 py-2.5 font-mono text-[9px] uppercase tracking-widest text-muted-foreground/80 font-bold">Event</th>
              <th className="px-4 py-2.5 font-mono text-[9px] uppercase tracking-widest text-muted-foreground/80 font-bold">Identity</th>
              <th className="px-4 py-2.5 font-mono text-[9px] uppercase tracking-widest text-muted-foreground/80 font-bold text-right">Severity</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border-dim">
            {findings.map((f) => {
              const sev = severityToken[f.severity];
              return (
                <tr key={f.id} className="hover:bg-white/[0.025] transition-colors">
                  <td className="px-4 py-2.5 font-mono text-[11px] text-muted-foreground">{f.timestamp}</td>
                  <td className="px-4 py-2.5 text-[11px] text-foreground/85">{f.source}</td>
                  <td className="px-4 py-2.5 text-[11px] text-foreground font-medium">{f.event}</td>
                  <td className="px-4 py-2.5 font-mono text-[11px] text-muted-foreground truncate max-w-[180px]">{f.identity}</td>
                  <td className="px-4 py-2.5 text-right">
                    <div className="inline-flex items-center gap-2">
                      <div className={cn("h-1 w-12 rounded-full", sev.bg)}>
                        <div
                          className={cn("h-full rounded-full", sev.dot)}
                          style={{
                            width:
                              f.severity === "critical"
                                ? "100%"
                                : f.severity === "high"
                                ? "70%"
                                : f.severity === "medium"
                                ? "45%"
                                : "20%",
                          }}
                        />
                      </div>
                      <span className={cn("text-[10px] font-mono uppercase tracking-tight", sev.text)}>
                        {sev.label}
                      </span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
