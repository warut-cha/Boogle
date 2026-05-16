export const SEVERITY_COLORS: Record<string, string> = {
  critical: '#f85149',
  high: '#e3b341',
  medium: '#d29922',
  low: '#58a6ff',
  info: '#8b949e',
};

export const getSeverityColor = (severity: string): string =>
  SEVERITY_COLORS[severity] ?? '#8b949e';

export const SEVERITY_ORDER: Record<string, number> = {
  critical: 5,
  high: 4,
  medium: 3,
  low: 2,
  info: 1,
};

// Made with Bob
