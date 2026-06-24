import { useState, type FormEvent } from 'react'

type Status =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'ok'; message: string }
  | { kind: 'error'; message: string }

// Task 1: this login page exists only to prove the deploy pipeline and the
// frontend -> /api integration. Real auth/session lands in Task 3.
export default function App() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [status, setStatus] = useState<Status>({ kind: 'idle' })

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setStatus({ kind: 'loading' })
    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      const data = (await res.json()) as { message?: string }
      setStatus(
        res.ok
          ? { kind: 'ok', message: data.message ?? 'Signed in.' }
          : { kind: 'error', message: data.message ?? 'Sign-in failed.' },
      )
    } catch {
      setStatus({ kind: 'error', message: 'Network error — is the backend running?' })
    }
  }

  return (
    <main className="login">
      <h1>PetaSight Chat</h1>
      <form onSubmit={onSubmit} noValidate>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          autoComplete="username"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button type="submit" disabled={status.kind === 'loading'}>
          {status.kind === 'loading' ? 'Signing in…' : 'Sign in'}
        </button>
      </form>

      <p role="status" aria-live="polite" className={`status status--${status.kind}`}>
        {status.kind === 'ok' || status.kind === 'error' ? status.message : ''}
      </p>
    </main>
  )
}
