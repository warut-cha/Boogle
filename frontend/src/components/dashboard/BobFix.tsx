import type { Incident } from "@/lib/incidents-data";

export function BobFix({ incident }: { incident: Incident }) {
  const { bob } = incident;
  return (
    <section data-annotate="bobfix" className="border border-border-dim bg-surface/40 flex flex-col">
      <header className="px-5 h-11 border-b border-border-dim flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="size-4 bg-info grid place-items-center rounded-sm">
            <span className="text-white font-mono text-[9px] font-bold">B</span>
          </div>
          <h2 className="text-[11px] font-bold uppercase tracking-[0.18em] text-muted-foreground font-mono">
            Bob · Mitigation Protocol
          </h2>
        </div>
        <span className="text-[10px] font-mono text-info">▲ ready</span>
      </header>

      <div className="p-5 space-y-4 flex-1 overflow-y-auto">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-[10px] uppercase tracking-widest text-muted-foreground/70 font-mono mb-1">
              Attack type
            </div>
            <div className="text-[12px] text-foreground font-medium">{bob.attack_type}</div>
          </div>
          <div>
            <div className="text-[10px] uppercase tracking-widest text-muted-foreground/70 font-mono mb-1">
              Target
            </div>
            <div className="text-[12px] text-foreground font-mono truncate">{bob.target}</div>
          </div>
        </div>

        <p className="text-[12px] leading-relaxed text-foreground/85">{bob.summary}</p>

        <div className="border-l-2 border-info pl-3 py-1">
          <div className="text-[10px] uppercase tracking-widest text-info/80 font-mono mb-0.5">
            Immediate action
          </div>
          <div className="text-[12px] text-foreground">{bob.immediate_action}</div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] uppercase tracking-widest text-muted-foreground/70 font-mono">
              Patch
            </span>
            <span className="text-[10px] font-mono text-muted-foreground/70 truncate ml-2">
              {bob.file_path}
            </span>
          </div>
          <pre className="bg-background border border-border-dim p-3 text-[11px] font-mono leading-relaxed overflow-x-auto">
            {bob.code_diff.removed.map((l, i) => (
              <div key={`r-${i}`} className="text-critical/90">
                <span className="text-muted-foreground/50 select-none mr-2">-</span>
                {l}
              </div>
            ))}
            {bob.code_diff.added.map((l, i) => (
              <div key={`a-${i}`} className="text-success">
                <span className="text-muted-foreground/50 select-none mr-2">+</span>
                {l}
              </div>
            ))}
          </pre>
        </div>

        <button className="w-full mt-2 py-2 bg-info hover:bg-info/90 text-white text-[10px] font-bold uppercase tracking-widest font-mono transition-colors">
          Apply Fix Package
        </button>
      </div>
    </section>
  );
}
