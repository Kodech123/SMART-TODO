import { screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { renderWithProviders } from '../../test/testUtils'
import TaskCard from './TaskCard'

const BASE_TASK = {
  task_id: 1,
  title: 'Submit assignment',
  category: 'Academic',
  due_date: '2026-12-20T17:00:00Z',
  priority_score: 7.82,
  priority_label: 'P2',
  status: 'active',
  days_remaining: 5,
}

describe('TaskCard', () => {
  it('renders the title, category, and priority badge', () => {
    renderWithProviders(<TaskCard task={BASE_TASK} onClick={() => {}} />)

    expect(screen.getByText('Submit assignment')).toBeInTheDocument()
    expect(screen.getByText('Academic')).toBeInTheDocument()
    expect(screen.getByTestId('priority-badge')).toHaveTextContent('P2')
  })

  it('shows overdue styling text when days_remaining is negative', () => {
    renderWithProviders(<TaskCard task={{ ...BASE_TASK, days_remaining: -2 }} onClick={() => {}} />)
    expect(screen.getByText(/overdue/i)).toBeInTheDocument()
  })

  it('shows completed tasks with a checked, disabled checkbox', () => {
    renderWithProviders(<TaskCard task={{ ...BASE_TASK, status: 'completed' }} onClick={() => {}} />)
    const checkbox = screen.getByRole('checkbox')
    expect(checkbox).toBeChecked()
    expect(checkbox).toBeDisabled()
  })

  it('calls onClick when the card is clicked', () => {
    const onClick = vi.fn()
    renderWithProviders(<TaskCard task={BASE_TASK} onClick={onClick} />)

    screen.getByText('Submit assignment').click()
    expect(onClick).toHaveBeenCalledTimes(1)
  })
})
