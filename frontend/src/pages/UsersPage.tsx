import { useMemo, useState } from 'react'
import { navigate, routes } from '../routes'

type UserEntry = {
  username: string
  role: string
}

type UsersResponse = {
  users?: UserEntry[]
  error?: string
}

type AdminResponse = {
  message?: string
  error?: string
}

function UsersPage() {
  const role = useMemo(() => localStorage.getItem('plagchecker.role') || '', [])
  const adminUsername = useMemo(() => localStorage.getItem('plagchecker.username') || '', [])
  const [adminPassword, setAdminPassword] = useState('')
  const [users, setUsers] = useState<UserEntry[]>([])
  const [status, setStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const apiBase =
    (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') ||
    window.location.origin

  const loadUsers = async () => {
    setStatus(null)
    setError(null)
    try {
      const res = await fetch(`${apiBase}/admin/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          admin_username: adminUsername,
          admin_password: adminPassword,
        }),
      })
      const data = (await res.json()) as UsersResponse
      if (!res.ok) {
        setError(data.error || 'Unable to load users.')
        return
      }
      setUsers(data.users || [])
      setStatus('User list updated.')
    } catch {
      setError('Unable to reach the server.')
    }
  }

  const updateRole = async (username: string, newRole: string) => {
    setStatus(null)
    setError(null)
    try {
      const res = await fetch(`${apiBase}/admin/users/role`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          admin_username: adminUsername,
          admin_password: adminPassword,
          username,
          role: newRole,
        }),
      })
      const data = (await res.json()) as AdminResponse
      if (!res.ok) {
        setError(data.error || 'Unable to update role.')
        return
      }
      setStatus(data.message || 'Role updated.')
      loadUsers()
    } catch {
      setError('Unable to reach the server.')
    }
  }

  const deleteUser = async (username: string) => {
    setStatus(null)
    setError(null)
    try {
      const res = await fetch(`${apiBase}/admin/users/delete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          admin_username: adminUsername,
          admin_password: adminPassword,
          username,
        }),
      })
      const data = (await res.json()) as AdminResponse
      if (!res.ok) {
        setError(data.error || 'Unable to delete user.')
        return
      }
      setStatus(data.message || 'User deleted.')
      loadUsers()
    } catch {
      setError('Unable to reach the server.')
    }
  }

  const resetPassword = async (username: string, newPassword: string) => {
    setStatus(null)
    setError(null)
    try {
      const res = await fetch(`${apiBase}/admin/users/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          admin_username: adminUsername,
          admin_password: adminPassword,
          username,
          password: newPassword,
        }),
      })
      const data = (await res.json()) as AdminResponse
      if (!res.ok) {
        setError(data.error || 'Unable to reset password.')
        return
      }
      setStatus(data.message || 'Password reset.')
    } catch {
      setError('Unable to reach the server.')
    }
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
            <p className="brand-subtitle">User control</p>
          </div>
        </button>
        <button className="ghost-button" type="button" onClick={() => navigate(routes.admin)}>
          Back to admin
        </button>
      </header>

      <main className="content">
        <section className="intro">
          <h1>User management</h1>
          <p>List users, adjust roles, delete accounts, or reset passwords.</p>
        </section>

        <section className="panel">
          <label className="field">
            <span>Admin password</span>
            <input
              type="password"
              value={adminPassword}
              onChange={(event) => setAdminPassword(event.target.value)}
              placeholder="••••••••"
            />
          </label>
          <div className="button-row">
            <button className="scan-button" type="button" onClick={loadUsers}>
              Load users
            </button>
          </div>

          {status ? <p className="success">{status}</p> : null}
          {error ? <p className="scan-error">{error}</p> : null}

          <div className="user-list">
            {users.length ? (
              users.map((user) => (
                <div key={user.username} className="user-row">
                  <div>
                    <p className="user-name">{user.username}</p>
                    <p className="report-subtitle">Role: {user.role}</p>
                  </div>
                  <div className="user-actions">
                    <select
                      value={user.role}
                      onChange={(event) => updateRole(user.username, event.target.value)}
                    >
                      <option value="student">student</option>
                      <option value="teacher">teacher</option>
                      <option value="admin">admin</option>
                    </select>
                    <button
                      className="ghost-button"
                      type="button"
                      onClick={() => deleteUser(user.username)}
                    >
                      Delete
                    </button>
                    <button
                      className="ghost-button"
                      type="button"
                      onClick={() => {
                        const value = window.prompt('Enter new password')
                        if (value) {
                          resetPassword(user.username, value)
                        }
                      }}
                    >
                      Reset password
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <p className="report-subtitle">No users loaded yet.</p>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}

export default UsersPage
