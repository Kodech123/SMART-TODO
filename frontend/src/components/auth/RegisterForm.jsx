import { Alert, Box, Button, Container, Link, Paper, TextField, Typography } from '@mui/material'
import { useForm } from 'react-hook-form'
import { useDispatch, useSelector } from 'react-redux'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { registerUser } from '../../features/auth/authSlice'

export default function RegisterForm() {
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
      await dispatch(registerUser(values)).unwrap()
      navigate('/dashboard')
    } catch {
      // error is surfaced via auth.error in the store
    }
  }

  return (
    <Container maxWidth="xs" sx={{ mt: { xs: 4, sm: 10 }, px: { xs: 2, sm: 3 } }}>
      <Paper elevation={2} sx={{ p: { xs: 3, sm: 4 } }}>
        <Typography variant="h5" fontWeight={700} gutterBottom>
          Create your account
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Start prioritizing your tasks with DoSmart
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
          <TextField
            label="Display name"
            fullWidth
            margin="normal"
            inputProps={{ 'data-testid': 'display-name-input' }}
            error={Boolean(errors.displayName)}
            helperText={errors.displayName?.message}
            {...register('displayName', { required: 'Display name is required' })}
          />
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
            helperText={errors.password?.message ?? 'At least 8 characters'}
            {...register('password', {
              required: 'Password is required',
              minLength: { value: 8, message: 'Password must be at least 8 characters' },
            })}
          />
          <Button
            type="submit"
            variant="contained"
            fullWidth
            size="large"
            sx={{ mt: 3 }}
            disabled={isLoading}
            data-testid="register-btn"
          >
            Sign up
          </Button>
        </Box>

        <Typography variant="body2" sx={{ mt: 3, textAlign: 'center' }}>
          Already have an account? <Link component={RouterLink} to="/login">Log in</Link>
        </Typography>
      </Paper>
    </Container>
  )
}
