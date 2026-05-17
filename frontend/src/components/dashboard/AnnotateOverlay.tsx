import { useEffect, useLayoutEffect, useState } from "react";
import { REGION_META, type AnnotateRegion } from "./annotate-context";

interface Rect { region: AnnotateRegion; x: number; y: number; w: number; h: number; }

/**
 * Click-driven HUD. Click any [data-annotate] region to mark it with
 * L-brackets + 9% color fill + a tiny label. No page dim, no number plate.
 * Click the same region again, click outside, or press ESC to clear.
 */
export function AnnotateOverlay() {
  const [selected, setSelected] = useState<AnnotateRegion | null>(null);
  const [rects, setRects] = useState<Rect[]>([]);

  useLayoutEffect(() => {
    const measure = () => {
      const next: Rect[] = [];
      document.querySelectorAll<HTMLElement>("[data-annotate]").forEach((el) => {
        const region = el.dataset.annotate as AnnotateRegion;
        if (!REGION_META[region]) return;
        const r = el.getBoundingClientRect();
        next.push({ region, x: r.left, y: r.top, w: r.width, h: r.height });
      });
      setRects(next);
    };
    measure();
    const ro = new ResizeObserver(measure);
    document.querySelectorAll("[data-annotate]").forEach((el) => ro.observe(el));
    window.addEventListener("scroll", measure, true);
    window.addEventListener("resize", measure);
    return () => {
      ro.disconnect();
      window.removeEventListener("scroll", measure, true);
      window.removeEventListener("resize", measure);
    };
  }, []);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      const target = (e.target as HTMLElement | null)?.closest<HTMLElement>("[data-annotate]");
      if (!target) {
        setSelected(null);
        return;
      }
      const region = target.dataset.annotate as AnnotateRegion;
      if (!REGION_META[region]) return;
      setSelected((curr) => (curr === region ? null : region));
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setSelected(null);
    };
    document.addEventListener("click", onClick);
    window.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("click", onClick);
      window.removeEventListener("keydown", onKey);
    };
  }, []);

  if (!selected) return null;
  const r = rects.find((x) => x.region === selected);
  if (!r) return null;
  const meta = REGION_META[selected];

  return (
    <div className="fixed inset-0 z-50 pointer-events-none">
      <div
        className="absolute transition-all duration-200"
        style={{ left: r.x, top: r.y, width: r.w, height: r.h }}
      >
        <div
          className="absolute inset-0"
          style={{ background: `color-mix(in oklab, ${meta.cssVar} 9%, transparent)` }}
        />
        <Bracket pos="tl" color={meta.cssVar} />
        <Bracket pos="tr" color={meta.cssVar} />
        <Bracket pos="bl" color={meta.cssVar} />
        <Bracket pos="br" color={meta.cssVar} />
        <div
          className="absolute top-2 left-2 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-[0.18em] font-bold bg-background/85"
          style={{ color: meta.cssVar, border: `1px solid ${meta.cssVar}` }}
        >
          {meta.label}
        </div>
      </div>
    </div>
  );
}

function Bracket({ pos, color }: { pos: "tl" | "tr" | "bl" | "br"; color: string }) {
  const len = 28;
  const w = 3;
  const horiz: React.CSSProperties = { position: "absolute", width: len, height: w, background: color };
  const vert: React.CSSProperties = { position: "absolute", width: w, height: len, background: color };
  const map: Record<typeof pos, { h: React.CSSProperties; v: React.CSSProperties }> = {
    tl: { h: { ...horiz, top: 0, left: 0 }, v: { ...vert, top: 0, left: 0 } },
    tr: { h: { ...horiz, top: 0, right: 0 }, v: { ...vert, top: 0, right: 0 } },
    bl: { h: { ...horiz, bottom: 0, left: 0 }, v: { ...vert, bottom: 0, left: 0 } },
    br: { h: { ...horiz, bottom: 0, right: 0 }, v: { ...vert, bottom: 0, right: 0 } },
  };
  return (
    <>
      <span style={map[pos].h} />
      <span style={map[pos].v} />
    </>
  );
}
