import { useCallback, useState } from 'react'
import * as pushApi from '../api/pushApi'

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = window.atob(base64)
  return Uint8Array.from([...rawData].map((char) => char.charCodeAt(0)))
}

export function usePushSubscription() {
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState(null)

  const subscribe = useCallback(async () => {
    setStatus('subscribing')
    setError(null)
    try {
      if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        throw new Error('Push notifications are not supported in this browser')
      }
      await navigator.serviceWorker.register('/service-worker.js')
      // register() resolves once the service worker is queued, not once it's active --
      // pushManager.subscribe() requires an active worker, so wait for that specifically
      // (matters most on a first-ever visit, before any service worker has installed yet).
      const registration = await navigator.serviceWorker.ready
      const permission = await Notification.requestPermission()
      if (permission !== 'granted') {
        throw new Error('Notification permission denied')
      }
      const vapidPublicKey = import.meta.env.VITE_VAPID_PUBLIC_KEY
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: vapidPublicKey ? urlBase64ToUint8Array(vapidPublicKey) : undefined,
      })
      await pushApi.subscribe(subscription.toJSON())
      setStatus('subscribed')
    } catch (err) {
      setError(err.message)
      setStatus('error')
    }
  }, [])

  return { subscribe, status, error }
}
