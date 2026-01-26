import { useEffect, useState } from 'react'

export const routes = {
  home: '/',
  auth: '/auth',
  upload: '/upload',
  report: '/report',
  admin: '/admin',
  uploads: '/uploads',
  users: '/users',
  database: '/database',
  dashboard: '/dashboard',
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
  if (path === routes.report) {
    return routes.report
  }
  if (path === routes.admin) {
    return routes.admin
  }
  if (path === routes.uploads) {
    return routes.uploads
  }
  if (path === routes.users) {
    return routes.users
  }
  if (path === routes.database) {
    return routes.database
  }
  if (path === routes.dashboard) {
    return routes.dashboard
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
