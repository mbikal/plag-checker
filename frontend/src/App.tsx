import './App.css'
import AuthPage from './pages/AuthPage'
import HomePage from './pages/HomePage'
import AdminPage from './pages/AdminPage'
import ReportPage from './pages/ReportPage'
import UploadPage from './pages/UploadPage'
import UploadsPage from './pages/UploadsPage'
import UsersPage from './pages/UsersPage'
import DatabasePage from './pages/DatabasePage'
import TeacherDashboard from './pages/TeacherDashboard'
import { routes, useRoute } from './routes'

function App() {
  const route = useRoute()

  if (route === routes.upload) {
    return <UploadPage />
  }
  if (route === routes.admin) {
    return <AdminPage />
  }
  if (route === routes.uploads) {
    return <UploadsPage />
  }
  if (route === routes.users) {
    return <UsersPage />
  }
  if (route === routes.database) {
    return <DatabasePage />
  }
  if (route === routes.dashboard) {
    return <TeacherDashboard />
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
