import { useEffect, useState } from 'react'
import LoginForm from './components/LoginForm'
import { getMe, logout, type AuthUser } from './api/auth'

type State =
  | { phase: 'loading' }
  | { phase: 'anon' }
  | { phase: 'authed'; user: AuthUser }

// Story 2.8: gate on the session. Check /api/me once on load so a signed-in user
// stays in across refreshes; an expired/invalid session (401) falls back to login.
// The chat screen itself lands in EP-3/EP-5/EP-6.
export default function App() {
  const [state, setState] = useState<State>({ phase: 'loading' })

  useEffect(() => {
    let active = true
    getMe().then((user) => {
      if (active) setState(user ? { phase: 'authed', user } : { phase: 'anon' })
    })
    return () => {
      active = false
    }
  }, [])

  async function handleLogout() {
    await logout()
    setState({ phase: 'anon' })
  }

  if (state.phase === 'loading') {
    return (
      <main className="auth">
        <p className="auth__loading" role="status" aria-live="polite">
          Loading…
        </p>
      </main>
    )
  }

  if (state.phase === 'anon') {
    return <LoginForm onSuccess={(user) => setState({ phase: 'authed', user })} />
  }

  return (
    <div className="app">
      <header className="app__header">
        <span className="app__brand">PetaSight Chat</span>
        <div className="app__account">
          <span className="app__user">{state.user.email}</span>
          <button type="button" className="app__logout" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </header>
      <main className="app__main">
        <p className="app__placeholder">
          You're signed in. The chat screen arrives with the bubble engine and conversations
          (EP-3 / EP-5 / EP-6).
        </p>
      </main>
    </div>
  )
}
