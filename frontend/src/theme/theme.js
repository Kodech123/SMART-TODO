import { createTheme, responsiveFontSizes } from '@mui/material/styles'

export const PRIORITY_COLORS = {
  P1: '#D32F2F',
  P2: '#F57C00',
  P3: '#1976D2',
  P4: '#616161',
}

export const PRIORITY_LABELS = {
  P1: 'Critical',
  P2: 'High',
  P3: 'Medium',
  P4: 'Low',
}

let theme = createTheme({
  palette: {
    primary: { main: '#2E5C8A', light: '#5580AC', dark: '#1F4266' },
    secondary: { main: '#2E9E5B' },
    background: { default: '#F4F6F9', paper: '#FFFFFF' },
  },
  shape: { borderRadius: 12 },
  typography: {
    fontFamily: ['Inter', 'Roboto', 'Segoe UI', 'sans-serif'].join(','),
    h4: { fontWeight: 700, letterSpacing: -0.5 },
    h5: { fontWeight: 700, letterSpacing: -0.25 },
    h6: { fontWeight: 700 },
    button: { fontWeight: 600, textTransform: 'none' },
  },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: { root: { borderRadius: 10 } },
    },
    MuiPaper: {
      styleOverrides: {
        outlined: { borderColor: 'rgba(0, 0, 0, 0.08)' },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 14,
          boxShadow: '0 1px 3px rgba(16, 24, 40, 0.06), 0 1px 2px rgba(16, 24, 40, 0.04)',
        },
      },
    },
    MuiChip: {
      styleOverrides: { root: { fontWeight: 600 } },
    },
    MuiAppBar: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: { borderBottom: '1px solid rgba(0, 0, 0, 0.08)' },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: { borderRadius: 16 },
        paperFullScreen: { borderRadius: 0 },
      },
    },
  },
})

theme = responsiveFontSizes(theme)

export default theme
