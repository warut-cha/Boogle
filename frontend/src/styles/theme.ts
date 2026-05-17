/**
 * IBM Bob Dashboard - Design System Theme
 * Professional color palette, typography, and spacing tokens
 */

export const theme = {
  // Color Palette - IBM Carbon Design System Inspired
  colors: {
    // Primary Colors
    primary: {
      50: '#e5f0ff',
      100: '#bdd9ff',
      200: '#8fc1ff',
      300: '#5fa9ff',
      400: '#3396ff',
      500: '#0f62fe', // Main primary
      600: '#0353e9',
      700: '#0043ce',
      800: '#0033b3',
      900: '#001d6c',
    },
    
    // Success Colors
    success: {
      50: '#e5f6ed',
      100: '#b8e8cc',
      200: '#8cd9a9',
      300: '#5fcb86',
      400: '#3ebf6b',
      500: '#24a148', // Main success
      600: '#1f9340',
      700: '#198038',
      800: '#146d30',
      900: '#0b4d21',
    },
    
    // Warning Colors
    warning: {
      50: '#fef7e5',
      100: '#fdeabd',
      200: '#fcdd91',
      300: '#fbd065',
      400: '#fac645',
      500: '#f1c21b', // Main warning
      600: '#e0b317',
      700: '#cda013',
      800: '#ba8e0f',
      900: '#996f08',
    },
    
    // Error Colors
    error: {
      50: '#fce8e8',
      100: '#f7c5c5',
      200: '#f29f9f',
      300: '#ed7979',
      400: '#e95c5c',
      500: '#da1e28', // Main error
      600: '#c21e26',
      700: '#a2191f',
      800: '#82151a',
      900: '#5a0a0d',
    },
    
    // Neutral Grays
    gray: {
      50: '#f9fafb',
      100: '#f4f4f4',
      200: '#e0e0e0',
      300: '#c6c6c6',
      400: '#a8a8a8',
      500: '#8d8d8d',
      600: '#6f6f6f',
      700: '#525252',
      800: '#393939',
      900: '#161616',
    },
    
    // Semantic Colors
    background: {
      primary: '#ffffff',
      secondary: '#f4f4f4',
      tertiary: '#e0e0e0',
      dark: '#161616',
      overlay: 'rgba(22, 22, 22, 0.5)',
    },
    
    text: {
      primary: '#161616',
      secondary: '#525252',
      tertiary: '#8d8d8d',
      inverse: '#ffffff',
      link: '#0f62fe',
      disabled: '#c6c6c6',
    },
    
    border: {
      subtle: '#e0e0e0',
      strong: '#8d8d8d',
      inverse: '#ffffff',
      interactive: '#0f62fe',
    },
  },
  
  // Typography
  typography: {
    fontFamily: {
      sans: "'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
      mono: "'IBM Plex Mono', 'Courier New', Courier, monospace",
    },
    
    fontSize: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      base: '1rem',     // 16px
      lg: '1.125rem',   // 18px
      xl: '1.25rem',    // 20px
      '2xl': '1.5rem',  // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem', // 36px
      '5xl': '3rem',    // 48px
    },
    
    fontWeight: {
      light: 300,
      regular: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75,
      loose: 2,
    },
    
    letterSpacing: {
      tight: '-0.025em',
      normal: '0',
      wide: '0.025em',
      wider: '0.05em',
      widest: '0.1em',
    },
  },
  
  // Spacing (8px base unit)
  spacing: {
    0: '0',
    1: '0.25rem',  // 4px
    2: '0.5rem',   // 8px
    3: '0.75rem',  // 12px
    4: '1rem',     // 16px
    5: '1.25rem',  // 20px
    6: '1.5rem',   // 24px
    8: '2rem',     // 32px
    10: '2.5rem',  // 40px
    12: '3rem',    // 48px
    16: '4rem',    // 64px
    20: '5rem',    // 80px
    24: '6rem',    // 96px
  },
  
  // Border Radius
  borderRadius: {
    none: '0',
    sm: '0.25rem',   // 4px
    base: '0.5rem',  // 8px
    md: '0.75rem',   // 12px
    lg: '1rem',      // 16px
    xl: '1.5rem',    // 24px
    full: '9999px',
  },
  
  // Shadows
  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 2px 4px 0 rgba(0, 0, 0, 0.1)',
    md: '0 4px 8px 0 rgba(0, 0, 0, 0.12)',
    lg: '0 8px 16px 0 rgba(0, 0, 0, 0.15)',
    xl: '0 12px 24px 0 rgba(0, 0, 0, 0.18)',
    '2xl': '0 16px 32px 0 rgba(0, 0, 0, 0.2)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
  },
  
  // Transitions
  transitions: {
    fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
    base: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '500ms cubic-bezier(0.4, 0, 0.2, 1)',
    bounce: '500ms cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  },
  
  // Z-Index
  zIndex: {
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modalBackdrop: 1040,
    modal: 1050,
    popover: 1060,
    tooltip: 1070,
  },
  
  // Breakpoints
  breakpoints: {
    xs: '320px',
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
} as const;

// Gradient Utilities
export const gradients = {
  primary: 'linear-gradient(135deg, #0f62fe 0%, #0043ce 100%)',
  success: 'linear-gradient(135deg, #24a148 0%, #198038 100%)',
  warning: 'linear-gradient(135deg, #f1c21b 0%, #cda013 100%)',
  error: 'linear-gradient(135deg, #da1e28 0%, #a2191f 100%)',
  dark: 'linear-gradient(135deg, #161616 0%, #262626 100%)',
  light: 'linear-gradient(135deg, #ffffff 0%, #f4f4f4 100%)',
  glass: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
};

// Helper function to get severity color
export const getSeverityColor = (severity: string): string => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return theme.colors.error[500];
    case 'high':
      return theme.colors.error[400];
    case 'medium':
      return theme.colors.warning[500];
    case 'low':
      return theme.colors.primary[500];
    default:
      return theme.colors.gray[500];
  }
};

// Helper function to get severity gradient
export const getSeverityGradient = (severity: string): string => {
  switch (severity.toLowerCase()) {
    case 'critical':
    case 'high':
      return gradients.error;
    case 'medium':
      return gradients.warning;
    case 'low':
      return gradients.primary;
    default:
      return gradients.dark;
  }
};

export type Theme = typeof theme;

// Made with Bob
