import { useState } from 'react'
import LoginForm from './components/LoginForm'
import type { AuthUser } from './api/auth'

// Story 2.7: render the login form. Session-aware gating (check /api/me on load,
// chat screen, logout) arrives in story 2.8.
export default function App() {
  const [user, setUser] = useState<AuthUser | null>(null)

  if (!user) return <LoginForm onSuccess={setUser} />

  return (
    <main className="auth">
      <div className="auth__card">
        <h1 className="auth__title">Signed in</h1>
        <p className="auth__hint">
          You are signed in as <strong>{user.email}</strong>. The chat screen comes next (2.8 / EP-6).
        </p>
      </div>
    </main>
  )
}
