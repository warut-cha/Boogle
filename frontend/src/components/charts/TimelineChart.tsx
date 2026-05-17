import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import type { Finding, Incident } from '../../api/types';
import { theme } from '../../styles/theme';

interface TimelineChartProps {
  findings: Finding[];
  incidents: Incident[];
}

export default function TimelineChart({ findings, incidents }: TimelineChartProps) {
  // Generate mock timeline data (in a real app, this would come from actual timestamps)
  const generateTimelineData = () => {
    const now = new Date();
    const data = [];
    
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000);
      const hour = time.getHours();
      
      // Simulate some activity patterns
      const findingsCount = Math.floor(Math.random() * (findings.length / 4)) + (i < 6 ? findings.length / 6 : 0);
      const incidentsCount = Math.floor(Math.random() * (incidents.length / 4)) + (i < 6 ? incidents.length / 6 : 0);
      
      data.push({
        time: `${hour.toString().padStart(2, '0')}:00`,
        findings: Math.round(findingsCount),
        incidents: Math.round(incidentsCount),
      });
    }
    
    return data;
  };

  const data = generateTimelineData();

  const CustomTooltip = ({ active, payload, label }: any) => {
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
            marginBottom: theme.spacing[2],
          }}>
            {label}
          </p>
          {payload.map((entry: any, index: number) => (
            <p
              key={index}
              style={{
                margin: `${theme.spacing[1]} 0 0 0`,
                fontSize: theme.typography.fontSize.xs,
                color: entry.color,
                display: 'flex',
                alignItems: 'center',
                gap: theme.spacing[2],
              }}
            >
              <span
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: entry.color,
                  display: 'inline-block',
                }}
              />
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (findings.length === 0 && incidents.length === 0) {
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
          No timeline data available
        </p>
      </div>
    );
  }

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
        📈 Detection Timeline (Last 24 Hours)
      </h3>

      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorFindings" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={theme.colors.primary[500]} stopOpacity={0.3}/>
              <stop offset="95%" stopColor={theme.colors.primary[500]} stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorIncidents" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={theme.colors.error[500]} stopOpacity={0.3}/>
              <stop offset="95%" stopColor={theme.colors.error[500]} stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.colors.border.subtle} />
          <XAxis 
            dataKey="time" 
            stroke={theme.colors.text.secondary}
            style={{ fontSize: theme.typography.fontSize.xs }}
          />
          <YAxis 
            stroke={theme.colors.text.secondary}
            style={{ fontSize: theme.typography.fontSize.xs }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="findings"
            stroke={theme.colors.primary[500]}
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorFindings)"
            animationDuration={1000}
          />
          <Area
            type="monotone"
            dataKey="incidents"
            stroke={theme.colors.error[500]}
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorIncidents)"
            animationDuration={1000}
          />
        </AreaChart>
      </ResponsiveContainer>

      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          gap: theme.spacing[6],
          marginTop: theme.spacing[4],
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[2] }}>
          <div
            style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: theme.colors.primary[500],
            }}
          />
          <span style={{ fontSize: theme.typography.fontSize.sm, color: theme.colors.text.secondary }}>
            Findings
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[2] }}>
          <div
            style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: theme.colors.error[500],
            }}
          />
          <span style={{ fontSize: theme.typography.fontSize.sm, color: theme.colors.text.secondary }}>
            Incidents
          </span>
        </div>
      </div>
    </div>
  );
}

// Made with Bob
