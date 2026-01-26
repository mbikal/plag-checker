import { useMemo, useState } from 'react'
import { navigate, routes } from '../routes'

type LogResponse = {
  lines?: string[]
  error?: string
}

type AdminResponse = {
  message?: string
  error?: string
}

function AdminPage() {
  const role = useMemo(() => localStorage.getItem('plagchecker.role') || '', [])
  const adminUsername = useMemo(
    () => localStorage.getItem('plagchecker.username') || '',
    [],
  )
  const [adminPassword, setAdminPassword] = useState('')
  const [teacherUsername, setTeacherUsername] = useState('')
  const [teacherPassword, setTeacherPassword] = useState('')
  const [logs, setLogs] = useState<string[]>([])
  const [status, setStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showTeacherForm, setShowTeacherForm] = useState(false)
  const [showAdminMenu, setShowAdminMenu] = useState(false)
  const apiBase =
    (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') ||
    window.location.origin

  const fetchLogs = async () => {
    setError(null)
    setStatus(null)
    try {
      const res = await fetch(`${apiBase}/admin/logs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ limit: 200 }),
      })
      const data = (await res.json()) as LogResponse
      if (!res.ok) {
        setError(data.error || 'Unable to fetch logs.')
        return
      }
      setLogs(data.lines || [])
      setStatus('Logs updated.')
    } catch {
      setError('Unable to reach the server.')
    }
  }

  const createTeacher = async () => {
    setError(null)
    setStatus(null)
    try {
      const res = await fetch(`${apiBase}/admin/teacher`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          admin_username: adminUsername,
          admin_password: adminPassword,
          username: teacherUsername,
          password: teacherPassword,
        }),
      })
      const data = (await res.json()) as AdminResponse
      if (!res.ok) {
        setError(data.error || 'Unable to create teacher.')
        return
      }
      setStatus(data.message || 'Teacher account created.')
      setTeacherUsername('')
      setTeacherPassword('')
    } catch {
      setError('Unable to reach the server.')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('plagchecker.username')
    localStorage.removeItem('plagchecker.session')
    localStorage.removeItem('plagchecker.role')
    navigate(routes.auth)
  }

  if (role !== 'admin') {
    return (
      <div className="page">
        <div className="orb orb-one" aria-hidden="true" />
        <div className="orb orb-two" aria-hidden="true" />
        <header className="topbar">
          <button className="brand" type="button" onClick={() => navigate(routes.home)}>
            <span className="brand-mark">PC</span>
            <div>
              <p className="brand-title">Plag Checker</p>
              <p className="brand-subtitle">Admin access required</p>
            </div>
          </button>
        </header>
        <main className="content">
          <section className="panel">
            <p className="scan-error">You need an admin account to access this page.</p>
            <button className="submit" type="button" onClick={() => navigate(routes.auth)}>
              Go to login
            </button>
          </section>
        </main>
      </div>
    )
  }

  return (
    <div className="page">
      <div className="orb orb-one" aria-hidden="true" />
      <div className="orb orb-two" aria-hidden="true" />

      <header className="topbar">
        <button className="brand" type="button" onClick={() => navigate(routes.home)}>
          <span className="brand-mark">PC</span>
          <div>
            <p className="brand-title">Plag Checker</p>
            <p className="brand-subtitle">Admin dashboard</p>
          </div>
        </button>
        <div className="admin-menu">
          <button
            className="ghost-button"
            type="button"
            onClick={() => setShowAdminMenu((value) => !value)}
          >
            Admin actions
          </button>
          {showAdminMenu ? (
            <div className="admin-menu-panel">
              <button
                className="menu-item"
                type="button"
                onClick={() => {
                  setShowTeacherForm(true)
                  setShowAdminMenu(false)
                }}
              >
                Create teacher account
              </button>
              <button
                className="menu-item"
                type="button"
                onClick={() => goTo(routes.uploads)}
              >
                View uploads
              </button>
              <button
                className="menu-item"
                type="button"
                onClick={() => goTo(routes.users)}
              >
                User control
              </button>
              <button
                className="menu-item"
                type="button"
                onClick={() => goTo(routes.database)}
              >
                Database management
              </button>
              <button
                className="menu-item"
                type="button"
                onClick={() => {
                  setShowAdminMenu(false)
                  handleLogout()
                }}
              >
                Log out
              </button>
            </div>
          ) : null}
        </div>
      </header>

      <main className="content">
        <section className="intro">
          <h1>Monitor the system.</h1>
          <p>Review recent activity and create teacher accounts.</p>
        </section>

        <section className="panel">
          <div className="admin-grid">
            <div className="admin-card">
              <h3>System logs</h3>
              <p className="report-subtitle">Signed in as {adminUsername}</p>
              <button className="scan-button" type="button" onClick={fetchLogs}>
                Refresh logs
              </button>
            </div>

            <div className="admin-card">
              {showTeacherForm ? (
                <div className="dropdown-panel">
                  <label className="field">
                    <span>Teacher username</span>
                    <input
                      value={teacherUsername}
                      onChange={(event) => setTeacherUsername(event.target.value)}
                      placeholder="teacher.name"
                    />
                  </label>
                  <label className="field">
                    <span>Teacher password</span>
                    <input
                      type="password"
                      value={teacherPassword}
                      onChange={(event) => setTeacherPassword(event.target.value)}
                      placeholder="••••••••"
                    />
                  </label>
                  <label className="field">
                    <span>Admin password</span>
                    <input
                      type="password"
                      value={adminPassword}
                      onChange={(event) => setAdminPassword(event.target.value)}
                      placeholder="••••••••"
                    />
                  </label>
                  <button className="submit" type="button" onClick={createTeacher}>
                    Create teacher
                  </button>
                </div>
              ) : null}
            </div>
          </div>

          {status ? <p className="success">{status}</p> : null}
          {error ? <p className="scan-error">{error}</p> : null}

          <div className="report logs">
            <p className="report-title">Recent logs</p>
            <pre>{logs.length ? logs.join('\n') : 'No logs yet.'}</pre>
          </div>
        </section>
      </main>
    </div>
  )
}

export default AdminPage
  const goTo = (path: string) => {
    setShowAdminMenu(false)
    navigate(path as typeof routes[keyof typeof routes])
  }
