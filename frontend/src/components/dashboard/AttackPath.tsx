import { useState } from "react";
import type { Incident, NodeType } from "@/lib/incidents-data";
import { cn } from "@/lib/utils";

const NODE_LABEL: Record<NodeType, string> = {
  secret: "SECRET",
  api: "API",
  runtime: "RUNTIME",
  database: "STORAGE",
  infrastructure: "INFRA",
  impact: "IMPACT",
};

const NODE_COLOR: Record<NodeType, string> = {
  secret: "border-yellow-500 text-yellow-400",
  api: "border-blue-500 text-blue-400",
  runtime: "border-purple-500 text-purple-400",
  database: "border-emerald-500 text-emerald-400",
  infrastructure: "border-slate-400 text-slate-300",
  impact: "border-critical text-critical",
};

function GraphNodes({ incident, large }: { incident: Incident; large?: boolean }) {
  const { nodes, criticalNodeId } = incident.path;

  return (
    <div className="relative flex items-center justify-between">
      <div className={cn("absolute top-6 left-0 right-0 h-px bg-border-dim z-0", large ? "mx-16" : "mx-12")} />

      {nodes.map((node, idx) => {
        const isCritical = node.id === criticalNodeId;
        const isImpact = node.type === "impact";
        const colorClass = NODE_COLOR[node.type] ?? "border-border text-muted-foreground";

        return (
          <div key={node.id} className="relative z-10 flex flex-col items-center gap-3 group">
            {idx < nodes.length - 1 && (
              <div className={cn(
                "absolute left-[calc(100%+4px)] top-5 font-mono z-20 pointer-events-none",
                large ? "text-[9px]" : "text-[8px]",
                "text-muted-foreground/50 whitespace-nowrap",
              )}>
                →
              </div>
            )}
            <div
              className={cn(
                "border-2 grid place-items-center bg-background transition-colors rounded-sm",
                large ? "size-16" : "size-12",
                isCritical || isImpact
                  ? "border-critical shadow-[0_0_0_4px_color-mix(in_oklab,var(--severity-critical)_8%,transparent)]"
                  : colorClass.split(" ")[0],
              )}
            >
              <span
                className={cn(
                  "font-mono font-bold tracking-tight",
                  large ? "text-[9px]" : "text-[8px]",
                  isCritical || isImpact ? "text-critical" : colorClass.split(" ")[1],
                )}
              >
                {NODE_LABEL[node.type] ?? node.type.toUpperCase()}
              </span>
            </div>
            <div className={cn("text-center", large ? "max-w-[160px]" : "max-w-[120px]")}>
              <div className={cn("font-semibold text-foreground leading-tight", large ? "text-[13px]" : "text-[11px]")}>
                {node.label}
              </div>
              <div className={cn("text-muted-foreground font-mono mt-0.5 truncate", large ? "text-[11px]" : "text-[10px]")}>
                {node.detail}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function AttackPath({ incident }: { incident: Incident }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <>
      <section data-annotate="attackpath" className="border border-border-dim bg-surface/40">
        <header className="px-5 h-11 border-b border-border-dim flex items-center justify-between">
          <h2 className="text-[11px] font-bold uppercase tracking-[0.18em] text-muted-foreground font-mono">
            Attack Vector Topology
          </h2>
          <button
            onClick={() => setExpanded(true)}
            className="text-[10px] text-accent hover:underline tracking-widest font-mono uppercase"
          >
            Expand Graph →
          </button>
        </header>

        <div className="p-8">
          <GraphNodes incident={incident} />
        </div>
      </section>

      {expanded && (
        <div
          className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-8"
          onClick={() => setExpanded(false)}
        >
          <div
            className="bg-background border border-border w-full max-w-5xl rounded-sm p-10 relative"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-[11px] font-bold uppercase tracking-[0.18em] text-muted-foreground font-mono mb-1">
                  Attack Vector Topology
                </h2>
                <p className="text-[13px] font-semibold text-foreground">{incident.title}</p>
              </div>
              <button
                onClick={() => setExpanded(false)}
                className="text-[10px] font-mono tracking-widest uppercase text-muted-foreground hover:text-foreground border border-border-dim px-3 py-1.5"
              >
                Close ✕
              </button>
            </div>

            <GraphNodes incident={incident} large />

            <div className="mt-8 pt-6 border-t border-border-dim grid grid-cols-3 gap-4">
              {incident.path.nodes.map((node) => (
                <div key={node.id} className="p-3 border border-border-dim bg-surface/40">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={cn(
                      "font-mono text-[9px] font-bold px-1.5 py-0.5 border",
                      NODE_COLOR[node.type]?.split(" ")[0] ?? "border-border",
                      NODE_COLOR[node.type]?.split(" ")[1] ?? "text-muted-foreground",
                    )}>
                      {NODE_LABEL[node.type] ?? node.type}
                    </span>
                    <span className="text-[11px] font-semibold text-foreground">{node.label}</span>
                  </div>
                  <p className="text-[10px] font-mono text-muted-foreground">{node.detail}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
