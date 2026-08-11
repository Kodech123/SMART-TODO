import { Alert, Box, Button, Container, Link, Paper, TextField, Typography } from '@mui/material'
import { useForm } from 'react-hook-form'
import { useDispatch, useSelector } from 'react-redux'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { fetchCurrentUser, loginUser } from '../../features/auth/authSlice'

export default function LoginForm() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { error, isLoading } = useSelector((state) => state.auth)
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm()

  async function onSubmit(values) {
    try {
      await dispatch(loginUser(values)).unwrap()
      await dispatch(fetchCurrentUser())
      navigate('/dashboard')
    } catch {
      // error is surfaced via auth.error in the store
    }
  }

  return (
    <Container maxWidth="xs" sx={{ mt: 10 }}>
      <Paper elevation={2} sx={{ p: 4 }}>
        <Typography variant="h5" fontWeight={700} gutterBottom>
          Welcome back
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Log in to DoSmart
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} data-testid="login-error">
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
          <TextField
            label="Email"
            type="email"
            fullWidth
            margin="normal"
            inputProps={{ 'data-testid': 'email-input' }}
            error={Boolean(errors.email)}
            helperText={errors.email?.message}
            {...register('email', { required: 'Email is required' })}
          />
          <TextField
            label="Password"
            type="password"
            fullWidth
            margin="normal"
            inputProps={{ 'data-testid': 'password-input' }}
            error={Boolean(errors.password)}
            helperText={errors.password?.message}
            {...register('password', { required: 'Password is required' })}
          />
          <Button
            type="submit"
            variant="contained"
            fullWidth
            size="large"
            sx={{ mt: 3 }}
            disabled={isLoading}
            data-testid="login-btn"
          >
            Log in
          </Button>
        </Box>

        <Typography variant="body2" sx={{ mt: 3, textAlign: 'center' }}>
          Don&apos;t have an account? <Link component={RouterLink} to="/register">Sign up</Link>
        </Typography>
      </Paper>
    </Container>
  )
}
