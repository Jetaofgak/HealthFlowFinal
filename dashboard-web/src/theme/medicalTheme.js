import { createTheme, alpha } from '@mui/material/styles';

export const medicalTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0066CC',
      light: '#3399FF',
      dark: '#004C99',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#00A86B',
      light: '#2ECC71',
      dark: '#008B57',
      contrastText: '#FFFFFF',
    },
    error: {
      main: '#E74C3C',
      light: '#EF5350',
      dark: '#C62828',
    },
    warning: {
      main: '#F39C12',
      light: '#FFB74D',
      dark: '#E65100',
    },
    success: {
      main: '#27AE60',
      light: '#66BB6A',
      dark: '#1B5E20',
    },
    info: {
      main: '#3498DB',
      light: '#64B5F6',
      dark: '#1565C0',
    },
    background: {
      default: '#F8F9FA',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#2C3E50',
      secondary: '#7F8C8D',
    },
    divider: '#DEE2E6',
  },
  typography: {
    fontFamily: '"Inter", "Segoe UI", system-ui, -apple-system, sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      letterSpacing: '-0.02em',
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      letterSpacing: '-0.01em',
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      letterSpacing: '-0.01em',
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
    h6: {
      fontSize: '1.125rem',
      fontWeight: 600,
    },
    subtitle1: {
      fontSize: '1rem',
      fontWeight: 500,
      letterSpacing: '0.01em',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    button: {
      fontWeight: 600,
      letterSpacing: '0.02em',
      textTransform: 'none',
    },
  },
  shape: {
    borderRadius: 12,
  },
  shadows: [
    'none',
    '0 1px 3px rgba(0,0,0,0.08)',
    '0 2px 6px rgba(0,0,0,0.08)',
    '0 4px 12px rgba(0,0,0,0.1)',
    '0 6px 16px rgba(0,0,0,0.1)',
    '0 8px 24px rgba(0,0,0,0.12)',
    '0 12px 32px rgba(0,0,0,0.12)',
    '0 16px 40px rgba(0,0,0,0.14)',
    '0 20px 48px rgba(0,0,0,0.14)',
    '0 24px 56px rgba(0,0,0,0.16)',
    '0 28px 64px rgba(0,0,0,0.16)',
    ...Array(14).fill('0 32px 72px rgba(0,0,0,0.18)'),
  ],
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarWidth: 'thin',
          '&::-webkit-scrollbar': {
            width: '8px',
            height: '8px',
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: '#BDC3C7',
            borderRadius: '4px',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          borderRadius: 16,
          transition: 'transform 250ms cubic-bezier(0.4, 0, 0.2, 1), box-shadow 250ms cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 32px rgba(0,0,0,0.12)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          padding: '10px 24px',
          fontSize: '0.95rem',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          },
        },
        containedPrimary: {
          background: 'linear-gradient(135deg, #0066CC 0%, #004C99 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #0077ED 0%, #0066CC 100%)',
          },
        },
        containedSecondary: {
          background: 'linear-gradient(135deg, #00A86B 0%, #008B57 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #00C77B 0%, #00A86B 100%)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 600,
          borderRadius: 8,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
        elevation1: {
          boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
        },
        elevation2: {
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        },
        elevation3: {
          boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          border: 'none',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          margin: '4px 8px',
          '&.Mui-selected': {
            backgroundColor: alpha('#0066CC', 0.1),
            '&:hover': {
              backgroundColor: alpha('#0066CC', 0.15),
            },
          },
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          height: 8,
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

// Risk level colors for charts
export const RISK_COLORS = {
  critical: '#E74C3C',
  high: '#F39C12',
  moderate: '#F1C40F',
  low: '#27AE60',
  minimal: '#95A5A6',
};

// Chart color palette
export const CHART_COLORS = [
  '#0066CC',
  '#00A86B',
  '#F39C12',
  '#E74C3C',
  '#9B59B6',
  '#3498DB',
  '#1ABC9C',
  '#E67E22',
];

export default medicalTheme;
