// Theme configuration for the application
// Inspired by NY Times minimalist aesthetic

export const themeConfig = {
  // Light theme colors
  light: {
    // Background colors
    background: {
      primary: '#FFFFFF',
      secondary: '#F8F8F8',
      tertiary: '#F1F1F1',
    },
    // Text colors
    text: {
      primary: '#121212',
      secondary: '#424242',
      tertiary: '#686868',
      muted: '#8A8A8A',
    },
    // Border colors
    border: {
      light: '#E0E0E0',
      medium: '#D0D0D0',
      dark: '#BBBBBB',
    },
    // UI element colors
    ui: {
      focus: '#000000',
      hover: '#F5F5F5',
      active: '#EBEBEB',
      disabled: '#F5F5F5',
    },
    // Semantic colors
    semantic: {
      success: {
        background: '#F0FDF4',
        text: '#166534',
        border: '#166534',
      },
      error: {
        background: '#FEF2F2',
        text: '#991B1B',
        border: '#991B1B',
      },
      warning: {
        background: '#FFFBEB',
        text: '#92400E',
        border: '#92400E',
      },
      info: {
        background: '#F9FAFB',
        text: '#1F2937',
        border: '#1F2937',
      },
    },
  },
  
  // Dark theme colors
  dark: {
    // Background colors
    background: {
      primary: '#121212',
      secondary: '#1E1E1E',
      tertiary: '#2A2A2A',
    },
    // Text colors
    text: {
      primary: '#E0E0E0',
      secondary: '#BBBBBB',
      tertiary: '#999999',
      muted: '#777777',
    },
    // Border colors
    border: {
      light: '#333333',
      medium: '#444444',
      dark: '#555555',
    },
    // UI element colors
    ui: {
      focus: '#FFFFFF',
      hover: '#2A2A2A',
      active: '#333333',
      disabled: '#2A2A2A',
    },
    // Semantic colors
    semantic: {
      success: {
        background: '#132F1E',
        text: '#A7F3D0',
        border: '#059669',
      },
      error: {
        background: '#2C1519',
        text: '#FCA5A5',
        border: '#DC2626',
      },
      warning: {
        background: '#2E2100',
        text: '#FCD34D',
        border: '#D97706',
      },
      info: {
        background: '#1A202C',
        text: '#E0E7FF',
        border: '#4F46E5',
      },
    },
  },
  
  // Typography
  typography: {
    fontFamily: {
      serif: 'Georgia, "Times New Roman", Times, serif',
      sans: 'Helvetica, Arial, sans-serif',
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
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
    },
    lineHeight: {
      none: '1',
      tight: '1.25',
      snug: '1.375',
      normal: '1.5',
      relaxed: '1.625',
      loose: '2',
    },
  },
  
  // Spacing
  spacing: {
    0: '0',
    1: '0.25rem',
    2: '0.5rem',
    3: '0.75rem',
    4: '1rem',
    5: '1.25rem',
    6: '1.5rem',
    8: '2rem',
    10: '2.5rem',
    12: '3rem',
    16: '4rem',
    20: '5rem',
    24: '6rem',
    32: '8rem',
  },
  
  // Breakpoints
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
  
  // Transitions
  transitions: {
    default: '0.3s ease',
    fast: '0.15s ease',
    slow: '0.5s ease',
  },
  
  // Shadows
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  },
};
