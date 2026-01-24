import './App.css'
import AuthPage from './pages/AuthPage'
import HomePage from './pages/HomePage'
import ReportPage from './pages/ReportPage'
import UploadPage from './pages/UploadPage'
import { routes, useRoute } from './routes'

function App() {
  const route = useRoute()

  if (route === routes.upload) {
    return <UploadPage />
  }
  if (route === routes.report) {
    return <ReportPage />
  }
  if (route === routes.auth) {
    return <AuthPage />
  }
  return <HomePage />
}

export default App
