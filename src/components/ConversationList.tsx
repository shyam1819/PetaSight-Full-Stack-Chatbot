import { useEffect, useState } from 'react'
import { createConversation, listConversations, type Conversation } from '../api/chat'

type Props = {
  selectedId: number | null
  onSelect: (id: number) => void
}

export default function ConversationList({ selectedId, onSelect }: Props) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    let active = true
    listConversations().then((items) => {
      if (active) {
        setConversations(items)
        setLoading(false)
      }
    })
    return () => {
      active = false
    }
  }, [])

  async function handleCreate() {
    setCreating(true)
    const convo = await createConversation()
    setCreating(false)
    if (convo) {
      setConversations((prev) => [convo, ...prev])
      onSelect(convo.id)
    }
  }

  return (
    <nav className="conversations" aria-label="Conversations">
      <button type="button" className="conversations__new" onClick={handleCreate} disabled={creating}>
        {creating ? 'Creating…' : '+ New conversation'}
      </button>

      {loading ? (
        <p className="conversations__status" role="status" aria-live="polite">
          Loading…
        </p>
      ) : conversations.length === 0 ? (
        <p className="conversations__status">No conversations yet.</p>
      ) : (
        <ul className="conversations__list">
          {conversations.map((c) => (
            <li key={c.id}>
              <button
                type="button"
                className="conversations__item"
                aria-current={c.id === selectedId ? 'true' : undefined}
                onClick={() => onSelect(c.id)}
              >
                {c.title || `Conversation ${c.id}`}
              </button>
            </li>
          ))}
        </ul>
      )}
    </nav>
  )
}
