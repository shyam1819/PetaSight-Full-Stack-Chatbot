// Auth API client. Same-origin, so the HttpOnly session cookie is set/sent automatically.

export type AuthUser = { id: number; email: string }

export type LoginResult =
  | { ok: true; user: AuthUser }
  | { ok: false; status: number; message: string }

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
