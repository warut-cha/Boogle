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

export function AttackPath({ incident }: { incident: Incident }) {
  const { nodes, criticalNodeId } = incident.path;

  return (
    <section data-annotate="attackpath" className="border border-border-dim bg-surface/40">
      <header className="px-5 h-11 border-b border-border-dim flex items-center justify-between">
        <h2 className="text-[11px] font-bold uppercase tracking-[0.18em] text-muted-foreground font-mono">
          Attack Vector Topology
        </h2>
        <button className="text-[10px] text-accent hover:underline tracking-widest font-mono uppercase">
          Expand Graph →
        </button>
      </header>

      <div className="p-8">
        <div className="relative flex items-center justify-between">
          <div className="absolute top-6 left-0 right-0 h-px bg-border-dim mx-12 z-0" />

          {nodes.map((node) => {
            const isCritical = node.id === criticalNodeId;
            const isImpact = node.type === "impact";
            return (
              <div key={node.id} className="relative z-10 flex flex-col items-center gap-3 group">
                <div
                  className={cn(
                    "size-12 rounded-sm border-2 grid place-items-center bg-background transition-colors",
                    isCritical || isImpact
                      ? "border-critical shadow-[0_0_0_4px_color-mix(in_oklab,var(--severity-critical)_8%,transparent)]"
                      : "border-border",
                  )}
                >
                  <span
                    className={cn(
                      "font-mono text-[8px] font-bold tracking-tight",
                      isCritical || isImpact ? "text-critical" : "text-muted-foreground",
                    )}
                  >
                    {NODE_LABEL[node.type]}
                  </span>
                </div>
                <div className="text-center max-w-[120px]">
                  <div className="font-semibold text-[11px] text-foreground leading-tight">
                    {node.label}
                  </div>
                  <div className="text-[10px] text-muted-foreground font-mono mt-0.5 truncate">
                    {node.detail}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
