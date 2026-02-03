import { useMemo, useState } from 'react'
import { navigate, routes } from '../routes'

function UploadPage() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState<string | null>(null)
  const username = useMemo(() => {
    return localStorage.getItem('plagchecker.username') || ''
  }, [])
  const role = useMemo(() => {
    return localStorage.getItem('plagchecker.role') || ''
  }, [])
  const handleLogout = () => {
    localStorage.removeItem('plagchecker.username')
    localStorage.removeItem('plagchecker.session')
    localStorage.removeItem('plagchecker.role')
    navigate(routes.auth)
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null
    setSelectedFile(file)
    setReport(null)
    setError(null)
  }

  const handleScan = async () => {
    if (!selectedFile) {
      setError('Please select a file to scan.')
      return
    }

    setLoading(true)
    setError(null)
    setReport(null)

    try {
      const apiBase =
        (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') ||
        window.location.origin
      const formData = new FormData()
      formData.append('file', selectedFile)
      const res = await fetch(`${apiBase}/scan`, {
        method: 'POST',
        body: formData,
      })
      const data = (await res.json()) as Record<string, unknown>
      if (!res.ok) {
        setError((data.error as string) || 'Scan failed.')
      } else {
        setReport(data)
        localStorage.setItem('plagchecker.report', JSON.stringify(data))
        navigate(routes.report)
      }
    } catch {
      setError('Unable to reach the server. Check API URL or backend status.')
    } finally {
      setLoading(false)
    }
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
            <p className="brand-subtitle">Upload a document to generate a similarity report</p>
          </div>
        </button>
        <div className="avatar-wrap">
          <button
            className="avatar"
            type="button"
            onClick={() => setMenuOpen((open) => !open)}
            aria-expanded={menuOpen}
            aria-haspopup="menu"
            aria-label="Account menu"
          >
            <svg className="avatar-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M12 12.2a4.1 4.1 0 1 0-4.1-4.1A4.1 4.1 0 0 0 12 12.2Zm0 1.9c-4 0-7.3 2-7.3 4.4v1.4h14.6v-1.4c0-2.4-3.3-4.4-7.3-4.4Z"
                fill="currentColor"
              />
            </svg>
          </button>
          {menuOpen ? (
            <div className="avatar-menu" role="menu">
              <p className="avatar-name">{username}</p>
              {role === 'admin' ? (
                <button
                  className="logout-button"
                  type="button"
                  onClick={() => navigate(routes.admin)}
                >
                  Admin dashboard
                </button>
              ) : null}
              <button className="logout-button" type="button" onClick={handleLogout}>
                Log out
              </button>
            </div>
          ) : null}
        </div>
      </header>

      <main className="content admin-full">
        <section className="intro">
          <h1>Start a plagiarism scan.</h1>
          <p>
            Upload your document to compare against indexed sources and receive a detailed similarity report.
          </p>
        </section>
        <section className="panel">
          <div className="upload-box">
            <p className="upload-title">Upload a document</p>
            <p className="upload-subtitle">PDF files supported for similarity checks.</p>
            <label className="upload-button">
              <input type="file" accept="application/pdf" onChange={handleFileChange} />
              {selectedFile ? 'Change file' : 'Select file'}
            </label>
            {selectedFile ? <p className="file-name">{selectedFile.name}</p> : null}
            <button className="scan-button" type="button" onClick={handleScan} disabled={loading}>
              {loading ? 'Scanning...' : 'Run scan'}
            </button>
            {error ? <p className="scan-error">{error}</p> : null}
            {report ? (
              <div className="report">
                <p className="report-title">Scan report</p>
                <pre>
                  {JSON.stringify(
                    { ...report, signature: undefined, public_key: undefined },
                    null,
                    2,
                  )}
                </pre>
              </div>
            ) : null}
          </div>
        </section>
      </main>
    </div>
  )
}

export default UploadPage
