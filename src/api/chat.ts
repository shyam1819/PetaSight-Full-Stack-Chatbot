// Chat API client (conversations + messages). Same-origin, so the session cookie is sent.

export type Conversation = { id: number; title: string | null; created_at: string }

export type ChatMessage = {
  id: number
  role: 'user' | 'assistant'
  content: string
  bubble_color: string | null
  color_rule: string | null
  created_at: string
}

export async function listConversations(): Promise<Conversation[]> {
  try {
    const res = await fetch('/api/conversations', { credentials: 'same-origin' })
    if (!res.ok) return []
    const data = await res.json()
    return (data.conversations as Conversation[]) ?? []
  } catch {
    return []
  }
}

export type SentTurn = { user_message: ChatMessage; assistant_message: ChatMessage }

export async function sendMessage(conversationId: number, text: string): Promise<SentTurn | null> {
  try {
    const res = await fetch('/api/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ conversation_id: conversationId, text }),
    })
    if (!res.ok) return null
    const data = await res.json()
    return { user_message: data.user_message, assistant_message: data.assistant_message }
  } catch {
    return null
  }
}

export async function getHistory(conversationId: number): Promise<ChatMessage[]> {
  try {
    const res = await fetch(`/api/messages?conversation_id=${conversationId}`, {
      credentials: 'same-origin',
    })
    if (!res.ok) return []
    const data = await res.json()
    return (data.messages as ChatMessage[]) ?? []
  } catch {
    return []
  }
}

export async function createConversation(title?: string): Promise<Conversation | null> {
  try {
    const res = await fetch('/api/conversations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(title ? { title } : {}),
    })
    if (!res.ok) return null
    const data = await res.json()
    return (data.conversation as Conversation) ?? null
  } catch {
    return null
  }
}
