import { useMemo, useState } from 'react'
import { navigate, routes } from '../routes'

function TeacherDashboard() {
  const role = useMemo(() => localStorage.getItem('plagchecker.role') || '', [])
  const username = useMemo(() => localStorage.getItem('plagchecker.username') || '', [])
  const [password, setPassword] = useState('')
  const [files, setFiles] = useState<
    {
      name: string
      url: string
      matching_sentences?: number
      total_sentences?: number
      plagiarism_percentage?: number
    }[]
  >([])
  const [checked, setChecked] = useState<Record<string, boolean>>({})
  const [error, setError] = useState<string | null>(null)
  const [status, setStatus] = useState<string | null>(null)
  const apiBase =
    (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') ||
    window.location.origin

  const loadUploads = async () => {
    setError(null)
    setStatus(null)
    try {
      const res = await fetch(`${apiBase}/teacher/uploads`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      const data = (await res.json()) as {
        files?: {
          name: string
          url: string
          matching_sentences?: number
          total_sentences?: number
          plagiarism_percentage?: number
        }[]
        error?: string
      }
      if (!res.ok) {
        setError(data.error || 'Unable to load uploads.')
        return
      }
      setFiles(data.files || [])
      setStatus('Uploads loaded.')
    } catch {
      setError('Unable to reach the server.')
    }
  }

  if (role !== 'teacher') {
    return (
      <div className="page">
        <div className="orb orb-one" aria-hidden="true" />
        <div className="orb orb-two" aria-hidden="true" />
        <header className="topbar">
          <button className="brand" type="button" onClick={() => navigate(routes.home)}>
            <span className="brand-mark">PC</span>
            <div>
              <p className="brand-title">Plag Checker</p>
              <p className="brand-subtitle">Teacher access required</p>
            </div>
          </button>
        </header>
        <main className="content">
          <section className="panel">
            <p className="scan-error">You need a teacher account to access this page.</p>
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
            <p className="brand-subtitle">Teacher dashboard</p>
          </div>
        </button>
        <button className="ghost-button" type="button" onClick={() => navigate(routes.upload)}>
          Go to upload
        </button>
      </header>

      <main className="content">
        <section className="intro">
          <h1>Welcome, {username || 'teacher'}.</h1>
          <p>Review submissions, manage classes, and track reports.</p>
        </section>

        <section className="panel">
          <label className="field">
            <span>Password</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
            />
          </label>
          <div className="button-row">
            <button className="scan-button" type="button" onClick={loadUploads}>
              View uploads
            </button>
          </div>
          {status ? <p className="success">{status}</p> : null}
          {error ? <p className="scan-error">{error}</p> : null}
          <div className="uploads-list">
            {files.length ? (
              files.map((file) => (
                <div className="user-row" key={file.name}>
                  <div>
                    <a className="upload-link" href={file.url} target="_blank">
                      {file.name}
                    </a>
                    <p className="report-subtitle">
                      {typeof file.matching_sentences === 'number'
                        ? `${file.matching_sentences} matched sentences`
                        : 'Matches: N/A'}
                      {typeof file.plagiarism_percentage === 'number'
                        ? ` • ${file.plagiarism_percentage}% plagiarized`
                        : ''}
                    </p>
                  </div>
                  <label className="checkbox">
                    <input
                      type="checkbox"
                      checked={!!checked[file.name]}
                      onChange={(event) =>
                        setChecked((prev) => ({ ...prev, [file.name]: event.target.checked }))
                      }
                    />
                    Checked
                  </label>
                </div>
              ))
            ) : (
              <p className="report-subtitle">No uploads available.</p>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}

export default TeacherDashboard
