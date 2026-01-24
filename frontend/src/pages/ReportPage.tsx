import { useMemo } from 'react'
import { navigate, routes } from '../routes'

type ScanReport = Record<string, unknown>

function ReportPage() {
  const report = useMemo(() => {
    const raw = localStorage.getItem('plagchecker.report')
    return raw ? (JSON.parse(raw) as ScanReport) : null
  }, [])
  const pdfUrl = typeof report?.pdf_url === 'string' ? report.pdf_url : null
  const matchingSentences = (() => {
    const value = report?.matching_sentences
    if (typeof value === 'number') {
      return value
    }
    if (typeof value === 'string') {
      const parsed = Number(value)
      return Number.isFinite(parsed) ? parsed : null
    }
    return null
  })()
  const totalSentences = (() => {
    const value = report?.total_sentences
    if (typeof value === 'number') {
      return value
    }
    if (typeof value === 'string') {
      const parsed = Number(value)
      return Number.isFinite(parsed) ? parsed : null
    }
    return null
  })()
  const sentenceMatchPercent =
    matchingSentences !== null && totalSentences
      ? Math.round((matchingSentences / totalSentences) * 100)
      : null

  return (
    <div className="page">
      <div className="orb orb-one" aria-hidden="true" />
      <div className="orb orb-two" aria-hidden="true" />

      <header className="topbar">
        <button className="brand" type="button" onClick={() => navigate(routes.home)}>
          <span className="brand-mark">PC</span>
          <div>
            <p className="brand-title">Plag Checker</p>
            <p className="brand-subtitle">Similarity report</p>
          </div>
        </button>
        <button className="ghost-button" type="button" onClick={() => navigate(routes.upload)}>
          New scan
        </button>
      </header>

      <main className="content">
        <section className="intro">
          <h1>Scan results</h1>
          <p>Review the similarity matches and export results for reporting.</p>
        </section>
        <section className="panel">
          {report ? (
            <div className="report-view">
              {pdfUrl ? (
                <iframe className="pdf-preview" title="Similarity report" src={pdfUrl} />
              ) : (
                <p className="scan-error">PDF report unavailable.</p>
              )}
              <div className="report">
                <p className="report-title">Matching sentences</p>
                <p className="similarity-score">
                  {matchingSentences !== null ? matchingSentences : 'N/A'}
                </p>
                <p className="report-subtitle">
                  {totalSentences !== null ? `${totalSentences} total sentences` : 'Total sentences N/A'}
                </p>
                <p className="report-subtitle">
                  {sentenceMatchPercent !== null ? `${sentenceMatchPercent}% matched` : 'Match rate N/A'}
                </p>
              </div>
            </div>
          ) : (
            <div className="report-empty">
              <p>No report found yet. Run a scan first.</p>
              <button className="submit" type="button" onClick={() => navigate(routes.upload)}>
                Go to upload
              </button>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default ReportPage
