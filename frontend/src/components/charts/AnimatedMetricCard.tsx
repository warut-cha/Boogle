import { useState } from 'react';
import CountUp from 'react-countup';
import type { ReactNode, CSSProperties } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { theme } from '../../styles/theme';

interface AnimatedMetricCardProps {
  icon: ReactNode;
  title: string;
  value: number;
  suffix?: string;
  subtitle?: string;
  color: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

export default function AnimatedMetricCard({
  icon,
  title,
  value,
  suffix = '',
  subtitle,
  color,
  trend,
}: AnimatedMetricCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  const cardStyle: CSSProperties = {
    backgroundColor: theme.colors.background.primary,
    border: `1px solid ${theme.colors.border.subtle}`,
    borderRadius: theme.borderRadius.base,
    padding: theme.spacing[6],
    minHeight: '180px',
    boxShadow: theme.shadows.base,
    transition: `all ${theme.transitions.base}`,
    position: 'relative',
    overflow: 'hidden',
    cursor: 'pointer',
    ...(isHovered ? {
      transform: 'translateY(-4px)',
      boxShadow: theme.shadows.lg,
    } : {}),
  };

  return (
    <div
      style={cardStyle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="animate-scale-in"
    >
      {/* Gradient accent bar */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          background: color,
        }}
      />

      <div style={{ 
        display: 'flex', 
        alignItems: 'flex-start', 
        justifyContent: 'space-between', 
        marginBottom: theme.spacing[4] 
      }}>
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: theme.borderRadius.base,
            background: `${color}15`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: color,
            transition: `all ${theme.transitions.base}`,
            transform: isHovered ? 'scale(1.1) rotate(5deg)' : 'scale(1)',
          }}
        >
          {icon}
        </div>

        {trend && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: theme.spacing[1],
              padding: `${theme.spacing[1]} ${theme.spacing[2]}`,
              borderRadius: theme.borderRadius.sm,
              backgroundColor: trend.isPositive 
                ? `${theme.colors.success[500]}15` 
                : `${theme.colors.error[500]}15`,
              color: trend.isPositive 
                ? theme.colors.success[600] 
                : theme.colors.error[600],
              fontSize: theme.typography.fontSize.xs,
              fontWeight: theme.typography.fontWeight.semibold,
            }}
          >
            {trend.isPositive ? (
              <TrendingUp size={14} />
            ) : (
              <TrendingDown size={14} />
            )}
            {Math.abs(trend.value)}%
          </div>
        )}
      </div>

      <div style={{ marginBottom: theme.spacing[3] }}>
        <div
          style={{
            color: color,
            fontSize: theme.typography.fontSize['4xl'],
            fontWeight: theme.typography.fontWeight.light,
            lineHeight: 1,
            marginBottom: theme.spacing[2],
            fontFamily: theme.typography.fontFamily.sans,
            transition: `all ${theme.transitions.base}`,
            transform: isHovered ? 'scale(1.05)' : 'scale(1)',
          }}
        >
          <CountUp
            end={value}
            duration={2}
            separator=","
            suffix={suffix}
            preserveValue
          />
        </div>
        <div
          style={{
            color: theme.colors.text.primary,
            fontSize: theme.typography.fontSize.sm,
            fontWeight: theme.typography.fontWeight.semibold,
            marginBottom: theme.spacing[1],
            letterSpacing: theme.typography.letterSpacing.wide,
          }}
        >
          {title}
        </div>
      </div>

      {subtitle && (
        <div
          style={{
            color: theme.colors.text.secondary,
            fontSize: theme.typography.fontSize.xs,
            borderTop: `1px solid ${theme.colors.border.subtle}`,
            paddingTop: theme.spacing[3],
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing[2],
          }}
        >
          <span style={{ flex: 1 }}>{subtitle}</span>
        </div>
      )}
    </div>
  );
}

// Made with Bob
