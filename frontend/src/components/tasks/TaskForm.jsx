import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  MenuItem,
  Stack,
  Switch,
  TextField,
  Typography,
} from '@mui/material'
import { useEffect } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { useDispatch, useSelector } from 'react-redux'
import { createTask, updateTask } from '../../features/tasks/tasksSlice'
import { closeTaskForm, showToast } from '../../features/ui/uiSlice'

const DEFAULT_VALUES = {
  title: '',
  description: '',
  category: '',
  due_date: '',
  importance_level: 3,
  estimated_effort: 3,
  enable_reminder: true,
}

export default function TaskForm() {
  const dispatch = useDispatch()
  const open = useSelector((state) => state.ui.showTaskForm)
  const editingTaskId = useSelector((state) => state.ui.editingTaskId)
  const categories = useSelector((state) => state.categories.items)
  const editingTask = useSelector((state) =>
    state.tasks.items.find((task) => task.task_id === editingTaskId),
  )

  const { control, register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm({
    defaultValues: DEFAULT_VALUES,
  })

  useEffect(() => {
    if (open) {
      reset(DEFAULT_VALUES)
    }
  }, [open, reset])

  async function onSubmit(values) {
    try {
      if (editingTaskId) {
        await dispatch(
          updateTask({
            taskId: editingTaskId,
            patch: {
              title: values.title,
              description: values.description || null,
              category: values.category || null,
              due_date: values.due_date,
              importance_level: values.importance_level,
              estimated_effort: values.estimated_effort,
            },
          }),
        ).unwrap()
        dispatch(showToast('Task updated'))
      } else {
        await dispatch(createTask(values)).unwrap()
        dispatch(showToast('Task created'))
      }
      dispatch(closeTaskForm())
    } catch (err) {
      dispatch(showToast(err?.message ?? 'Something went wrong'))
    }
  }

  return (
    <Dialog open={open} onClose={() => dispatch(closeTaskForm())} fullWidth maxWidth="sm">
      <DialogTitle>{editingTask ? 'Edit task' : 'New task'}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <TextField
            label="Title"
            fullWidth
            data-testid="task-title"
            error={Boolean(errors.title)}
            helperText={errors.title?.message}
            {...register('title', { required: 'Title is required', minLength: { value: 3, message: 'At least 3 characters' } })}
          />
          <TextField label="Description" fullWidth multiline rows={2} {...register('description')} />

          <TextField select label="Category" defaultValue="" {...register('category')}>
            <MenuItem value="">Auto-detect</MenuItem>
            {categories.map((category) => (
              <MenuItem key={category.category_id} value={category.category_name}>
                {category.category_name}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            label="Due date"
            placeholder="e.g. tomorrow at 5pm, in 3 days, 2026-12-25"
            fullWidth
            data-testid="due-date"
            error={Boolean(errors.due_date)}
            helperText={errors.due_date?.message ?? 'Natural language dates are supported'}
            {...register('due_date', { required: 'Due date is required' })}
          />

          <Stack>
            <Typography variant="body2" gutterBottom>
              Importance
            </Typography>
            <Controller
              name="importance_level"
              control={control}
              render={({ field }) => (
                <TextField
                  select
                  data-testid="importance"
                  value={field.value}
                  onChange={(e) => field.onChange(Number(e.target.value))}
                >
                  {[1, 2, 3, 4, 5].map((level) => (
                    <MenuItem key={level} value={level}>
                      {level}
                    </MenuItem>
                  ))}
                </TextField>
              )}
            />
          </Stack>

          <Stack>
            <Typography variant="body2" gutterBottom>
              Estimated effort
            </Typography>
            <Controller
              name="estimated_effort"
              control={control}
              render={({ field }) => (
                <TextField
                  select
                  data-testid="effort"
                  value={field.value}
                  onChange={(e) => field.onChange(Number(e.target.value))}
                >
                  {[1, 2, 3, 4, 5].map((level) => (
                    <MenuItem key={level} value={level}>
                      {level}
                    </MenuItem>
                  ))}
                </TextField>
              )}
            />
          </Stack>

          {!editingTaskId && (
            <FormControlLabel
              control={<Switch defaultChecked {...register('enable_reminder')} />}
              label="Enable reminder"
            />
          )}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => dispatch(closeTaskForm())}>Cancel</Button>
        <Button variant="contained" data-testid="submit-task" disabled={isSubmitting} onClick={handleSubmit(onSubmit)}>
          {editingTaskId ? 'Save' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
