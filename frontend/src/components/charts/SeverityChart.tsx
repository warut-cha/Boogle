import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import type { Finding } from '../../api/types';
import { theme, getSeverityColor } from '../../styles/theme';

interface SeverityChartProps {
  findings: Finding[];
}

export default function SeverityChart({ findings }: SeverityChartProps) {
  // Count findings by severity
  const severityCounts = findings.reduce((acc, finding) => {
    const severity = finding.severity_hint || 'unknown';
    acc[severity] = (acc[severity] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // Convert to chart data format
  const data = Object.entries(severityCounts).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
    color: getSeverityColor(name),
  }));

  // Sort by severity (critical > high > medium > low)
  const severityOrder = ['critical', 'high', 'medium', 'low', 'unknown'];
  data.sort((a, b) => {
    const aIndex = severityOrder.indexOf(a.name.toLowerCase());
    const bIndex = severityOrder.indexOf(b.name.toLowerCase());
    return aIndex - bIndex;
  });

  if (findings.length === 0) {
    return (
      <div
        style={{
          backgroundColor: theme.colors.background.primary,
          border: `1px solid ${theme.colors.border.subtle}`,
          borderRadius: theme.borderRadius.base,
          padding: theme.spacing[8],
          textAlign: 'center',
          boxShadow: theme.shadows.base,
        }}
      >
        <p style={{ 
          color: theme.colors.text.secondary,
          fontSize: theme.typography.fontSize.sm,
          margin: 0,
        }}>
          No data to display
        </p>
      </div>
    );
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div
          style={{
            backgroundColor: theme.colors.background.primary,
            border: `1px solid ${theme.colors.border.subtle}`,
            borderRadius: theme.borderRadius.sm,
            padding: theme.spacing[3],
            boxShadow: theme.shadows.md,
          }}
        >
          <p style={{ 
            margin: 0,
            fontSize: theme.typography.fontSize.sm,
            fontWeight: theme.typography.fontWeight.semibold,
            color: theme.colors.text.primary,
          }}>
            {payload[0].name}: {payload[0].value}
          </p>
          <p style={{ 
            margin: `${theme.spacing[1]} 0 0 0`,
            fontSize: theme.typography.fontSize.xs,
            color: theme.colors.text.secondary,
          }}>
            {((payload[0].value / findings.length) * 100).toFixed(1)}% of total
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div
      className="animate-fade-in"
      style={{
        backgroundColor: theme.colors.background.primary,
        border: `1px solid ${theme.colors.border.subtle}`,
        borderRadius: theme.borderRadius.base,
        padding: theme.spacing[6],
        boxShadow: theme.shadows.md,
      }}
    >
      <h3
        style={{
          fontSize: theme.typography.fontSize.lg,
          fontWeight: theme.typography.fontWeight.semibold,
          color: theme.colors.text.primary,
          marginBottom: theme.spacing[4],
          display: 'flex',
          alignItems: 'center',
          gap: theme.spacing[2],
        }}
      >
        📊 Severity Distribution
      </h3>

      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
            animationBegin={0}
            animationDuration={800}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>

      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          gap: theme.spacing[4],
          marginTop: theme.spacing[4],
          flexWrap: 'wrap',
        }}
      >
        {data.map((entry) => (
          <div
            key={entry.name}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: theme.spacing[2],
            }}
          >
            <div
              style={{
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                backgroundColor: entry.color,
              }}
            />
            <span
              style={{
                fontSize: theme.typography.fontSize.sm,
                color: theme.colors.text.secondary,
              }}
            >
              {entry.name}: {entry.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Made with Bob
