import LogoutIcon from '@mui/icons-material/Logout'
import { AppBar, Avatar, Box, IconButton, Toolbar, Tooltip, Typography } from '@mui/material'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { logout } from '../../features/auth/authSlice'

export default function Header() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const user = useSelector((state) => state.auth.user)

  function handleLogout() {
    dispatch(logout())
    navigate('/login')
  }

  return (
    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, fontWeight: 700 }}>
          DoSmart
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          {user && (
            <Typography variant="body2" sx={{ display: { xs: 'none', sm: 'block' } }}>
              {user.display_name}
            </Typography>
          )}
          <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
            {user?.display_name?.[0]?.toUpperCase() ?? '?'}
          </Avatar>
          <Tooltip title="Log out">
            <IconButton color="inherit" onClick={handleLogout} data-testid="logout-btn">
              <LogoutIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  )
}
