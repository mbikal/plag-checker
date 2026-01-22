import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'

type AuthMode = 'login' | 'signup'

type AuthResponse = {
  message?: string
  error?: string
  role?: string
  certificate_path?: string
}

const DEFAULT_ROLE = 'student'

function App() {
  const [mode, setMode] = useState<AuthMode>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState(DEFAULT_ROLE)
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState<AuthResponse | null>(null)

  const apiBase = useMemo(() => 'http://127.0.0.1:5000', [])

  const resetFeedback = () => setResponse(null)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    resetFeedback()
    setLoading(true)

    const payload: Record<string, string> = { username, password }
    if (mode === 'signup') {
      payload.role = role
    }

    try {
      const res = await fetch(`${apiBase}/${mode === 'login' ? 'login' : 'signup'}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const data = (await res.json()) as AuthResponse
      setResponse(data)
    } catch (error) {
      setResponse({ error: 'Unable to reach the server. Check API URL or backend status.' })
    } finally {
      setLoading(false)
    }
  }

  const successMessage = response?.message
  const errorMessage = response?.error

  return (
    <div className="page">
      <div className="orb orb-one" aria-hidden="true" />
      <div className="orb orb-two" aria-hidden="true" />

      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">PC</span>
          <div>
            <p className="brand-title">Plag Checker</p>
            <p className="brand-subtitle">Secure access for integrity tools</p>
          </div>
        </div>
        <div className="env-pill">
          <span className="dot" />
          API: {apiBase}
        </div>
      </header>

      <main className="content">
        <section className="intro">
          <h1>
            Trusted authentication for every scan, every time.
          </h1>
          <p>
            Create verified accounts and issue certificates that prove authorship during plagiarism checks.
            Switch between login and sign up without leaving this screen.
          </p>
          <div className="feature-grid">
            <div className="feature-card">
              <h3>Certificate-backed access</h3>
              <p>Every login issues a fresh certificate tied to user role.</p>
            </div>
            <div className="feature-card">
              <h3>Role-based setup</h3>
              <p>Choose student or teacher roles during onboarding.</p>
            </div>
            <div className="feature-card">
              <h3>Simple JSON API</h3>
              <p>Frontend connects directly to the Flask endpoints.</p>
            </div>
          </div>
        </section>

        <section className="panel" aria-live="polite">
          <div className="panel-tabs">
            <button
              className={mode === 'login' ? 'tab active' : 'tab'}
              type="button"
              onClick={() => {
                setMode('login')
                resetFeedback()
              }}
            >
              Login
            </button>
            <button
              className={mode === 'signup' ? 'tab active' : 'tab'}
              type="button"
              onClick={() => {
                setMode('signup')
                resetFeedback()
              }}
            >
              Sign up
            </button>
          </div>

          <form className="form" onSubmit={handleSubmit}>
            <label className="field">
              <span>Username</span>
              <input
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="e.g. ada.lovelace"
                required
              />
            </label>

            <label className="field">
              <span>Password</span>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="••••••••"
                required
              />
            </label>

            {mode === 'signup' ? (
              <label className="field">
                <span>Role</span>
                <select value={role} onChange={(event) => setRole(event.target.value)}>
                  <option value="student">Student</option>
                  <option value="teacher">Teacher</option>
                </select>
              </label>
            ) : null}

            <button className="submit" type="submit" disabled={loading}>
              {loading ? 'Processing...' : mode === 'login' ? 'Log in' : 'Create account'}
            </button>
          </form>

          <div className="feedback">
            {successMessage ? <p className="success">{successMessage}</p> : null}
            {errorMessage ? <p className="error">{errorMessage}</p> : null}
            {response?.certificate_path ? (
              <div className="cert">
                <p className="label">Certificate path</p>
                <code>{response.certificate_path}</code>
              </div>
            ) : null}
            {response?.role ? (
              <div className="role-pill">
                Role: <strong>{response.role}</strong>
              </div>
            ) : null}
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
