import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

export function formatDateTime(isoString) {
  return dayjs(isoString).format('MMM D, YYYY h:mm A')
}

export function formatDate(isoString) {
  return dayjs(isoString).format('MMM D, YYYY')
}

export function fromNow(isoString) {
  return dayjs(isoString).fromNow()
}

export function daysRemainingLabel(days) {
  if (days < 0) return `${Math.abs(days)} day${Math.abs(days) === 1 ? '' : 's'} overdue`
  if (days === 0) return 'Due today'
  return `${days} day${days === 1 ? '' : 's'} remaining`
}
