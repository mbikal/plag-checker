import { useMemo, useState } from 'react'
import { navigate, routes } from '../routes'

function DatabasePage() {
  const role = useMemo(() => localStorage.getItem('plagchecker.role') || '', [])
  const adminUsername = useMemo(() => localStorage.getItem('plagchecker.username') || '', [])
  const [adminPassword, setAdminPassword] = useState('')
  const [files, setFiles] = useState<string[]>([])
  const [status, setStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const apiBase =
    (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') ||
    window.location.origin

  const loadCorpus = async () => {
    setStatus(null)
    setError(null)
    try {
      const res = await fetch(`${apiBase}/admin/corpus/list`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          admin_username: adminUsername,
          admin_password: adminPassword,
        }),
      })
      const data = (await res.json()) as { files?: string[]; error?: string }
      if (!res.ok) {
        setError(data.error || 'Unable to load corpus.')
        return
      }
      setFiles(data.files || [])
      setStatus('Corpus list updated.')
    } catch {
      setError('Unable to reach the server.')
    }
  }

  const uploadCorpus = async () => {
    if (!uploadFile) {
      setError('Select a PDF file to upload.')
      return
    }
    setStatus(null)
    setError(null)
    try {
      const form = new FormData()
      form.append('admin_username', adminUsername)
      form.append('admin_password', adminPassword)
      form.append('file', uploadFile)
      const res = await fetch(`${apiBase}/admin/corpus/upload`, {
        method: 'POST',
        body: form,
      })
      const data = (await res.json()) as { message?: string; error?: string }
      if (!res.ok) {
        setError(data.error || 'Unable to upload file.')
        return
      }
      setStatus(data.message || 'Corpus file uploaded.')
      setUploadFile(null)
      loadCorpus()
    } catch {
      setError('Unable to reach the server.')
    }
  }

  const deleteCorpus = async (filename: string) => {
    setStatus(null)
    setError(null)
    try {
      const res = await fetch(`${apiBase}/admin/corpus/delete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          admin_username: adminUsername,
          admin_password: adminPassword,
          filename,
        }),
      })
      const data = (await res.json()) as { message?: string; error?: string }
      if (!res.ok) {
        setError(data.error || 'Unable to delete file.')
        return
      }
      setStatus(data.message || 'Corpus file deleted.')
      loadCorpus()
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
            <p className="brand-subtitle">Database management</p>
          </div>
        </button>
        <button className="ghost-button" type="button" onClick={() => navigate(routes.admin)}>
          Back to admin
        </button>
      </header>

      <main className="content">
        <section className="intro">
          <h1>Database management</h1>
          <p>Manage corpus files, database backups, and storage policies here.</p>
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
            <button className="scan-button" type="button" onClick={loadCorpus}>
              Load corpus
            </button>
          </div>

          <div className="dropdown-panel spaced-section">
            <label className="field">
              <span>Upload PDF to corpus</span>
              <input
                type="file"
                accept="application/pdf"
                onChange={(event) => setUploadFile(event.target.files?.[0] || null)}
              />
            </label>
            <button className="submit" type="button" onClick={uploadCorpus}>
              Upload file
            </button>
          </div>

          {status ? <p className="success">{status}</p> : null}
          {error ? <p className="scan-error">{error}</p> : null}

          <div className="uploads-list">
            {files.length ? (
              files.map((name) => (
                <div className="user-row" key={name}>
                  <a
                    className="upload-link"
                    href={`${apiBase}/admin/corpus/file/${encodeURIComponent(name)}?admin_username=${encodeURIComponent(
                      adminUsername,
                    )}&admin_password=${encodeURIComponent(adminPassword)}`}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {name}
                  </a>
                  <button className="ghost-button" type="button" onClick={() => deleteCorpus(name)}>
                    Delete
                  </button>
                </div>
              ))
            ) : (
              <p className="report-subtitle">No corpus files found.</p>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}

export default DatabasePage
