import { useEffect, useState } from 'react'

export const routes = {
  home: '/',
  auth: '/auth',
  upload: '/upload',
} as const

type RoutePath = typeof routes[keyof typeof routes]

const normalizePath = (hash: string) => {
  if (!hash || hash === '#') {
    return routes.home
  }
  const raw = hash.startsWith('#') ? hash.slice(1) : hash
  return raw.startsWith('/') ? raw : `/${raw}`
}

const getRoute = (): RoutePath => {
  const path = normalizePath(window.location.hash)
  if (path === routes.upload) {
    return routes.upload
  }
  if (path === routes.auth) {
    return routes.auth
  }
  return routes.home
}

export const navigate = (path: RoutePath) => {
  window.location.hash = path
}

export const useRoute = () => {
  const [route, setRoute] = useState<RoutePath>(() => getRoute())

  useEffect(() => {
    if (!window.location.hash) {
      window.location.hash = routes.home
    }
    const handleChange = () => setRoute(getRoute())
    window.addEventListener('hashchange', handleChange)
    return () => window.removeEventListener('hashchange', handleChange)
  }, [])

  return route
}
