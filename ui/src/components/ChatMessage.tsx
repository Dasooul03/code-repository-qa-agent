/** Renders a single chat message with Markdown formatting and code citations. */

import type { MessageItem } from "../api/types";
import { renderMarkdown } from "./Markdown";
import { useI18n } from "../i18n";

interface ChatMessageProps {
  message: MessageItem;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const { t } = useI18n();
  const isUser = message.role === "user";

  return (
    <div className={`chat-message ${isUser ? "chat-message--user" : "chat-message--assistant"}`}>
      <div className="chat-message__role">{isUser ? t("chat.you") : t("chat.assistant")}</div>
      <div className="chat-message__content">
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <div className="answer-content">
            {renderMarkdown(message.content)}
          </div>
        )}
      </div>
    </div>
  );
}
