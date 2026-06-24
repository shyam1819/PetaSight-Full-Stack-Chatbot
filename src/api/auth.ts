// Auth API client. Same-origin, so the HttpOnly session cookie is set/sent automatically.

export type AuthUser = { id: number; email: string }

export type LoginResult =
  | { ok: true; user: AuthUser }
  | { ok: false; status: number; message: string }

// Restore session on load: returns the user if the cookie is still valid, else null
// (a 401 from an expired/invalid session is treated as "not signed in").
export async function getMe(): Promise<AuthUser | null> {
  try {
    const res = await fetch('/api/me', { credentials: 'same-origin' })
    if (res.status !== 200) return null
    const data = await res.json().catch(() => ({}))
    return (data.user as AuthUser) ?? null
  } catch {
    return null
  }
}

export async function logout(): Promise<void> {
  try {
    await fetch('/api/logout', { method: 'POST', credentials: 'same-origin' })
  } catch {
    // Best-effort: the client drops session state regardless.
  }
}

export async function login(email: string, password: string): Promise<LoginResult> {
  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
      credentials: 'same-origin',
    })
    const data = await res.json().catch(() => ({}))
    if (res.ok) return { ok: true, user: data.user as AuthUser }
    return { ok: false, status: res.status, message: data.message ?? 'Sign-in failed.' }
  } catch {
    return { ok: false, status: 0, message: 'Network error — please try again.' }
  }
}
