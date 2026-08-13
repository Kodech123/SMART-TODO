const API_BASE = new URL(self.location.href).searchParams.get('apiBase') || self.location.origin

self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : {}
  const options = {
    body: data.body,
    icon: data.icon || '/favicon.svg',
    badge: data.badge || '/favicon.svg',
    data: data.data || {},
    tag: data.data?.task_id ? `task-${data.data.task_id}` : undefined,
    requireInteraction: false,
  }

  event.waitUntil(self.registration.showNotification(data.title || 'DoSmart', options))
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const { click_action: targetUrl = '/tasks', reminder_id: reminderId, opened_token: token } = event.notification.data || {}

  const reportOpened =
    reminderId && token
      ? fetch(`${API_BASE}/api/v1/reminders/${reminderId}/opened?token=${encodeURIComponent(token)}`, {
          method: 'PUT',
        }).catch(() => {})
      : Promise.resolve()

  const focusOrOpen = self.clients.matchAll({ type: 'window' }).then((clientList) => {
    for (const client of clientList) {
      if ('focus' in client) {
        client.navigate(targetUrl)
        return client.focus()
      }
    }
    return self.clients.openWindow(targetUrl)
  })

  event.waitUntil(Promise.all([reportOpened, focusOrOpen]))
})
