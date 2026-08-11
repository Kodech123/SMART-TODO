import { Navigate, Route, Routes } from 'react-router-dom'
import ProtectedRoute from '../components/auth/ProtectedRoute'
import LoginForm from '../components/auth/LoginForm'
import RegisterForm from '../components/auth/RegisterForm'
import Dashboard from '../components/dashboard/Dashboard'
import Layout from '../components/layout/Layout'
import RemindersPage from '../components/reminders/RemindersPage'
import Settings from '../components/settings/Settings'
import TaskList from '../components/tasks/TaskList'

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginForm />} />
      <Route path="/register" element={<RegisterForm />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/tasks" element={<TaskList />} />
          <Route path="/reminders" element={<RemindersPage />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Route>

      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
