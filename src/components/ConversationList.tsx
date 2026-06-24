import { useEffect, useState } from 'react'
import { listConversations, type Conversation } from '../api/chat'

type Props = {
  selectedId: number | null
  onSelect: (id: number | null) => void
  reloadKey: number
}

export default function ConversationList({ selectedId, onSelect, reloadKey }: Props) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)

  // Reloads on mount and whenever reloadKey changes (e.g. a new chat was just created).
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
  }, [reloadKey])

  return (
    <nav className="conversations" aria-label="Conversations">
      <button
        type="button"
        className="conversations__new"
        aria-current={selectedId === null ? 'true' : undefined}
        onClick={() => onSelect(null)}
      >
        + New chat
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
