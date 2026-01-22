import { useMemo, useState } from 'react'
import { navigate, routes } from '../routes'

function UploadPage() {
  const [menuOpen, setMenuOpen] = useState(false)
  const username = useMemo(() => {
    return localStorage.getItem('plagchecker.username') || ''
  }, [])
  const handleLogout = () => {
    localStorage.removeItem('plagchecker.username')
    navigate(routes.auth)
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
              <button className="logout-button" type="button" onClick={handleLogout}>
                Log out
              </button>
            </div>
          ) : null}
        </div>
      </header>

      <main className="content">
        <section className="intro">
          <h1>Start a plagiarism scan.</h1>
          <p>
            Upload your document to compare against indexed sources and receive a detailed similarity report.
          </p>
        </section>
        <section className="panel">
          <div className="upload-box">
            <p className="upload-title">Upload a document</p>
            <p className="upload-subtitle">PDF, DOCX, or TXT files supported for similarity checks.</p>
            <label className="upload-button">
              <input type="file" />
              Select file
            </label>
          </div>
        </section>
      </main>
    </div>
  )
}

export default UploadPage
