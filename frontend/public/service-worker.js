self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : {}
  const options = {
    body: data.body,
    icon: data.icon || '/icon-192x192.png',
    badge: data.badge || '/badge-72x72.png',
    data: data.data || {},
    tag: data.data?.task_id ? `task-${data.data.task_id}` : undefined,
    requireInteraction: false,
  }

  event.waitUntil(self.registration.showNotification(data.title || 'DoSmart', options))
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const targetUrl = event.notification.data?.click_action || '/tasks'

  event.waitUntil(
    self.clients.matchAll({ type: 'window' }).then((clientList) => {
      for (const client of clientList) {
        if ('focus' in client) {
          client.navigate(targetUrl)
          return client.focus()
        }
      }
      return self.clients.openWindow(targetUrl)
    }),
  )
})
