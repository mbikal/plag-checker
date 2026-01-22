import './App.css'
import AuthPage from './pages/AuthPage'
import HomePage from './pages/HomePage'
import UploadPage from './pages/UploadPage'
import { routes, useRoute } from './routes'

function App() {
  const route = useRoute()

  if (route === routes.upload) {
    return <UploadPage />
  }
  if (route === routes.auth) {
    return <AuthPage />
  }
  return <HomePage />
}

export default App
