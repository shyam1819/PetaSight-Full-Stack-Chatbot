import { useEffect, useState } from 'react'
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
              <button type="button" className="sidebar__logout" onClick={handleLogout}>
                Log out
              </button>
            </div>
          </aside>
        )}
        <main className="app__main">
          <ChatPanel conversationId={selectedId} onConversationCreated={handleConversationCreated} />
        </main>
      </div>
    </div>
  )
}
