import { createTheme } from '@mui/material/styles'

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

const theme = createTheme({
  palette: {
    primary: { main: '#2E5C8A' },
    secondary: { main: '#388E3C' },
    background: { default: '#F5F7FA' },
  },
  shape: { borderRadius: 8 },
  typography: {
    fontFamily: ['Inter', 'Roboto', 'Segoe UI', 'sans-serif'].join(','),
  },
})

export default theme
