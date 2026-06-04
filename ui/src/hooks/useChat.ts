/** Custom hook managing chat state — messages, streaming, session. */

import { useCallback, useRef, useState } from "react";
import { streamChat } from "../api/chat";
import type { MessageItem } from "../api/types";

interface UseChatOptions {
  repoRoot?: string;
}

interface UseChatReturn {
  messages: MessageItem[];
  isStreaming: boolean;
  error: string | null;
  sessionId: string | null;
  sendMessage: (query: string) => Promise<void>;
  clearMessages: () => void;
  restoreSession: (sessionId: string, msgs: MessageItem[]) => void;
}

export function useChat(opts?: UseChatOptions): UseChatReturn {
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (query: string) => {
      setError(null);
      setIsStreaming(true);

      const userMsg: MessageItem = { role: "user", content: query };
      setMessages((prev) => [...prev, userMsg]);

      // placeholder assistant message
      const assistantIdx = messages.length + 1;
      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      const abort = new AbortController();
      abortRef.current = abort;

      try {
        let fullAnswer = "";

        for await (const event of streamChat(
          {
            query,
            session_id: sessionId ?? undefined,
            repo_root: opts?.repoRoot ?? ".",
          },
          abort.signal,
        )) {
          if ("error" in event) {
            setError(event.error);
            break;
          }
          if ("delta" in event) {
            fullAnswer += event.delta;
            setMessages((prev) => {
              const next = [...prev];
              next[assistantIdx] = { role: "assistant", content: fullAnswer };
              return next;
            });
          }
          if ("done" in event && event.done) {
            setSessionId(event.session_id);
          }
        }
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === "AbortError") return;
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setIsStreaming(false);
        abortRef.current = null;
      }
    },
    [sessionId, messages, opts?.repoRoot],
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    setError(null);
  }, []);

  const restoreSession = useCallback(
    (sid: string, msgs: MessageItem[]) => {
      setSessionId(sid);
      setMessages(msgs);
      setError(null);
    },
    [],
  );

  return {
    messages,
    isStreaming,
    error,
    sessionId,
    sendMessage,
    clearMessages,
    restoreSession,
  };
}
