import { useEffect, useState } from 'react'
import { getHistory, type ChatMessage } from '../api/chat'
import { readableTextColor } from '../lib/contrast'

export default function MessageThread({ conversationId }: { conversationId: number }) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    setLoading(true)
    getHistory(conversationId).then((items) => {
      if (active) {
        setMessages(items)
        setLoading(false)
      }
    })
    return () => {
      active = false
    }
  }, [conversationId])

  if (loading) {
    return (
      <p className="thread__status" role="status" aria-live="polite">
        Loading messages…
      </p>
    )
  }

  if (messages.length === 0) {
    return <p className="thread__status">No messages yet. Send one to get started.</p>
  }

  return (
    <ul className="thread" aria-label="Messages">
      {messages.map((m) => {
        // Assistant bubbles carry the engine's colour; text colour is derived for readability.
        const style =
          m.role === 'assistant' && m.bubble_color
            ? { background: m.bubble_color, color: readableTextColor(m.bubble_color) }
            : undefined
        return (
          <li key={m.id} className={`bubble bubble--${m.role}`} style={style}>
            {m.content}
          </li>
        )
      })}
    </ul>
  )
}
