import bobImg from "@/assets/bob-character.png";

/**
 * Ambient BOB — visible but blended. Sits in the bottom-right corner as
 * low-contrast background telemetry: cyan-tinted, slightly blurred, with a
 * subtle head-bob and a faint cyan scan sweep. Not interactive.
 */
export function BobInspector() {
  return (
    <div
      aria-hidden
      className="pointer-events-none fixed bottom-2 right-3 z-0 select-none"
    >
      <div
        className="relative w-[120px] h-[150px] overflow-hidden opacity-50 hover:opacity-90 transition-opacity duration-500"
        style={{ filter: "grayscale(0.6) contrast(0.95) brightness(1.05) drop-shadow(0 0 14px color-mix(in oklab, var(--severity-info) 35%, transparent))" }}
      >
        <div className="bob-bob absolute inset-0 grid place-items-end">
          <img src={bobImg} alt="" className="w-[110px] h-[140px] object-contain" />
        </div>
        {/* faint cyan scan sweep over him */}
        <div className="absolute inset-x-0 h-px bg-info/70 scan-beam" style={{ boxShadow: "0 0 8px var(--severity-info)" }} />
      </div>

      <style>{`
        @keyframes bob-head {
          0%,100% { transform: translateY(0) rotate(-1deg); }
          25%     { transform: translateY(-3px) rotate(1deg); }
          50%     { transform: translateY(1px) rotate(0deg); }
          75%     { transform: translateY(-1px) rotate(-0.5deg); }
        }
        .bob-bob { animation: bob-head 2.8s ease-in-out infinite; transform-origin: bottom center; }
        @keyframes scan-beam {
          0%   { top: 0; opacity: 0; }
          20%  { opacity: 1; }
          80%  { opacity: 1; }
          100% { top: 100%; opacity: 0; }
        }
        .scan-beam { animation: scan-beam 3.2s linear infinite; }
      `}</style>
    </div>
  );
}
