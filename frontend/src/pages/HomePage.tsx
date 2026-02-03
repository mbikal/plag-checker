import { useMemo, useState } from 'react'
import { navigate, routes } from '../routes'
import reportImage from '../assets/report.svg'
import scanImage from '../assets/scan.svg'
import libraryImage from '../assets/library.svg'

function HomePage() {
  const isLoggedIn = useMemo(
    () => localStorage.getItem('plagchecker.session') === 'true',
    [],
  )
  const [showReport, setShowReport] = useState(false)

  return (
    <div className="page">
      <div className="orb orb-one" aria-hidden="true" />
      <div className="orb orb-two" aria-hidden="true" />

      <header className="topbar">
        <button className="brand" type="button" onClick={() => navigate(routes.home)}>
          <span className="brand-mark">PC</span>
          <div>
            <p className="brand-title">Plag Checker</p>
            <p className="brand-subtitle">Plagiarism detection with clear reporting</p>
          </div>
        </button>
        <button
          className="ghost-button"
          type="button"
          onClick={() => navigate(isLoggedIn ? routes.upload : routes.auth)}
        >
          {isLoggedIn ? 'Go to upload' : 'Sign in'}
        </button>
      </header>

      <main className="home">
        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">Academic integrity toolkit</p>
            <h1>Detect similarity, protect originality, and keep work credible.</h1>
            <p>
              Plag Checker scans documents against indexed sources, highlights matches, and delivers
              transparent similarity reports you can trust.
            </p>
            <div className="hero-actions">
              <button
                className="submit"
                type="button"
                onClick={() => navigate(isLoggedIn ? routes.upload : routes.auth)}
              >
                {isLoggedIn ? 'Continue scan' : 'Get started'}
              </button>
              <button
                className="outline-button"
                type="button"
                onClick={() => setShowReport(true)}
              >
                View sample report
              </button>
            </div>
          </div>
          <div className="hero-media">
            <div className="hero-card">
              <img src={reportImage} alt="Report preview" />
              <div>
                <p className="hero-title">Similarity snapshot</p>
                <p className="hero-note">Flagged passages with source links.</p>
              </div>
            </div>
            <div className="hero-card">
              <img src={scanImage} alt="Scanning illustration" />
              <div>
                <p className="hero-title">Deep scan engine</p>
                <p className="hero-note">Finds close paraphrases and overlaps.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="home-grid">
          <article className="media-card">
            <img src={libraryImage} alt="Source library" />
            <h3>Source library coverage</h3>
            <p>Check against academic sources, open web, and internal archives.</p>
          </article>
          <article className="media-card">
            <img src={scanImage} alt="Match tracker" />
            <h3>Match tracker</h3>
            <p>Track flagged segments and export reports for reviewers.</p>
          </article>
          <article className="media-card">
            <img src={reportImage} alt="Ready report" />
            <h3>Share-ready reports</h3>
            <p>Download clean summaries for students, faculty, and teams.</p>
          </article>
        </section>
      </main>

      {showReport ? (
        <div className="modal-backdrop" role="dialog" aria-modal="true">
          <div className="modal">
            <div className="modal-header">
              <div>
                <p className="modal-title">Sample report</p>
                <p className="report-subtitle">Similarity scan summary</p>
              </div>
              <button className="ghost-button" type="button" onClick={() => setShowReport(false)}>
                Close
              </button>
            </div>
            <div className="modal-body">
              <div className="report-card">
                <h3>Overall similarity</h3>
                <p className="similarity-score">18%</p>
                <p className="report-subtitle">8 matched sentences • 42 total sentences</p>
              </div>
              <div className="report-card">
                <h3>Top sources</h3>
                <div className="source-row">
                  <span>Open Web: Example.edu</span>
                  <span>7%</span>
                </div>
                <div className="source-row">
                  <span>Journal archive</span>
                  <span>5%</span>
                </div>
                <div className="source-row">
                  <span>Internal submissions</span>
                  <span>6%</span>
                </div>
              </div>
              <div className="report-card">
                <h3>Flagged passages</h3>
                <ul className="flag-list">
                  <li>Paragraph 2 • Similar phrasing with Example.edu</li>
                  <li>Paragraph 4 • Overlap with journal abstract</li>
                  <li>Paragraph 7 • Paraphrased from internal archive</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}

export default HomePage
