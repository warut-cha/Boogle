import { createContext, useContext, useState, type ReactNode } from "react";

export type AnnotateRegion = "topbar" | "sidebar" | "hero" | "attackpath" | "bobfix" | "evidence";

export const REGION_META: Record<
  AnnotateRegion,
  { num: string; label: string; sub: string; color: string; cssVar: string }
> = {
  topbar:     { num: "01", label: "TOPBAR",      sub: "56px · global KPI strip · case actions", color: "cyan",    cssVar: "oklch(0.78 0.14 200)" },
  sidebar:    { num: "02", label: "INCIDENT FEED", sub: "300px · live triage queue · 3 active", color: "amber",   cssVar: "oklch(0.78 0.16 70)" },
  hero:       { num: "03", label: "INCIDENT HERO", sub: "ID · region · 4 KPI · severity tint", color: "rose",    cssVar: "oklch(0.68 0.22 18)" },
  attackpath: { num: "04", label: "ATTACK TOPOLOGY", sub: "5-node killchain · critical halo on RUN/IMPACT", color: "violet", cssVar: "oklch(0.7 0.18 295)" },
  bobfix:     { num: "05", label: "BOB · FIX",   sub: "AI mitigation · code diff · apply patch", color: "info",   cssVar: "oklch(0.7 0.18 250)" },
  evidence:   { num: "06", label: "EVIDENCE",    sub: "correlated artifacts · severity bars · 5 events", color: "green", cssVar: "oklch(0.72 0.16 145)" },
};

interface Ctx { active: boolean; toggle: () => void; }
const AnnotateCtx = createContext<Ctx>({ active: false, toggle: () => {} });

export function AnnotateProvider({ children }: { children: ReactNode }) {
  const [active, setActive] = useState(false);
  return (
    <AnnotateCtx.Provider value={{ active, toggle: () => setActive((a) => !a) }}>
      {children}
    </AnnotateCtx.Provider>
  );
}

export const useAnnotate = () => useContext(AnnotateCtx);
