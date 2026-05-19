import type { Incident } from "@/lib/incidents-data";
import { severityToken } from "./severity";
import { AttackPath } from "./AttackPath";
import { BobFix } from "./BobFix";
import { EvidenceTable } from "./EvidenceTable";
import { cn } from "@/lib/utils";

export function IncidentMainStage({ incident }: { incident: Incident }) {
  const sev = severityToken[incident.severity];

  return (
    <div key={incident.id} className="flex-1 overflow-y-auto animate-incident-fade">
      <section data-annotate="hero" className="px-8 pt-8 pb-6 border-b border-border-dim bg-surface/50">
        <div className="max-w-[1280px] mx-auto">
          <div className="flex items-center gap-3 mb-2">
            <div className={cn("size-2.5 rounded-sm", sev.dot)} />
            <span className="font-mono text-[10px] text-muted-foreground tracking-widest uppercase">
              {incident.id}
            </span>
            <span className="text-muted-foreground/40">·</span>
            <span className="font-mono text-[10px] text-muted-foreground tracking-widest">
              {incident.region}
            </span>
          </div>
          <h1 className="text-[22px] font-semibold text-foreground tracking-tight mb-6 text-balance">
            {incident.title}
          </h1>

          <div className="grid grid-cols-4 gap-3">
            <Stat
              label="Severity"
              value={`${sev.label} (${incident.severity_score.toFixed(1)})`}
              valueClass={cn(sev.text, "italic")}
            />
            <Stat
              label="Confidence"
              value={`${(incident.confidence * 100).toFixed(1)}%`}
              valueClass="text-accent"
              mono
            />
            <Stat label="First observed" value={incident.detected_at} mono small />
            <Stat label="Impacted nodes" value={`${incident.impacted_nodes} units`} />
          </div>
        </div>
      </section>

      <div className="px-8 py-6 max-w-[1280px] mx-auto w-full space-y-5">
        <AttackPath incident={incident} />

        <div className="grid grid-cols-2 gap-5 min-h-[420px]">
          <BobFix incident={incident} />
          <EvidenceTable incident={incident} />
        </div>

        {incident.affected_repos.length > 0 && (
          <div className="flex items-center gap-4 pt-2 text-[11px] font-mono text-muted-foreground">
            <span className="uppercase tracking-widest">Affected repos:</span>
            {incident.affected_repos.map((r) => (
              <span key={r} className="px-2 py-0.5 border border-border-dim text-foreground/80">
                {r}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function Stat({
  label,
  value,
  valueClass,
  mono,
  small,
}: {
  label: string;
  value: string;
  valueClass?: string;
  mono?: boolean;
  small?: boolean;
}) {
  return (
    <div className="p-3.5 border border-border-dim bg-white/[0.015]">
      <div className="text-[9px] uppercase tracking-[0.18em] text-muted-foreground/70 font-mono mb-1.5">
        {label}
      </div>
      <div
        className={cn(
          "font-bold tracking-tight",
          small ? "text-[13px]" : "text-[18px]",
          mono && "font-mono",
          valueClass ?? "text-foreground",
        )}
      >
        {value}
      </div>
    </div>
  );
}
