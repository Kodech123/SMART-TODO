import { Box, Snackbar, Toolbar } from '@mui/material'
import { useDispatch, useSelector } from 'react-redux'
import { Outlet } from 'react-router-dom'
import { clearToast } from '../../features/ui/uiSlice'
import Header from './Header'
import Sidebar from './Sidebar'

export default function Layout() {
  const dispatch = useDispatch()
  const toastMessage = useSelector((state) => state.ui.toastMessage)

  return (
    <Box sx={{ display: 'flex' }}>
      <Header />
      <Sidebar />
      <Box
        component="main"
        sx={{ flexGrow: 1, minWidth: 0, bgcolor: 'background.default', minHeight: '100vh', p: { xs: 2, sm: 3 } }}
      >
        <Toolbar />
        <Outlet />
      </Box>
      <Snackbar
        open={Boolean(toastMessage)}
        autoHideDuration={4000}
        onClose={() => dispatch(clearToast())}
        message={toastMessage}
      />
    </Box>
  )
}
