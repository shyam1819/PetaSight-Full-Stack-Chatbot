import { useEffect, useRef, useState } from 'react'
import LoginForm from './components/LoginForm'
import ConversationList from './components/ConversationList'
import ChatPanel from './components/ChatPanel'
import { getMe, logout, type AuthUser } from './api/auth'

type State =
  | { phase: 'loading' }
  | { phase: 'anon' }
  | { phase: 'authed'; user: AuthUser }

// Gate on the session, then a collapsible-sidebar chat shell. Default view is a fresh
// "new chat" (selectedId = null) with the composer ready.
export default function App() {
  const [state, setState] = useState<State>({ phase: 'loading' })
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [listVersion, setListVersion] = useState(0)
  const [confirmingLogout, setConfirmingLogout] = useState(false)
  const cancelRef = useRef<HTMLButtonElement>(null)

  // Move focus into the dialog when it opens (accessibility).
  useEffect(() => {
    if (confirmingLogout) cancelRef.current?.focus()
  }, [confirmingLogout])

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
    setSidebarOpen(true)
    setState({ phase: 'anon' })
  }

  function handleConversationCreated(id: number) {
    setSelectedId(id)
    setListVersion((v) => v + 1) // refresh the sidebar to show the new conversation
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
        <button
          type="button"
          className="app__toggle"
          aria-expanded={sidebarOpen}
          aria-controls="sidebar"
          aria-label={sidebarOpen ? 'Hide conversations' : 'Show conversations'}
          onClick={() => setSidebarOpen((o) => !o)}
        >
          ☰
        </button>
        <span className="app__brand">PetaSight Chat</span>
        <span className="app__user" title={state.user.email}>
          {state.user.email}
        </span>
      </header>

      <div className="app__body">
        {sidebarOpen && (
          <aside id="sidebar" className="app__sidebar">
            <div className="sidebar__list">
              <ConversationList selectedId={selectedId} onSelect={setSelectedId} reloadKey={listVersion} />
            </div>
            <div className="sidebar__account">
              <button
                type="button"
                className="sidebar__logout"
                onClick={() => setConfirmingLogout(true)}
              >
                Log out
              </button>
            </div>
          </aside>
        )}
        <main className="app__main">
          <ChatPanel conversationId={selectedId} onConversationCreated={handleConversationCreated} />
        </main>
      </div>

      {confirmingLogout && (
        <div className="modal" onClick={() => setConfirmingLogout(false)}>
          <div
            className="modal__box"
            role="dialog"
            aria-modal="true"
            aria-labelledby="logout-title"
            onClick={(e) => e.stopPropagation()}
            onKeyDown={(e) => {
              if (e.key === 'Escape') setConfirmingLogout(false)
            }}
          >
            <h2 id="logout-title" className="modal__title">
              Log out?
            </h2>
            <p className="modal__text">Are you sure you want to log out?</p>
            <div className="modal__actions">
              <button
                type="button"
                className="modal__cancel"
                ref={cancelRef}
                onClick={() => setConfirmingLogout(false)}
              >
                Cancel
              </button>
              <button type="button" className="modal__confirm" onClick={handleLogout}>
                Log out
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
