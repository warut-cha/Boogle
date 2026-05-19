import type { Severity } from "@/lib/incidents-data";

export const severityToken: Record<Severity, { text: string; bg: string; ring: string; dot: string; label: string }> = {
  critical: { text: "text-critical", bg: "bg-critical/10", ring: "ring-critical/30", dot: "bg-critical", label: "Critical" },
  high: { text: "text-high", bg: "bg-high/10", ring: "ring-high/30", dot: "bg-high", label: "High" },
  medium: { text: "text-medium", bg: "bg-medium/10", ring: "ring-medium/30", dot: "bg-medium", label: "Medium" },
  low: { text: "text-muted-foreground", bg: "bg-muted/40", ring: "ring-border", dot: "bg-muted-foreground", label: "Low" },
};
