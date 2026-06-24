import { useEffect, useRef, useState, type FormEvent } from 'react'
import { login, type AuthUser } from '../api/auth'

type Status = { kind: 'idle' } | { kind: 'loading' } | { kind: 'error'; message: string }

export default function LoginForm({ onSuccess }: { onSuccess: (user: AuthUser) => void }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [status, setStatus] = useState<Status>({ kind: 'idle' })
  const emailRef = useRef<HTMLInputElement>(null)

  // Focus the first field on load so a keyboard user can type immediately.
  useEffect(() => {
    emailRef.current?.focus()
  }, [])

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setStatus({ kind: 'loading' })
    const result = await login(email, password)
    if (result.ok) onSuccess(result.user)
    else setStatus({ kind: 'error', message: result.message })
  }

  const loading = status.kind === 'loading'
  const invalid = status.kind === 'error'

  return (
    <main className="auth">
      <div className="auth__card">
        <h1 className="auth__title">PetaSight Chat</h1>
        <p className="auth__hint">
          Sign in with your <strong>@petasight.com</strong> email. Your first sign-in creates your account.
        </p>

        <form onSubmit={onSubmit} noValidate aria-busy={loading}>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input
              ref={emailRef}
              id="email"
              name="email"
              type="email"
              autoComplete="username"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
              aria-invalid={invalid}
            />
          </div>

          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              aria-invalid={invalid}
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        {/* Announced to screen readers without stealing focus. */}
        <p className="auth__status" role="status" aria-live="polite">
          {status.kind === 'error' ? status.message : ''}
        </p>
      </div>
    </main>
  )
}
