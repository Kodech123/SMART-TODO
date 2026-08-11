import ChecklistIcon from '@mui/icons-material/Checklist'
import DashboardIcon from '@mui/icons-material/Dashboard'
import NotificationsIcon from '@mui/icons-material/Notifications'
import SettingsIcon from '@mui/icons-material/Settings'
import { Drawer, List, ListItemButton, ListItemIcon, ListItemText, Toolbar } from '@mui/material'
import { useLocation, useNavigate } from 'react-router-dom'

const DRAWER_WIDTH = 220

const NAV_ITEMS = [
  { label: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
  { label: 'Tasks', path: '/tasks', icon: <ChecklistIcon /> },
  { label: 'Reminders', path: '/reminders', icon: <NotificationsIcon /> },
  { label: 'Settings', path: '/settings', icon: <SettingsIcon /> },
]

export default function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { width: DRAWER_WIDTH, boxSizing: 'border-box' },
      }}
    >
      <Toolbar />
      <List>
        {NAV_ITEMS.map((item) => (
          <ListItemButton
            key={item.path}
            selected={location.pathname.startsWith(item.path)}
            onClick={() => navigate(item.path)}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
    </Drawer>
  )
}

export { DRAWER_WIDTH }
