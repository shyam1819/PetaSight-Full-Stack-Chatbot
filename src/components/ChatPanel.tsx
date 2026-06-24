import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from 'react'
import { getHistory, sendMessage, type ChatMessage } from '../api/chat'
import { readableTextColor } from '../lib/contrast'

// The chat panel: history + composer. Accessibility is the point here —
// focus stays in the composer when a reply appends, and new messages are announced
// via a role="log" live region (so a screen-reader user hears the reply without being moved).
export default function ChatPanel({ conversationId }: { conversationId: number }) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(true)
  const [text, setText] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const endRef = useRef<HTMLDivElement>(null)

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

  // Focus the composer once the conversation is ready — never the messages.
  useEffect(() => {
    if (!loading) inputRef.current?.focus()
  }, [loading, conversationId])

  // Scroll the latest message into view (scrolling only — this does NOT move focus).
  useEffect(() => {
    endRef.current?.scrollIntoView({ block: 'end' })
  }, [messages])

  async function handleSend(event?: FormEvent) {
    event?.preventDefault()
    const trimmed = text.trim()
    if (!trimmed || sending) return
    setSending(true)
    setError(null)
    setText('')
    const turn = await sendMessage(conversationId, trimmed)
    setSending(false)
    if (turn) {
      setMessages((prev) => [...prev, turn.user_message, turn.assistant_message])
    } else {
      setError('Could not send your message. Please try again.')
    }
    // Keep focus in the composer; the appended reply must never steal it.
    inputRef.current?.focus()
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat">
      <div className="chat__messages">
        {loading ? (
          <p className="thread__status" role="status" aria-live="polite">
            Loading messages…
          </p>
        ) : messages.length === 0 ? (
          <p className="thread__status">No messages yet. Send one to get started.</p>
        ) : (
          <ul className="thread" aria-label="Messages" role="log">
            {messages.map((m) => {
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
        )}
        <div ref={endRef} />
      </div>

      <form className="composer" onSubmit={handleSend}>
        <label htmlFor="composer-input" className="sr-only">
          Message
        </label>
        <textarea
          id="composer-input"
          ref={inputRef}
          className="composer__input"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message…  (Enter to send, Shift+Enter for a new line)"
          rows={1}
        />
        <button type="submit" className="composer__send" disabled={sending || !text.trim()}>
          {sending ? 'Sending…' : 'Send'}
        </button>
      </form>
      <p className="composer__error" role="status" aria-live="polite">
        {error ?? ''}
      </p>
    </div>
  )
}
