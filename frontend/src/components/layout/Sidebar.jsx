import ChecklistIcon from '@mui/icons-material/Checklist'
import DashboardIcon from '@mui/icons-material/Dashboard'
import NotificationsIcon from '@mui/icons-material/Notifications'
import SettingsIcon from '@mui/icons-material/Settings'
import { Box, Drawer, List, ListItemButton, ListItemIcon, ListItemText, Toolbar } from '@mui/material'
import { useDispatch, useSelector } from 'react-redux'
import { useLocation, useNavigate } from 'react-router-dom'
import { closeMobileNav } from '../../features/ui/uiSlice'

const DRAWER_WIDTH = 240

const NAV_ITEMS = [
  { label: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
  { label: 'Tasks', path: '/tasks', icon: <ChecklistIcon /> },
  { label: 'Reminders', path: '/reminders', icon: <NotificationsIcon /> },
  { label: 'Settings', path: '/settings', icon: <SettingsIcon /> },
]

function NavList({ onNavigate }) {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <List sx={{ px: 1.5, py: 1 }}>
      {NAV_ITEMS.map((item) => {
        const selected = location.pathname.startsWith(item.path)
        return (
          <ListItemButton
            key={item.path}
            selected={selected}
            onClick={() => {
              navigate(item.path)
              onNavigate?.()
            }}
            data-testid={`nav-${item.path.slice(1)}`}
            sx={{
              borderRadius: 2,
              mb: 0.5,
              color: selected ? 'primary.main' : 'text.secondary',
              '&.Mui-selected': {
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                '&:hover': { bgcolor: 'primary.dark' },
                '& .MuiListItemIcon-root': { color: 'primary.contrastText' },
              },
            }}
          >
            <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} primaryTypographyProps={{ fontWeight: selected ? 700 : 500 }} />
          </ListItemButton>
        )
      })}
    </List>
  )
}

export default function Sidebar() {
  const dispatch = useDispatch()
  const mobileOpen = useSelector((state) => state.ui.mobileNavOpen)

  function handleClose() {
    dispatch(closeMobileNav())
  }

  return (
    <Box component="nav" sx={{ width: { md: DRAWER_WIDTH }, flexShrink: { md: 0 } }}>
      {/* Mobile: overlay drawer toggled by the header's hamburger button */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleClose}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { width: DRAWER_WIDTH, boxSizing: 'border-box' },
        }}
      >
        <Toolbar />
        <NavList onNavigate={handleClose} />
      </Drawer>

      {/* Desktop: always-visible drawer */}
      <Drawer
        variant="permanent"
        open
        sx={{
          display: { xs: 'none', md: 'block' },
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            borderRight: '1px solid',
            borderColor: 'divider',
          },
        }}
      >
        <Toolbar />
        <NavList />
      </Drawer>
    </Box>
  )
}

export { DRAWER_WIDTH }
