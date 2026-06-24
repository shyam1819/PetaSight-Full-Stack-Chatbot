import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from 'react'
import { createConversation, getHistory, sendMessage, type ChatMessage } from '../api/chat'
import { bubbleStyle } from '../lib/contrast'

type Props = {
  conversationId: number | null // null = a fresh "new chat" draft
  onConversationCreated: (id: number) => void
}

export default function ChatPanel({ conversationId, onConversationCreated }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [text, setText] = useState('')
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const endRef = useRef<HTMLDivElement>(null)
  const selfCreatedRef = useRef<number | null>(null)
  const tempIdRef = useRef(-1)

  // Load history when the selected conversation changes — but skip the one we just created
  // locally (a one-shot), so the optimistic messages aren't wiped.
  useEffect(() => {
    if (conversationId === null) {
      setMessages([])
      selfCreatedRef.current = null
      return
    }
    if (conversationId === selfCreatedRef.current) {
      selfCreatedRef.current = null
      return
    }
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

  // Keep the composer focused (new chat or after load) — never the messages.
  useEffect(() => {
    if (!loading) inputRef.current?.focus()
  }, [loading, conversationId])

  // Scroll the latest into view (scroll only — does NOT move focus).
  useEffect(() => {
    endRef.current?.scrollIntoView({ block: 'end' })
  }, [messages, generating])

  async function handleSend(event?: FormEvent) {
    event?.preventDefault()
    const trimmed = text.trim()
    if (!trimmed || generating) return
    setText('')
    setError(null)

    // Optimistic: show the user's message immediately, then a typing indicator below it.
    const tempUser: ChatMessage = {
      id: tempIdRef.current--,
      role: 'user',
      content: trimmed,
      bubble_color: null,
      color_rule: null,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, tempUser])
    setGenerating(true)

    let cid = conversationId
    if (cid === null) {
      const convo = await createConversation(trimmed.slice(0, 40))
      if (!convo) {
        setGenerating(false)
        setError('Could not start the conversation. Please try again.')
        setMessages((prev) => prev.filter((m) => m.id !== tempUser.id))
        inputRef.current?.focus()
        return
      }
      cid = convo.id
      selfCreatedRef.current = cid // tell the load effect to skip the upcoming prop change
      onConversationCreated(cid)
    }

    const turn = await sendMessage(cid, trimmed)
    setGenerating(false)
    if (turn) {
      setMessages((prev) =>
        prev
          .map((m) => (m.id === tempUser.id ? turn.user_message : m))
          .concat(turn.assistant_message),
      )
    } else {
      setError('Could not send your message. Please try again.')
      setMessages((prev) => prev.filter((m) => m.id !== tempUser.id))
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
    <section className="chat" aria-label="Conversation">
      <div className="chat__messages">
        {loading ? (
          <p className="thread__status" role="status" aria-live="polite">
            Loading messages…
          </p>
        ) : messages.length === 0 && !generating ? (
          <p className="thread__status">Start a new chat — type your first message below.</p>
        ) : (
          <ul className="thread" aria-label="Messages" role="log">
            {messages.map((m) => {
              const style =
                m.role === 'assistant' && m.bubble_color ? bubbleStyle(m.bubble_color) : undefined
              return (
                <li key={m.id} className={`bubble bubble--${m.role}`} style={style}>
                  {m.content}
                </li>
              )
            })}
            {generating && (
              <li className="bubble bubble--assistant bubble--loading" aria-label="Assistant is typing">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </li>
            )}
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
        <button type="submit" className="composer__send" disabled={generating || !text.trim()}>
          {generating ? 'Sending…' : 'Send'}
        </button>
      </form>
      <p className="composer__error" role="status" aria-live="polite">
        {error ?? ''}
      </p>
    </section>
  )
}
