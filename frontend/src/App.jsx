import { CssBaseline, ThemeProvider } from '@mui/material'
import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { fetchCurrentUser } from './features/auth/authSlice'
import AppRoutes from './routes/AppRoutes'
import theme from './theme/theme'

export default function App() {
  const dispatch = useDispatch()
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated)
  const user = useSelector((state) => state.auth.user)

  useEffect(() => {
    if (isAuthenticated && !user) {
      dispatch(fetchCurrentUser())
    }
  }, [dispatch, isAuthenticated, user])

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </ThemeProvider>
  )
}
