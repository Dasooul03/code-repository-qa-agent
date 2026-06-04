/** Main chat window — message list + input bar. */

import React, { useRef, useEffect, useState } from "react";
import { ChatMessage } from "./ChatMessage";
import type { MessageItem } from "../api/types";
import { useI18n } from "../i18n";

interface ChatWindowProps {
  messages: MessageItem[];
  isStreaming: boolean;
  error: string | null;
  sessionId: string | null;
  onSend: (query: string) => void;
  onClear: () => void;
}

export function ChatWindow({
  messages,
  isStreaming,
  error,
  sessionId,
  onSend,
  onClear,
}: ChatWindowProps) {
  const { t } = useI18n();
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const q = input.trim();
    if (!q || isStreaming) return;
    setInput("");
    onSend(q);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-window">
      {/* Header */}
      <div className="chat-window__header">
        <h2>{t("chat.header")}</h2>
        <div className="chat-window__header-actions">
          {sessionId && (
            <span className="chat-window__session-badge" title="Session ID">
              {sessionId.slice(0, 8)}...
            </span>
          )}
          <button className="btn btn--ghost" onClick={onClear} disabled={isStreaming}>
            {t("chat.clear")}
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-window__messages">
        {messages.length === 0 && (
          <div className="chat-window__empty">
            <p>{t("chat.empty")}</p>
            <p className="text-muted">{t("chat.example")}</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} />
        ))}

        {/* Streaming indicator */}
        {isStreaming && messages[messages.length - 1]?.content === "" && (
          <div className="chat-window__typing">
            <span className="dot-pulse">{t("chat.thinking")}</span>
          </div>
        )}

        {/* Error */}
        {error && <div className="chat-window__error">{error}</div>}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form className="chat-window__input-bar" onSubmit={handleSubmit}>
        <textarea
          ref={inputRef}
          className="chat-window__input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t("chat.placeholder")}
          rows={1}
          disabled={isStreaming}
        />
        <button
          className="btn btn--primary"
          type="submit"
          disabled={!input.trim() || isStreaming}
        >
          {t("chat.send")}
        </button>
      </form>
    </div>
  );
}
