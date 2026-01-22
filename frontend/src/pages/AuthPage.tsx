import { useState } from 'react'
import type { FormEvent } from 'react'
import { navigate, routes } from '../routes'

type AuthMode = 'login' | 'signup'

type AuthResponse = {
  message?: string
  error?: string
}

const apiBase = 'http://127.0.0.1:5000'

function AuthPage() {
  const [mode, setMode] = useState<AuthMode>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState<AuthResponse | null>(null)

  const resetFeedback = () => setResponse(null)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    resetFeedback()
    setLoading(true)

    if (mode === 'signup' && password !== confirmPassword) {
      setResponse({ error: 'Passwords do not match.' })
      setLoading(false)
      return
    }

    const payload: Record<string, string> = { username, password }
    try {
      const res = await fetch(`${apiBase}/${mode === 'login' ? 'login' : 'signup'}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const data = (await res.json()) as AuthResponse
      setResponse(data)
      if (mode === 'login' && !data.error) {
        localStorage.setItem('plagchecker.username', username)
        navigate(routes.upload)
      }
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
        <button className="brand" type="button" onClick={() => navigate(routes.home)}>
          <span className="brand-mark">PC</span>
          <div>
            <p className="brand-title">Plag Checker</p>
            <p className="brand-subtitle">Secure access for plagiarism reports</p>
          </div>
        </button>
      </header>

      <main className="content">
        <section className="intro">
          <h1>
            Plagiarism checks that stay fair, fast, and traceable.
          </h1>
          <p>
            Sign in to submit documents, compare against sources, and generate a clear similarity report.
            Create an account in seconds and keep your submissions organized.
          </p>
          <div className="feature-grid">
            <div className="feature-card">
              <h3>Similarity insights</h3>
              <p>See matched sources and percentages at a glance.</p>
            </div>
            <div className="feature-card">
              <h3>Secure submissions</h3>
              <p>Your uploads stay tied to your account for quick retrieval.</p>
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
                setConfirmPassword('')
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
                <span>Confirm password</span>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  placeholder="••••••••"
                  required
                />
              </label>
            ) : null}

            <button className="submit" type="submit" disabled={loading}>
              {loading ? 'Processing...' : mode === 'login' ? 'Log in' : 'Create account'}
            </button>
          </form>

          <div className="feedback">
            {successMessage ? <p className="success">{successMessage}</p> : null}
            {errorMessage ? <p className="error">{errorMessage}</p> : null}
          </div>
        </section>
      </main>
    </div>
  )
}

export default AuthPage
