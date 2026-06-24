import { useEffect, useState } from 'react'
import LoginForm from './components/LoginForm'
import ConversationList from './components/ConversationList'
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
  const [selectedId, setSelectedId] = useState<number | null>(null)

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
    setSelectedId(null)
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
      <div className="app__body">
        <aside className="app__sidebar">
          <ConversationList selectedId={selectedId} onSelect={setSelectedId} />
        </aside>
        <main className="app__main">
          {selectedId === null ? (
            <p className="app__placeholder">Select a conversation, or create a new one.</p>
          ) : (
            <p className="app__placeholder">
              Conversation {selectedId} — the message thread arrives in story 5.7.
            </p>
          )}
        </main>
      </div>
    </div>
  )
}
