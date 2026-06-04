/** Chat SSE streaming — reads POST /chat as an SSE event stream. */

import type { ChatRequest, ChatStreamEvent } from "./types";
import { apiEventStream } from "./client";

export async function* streamChat(
  req: ChatRequest,
  signal?: AbortSignal,
): AsyncGenerator<ChatStreamEvent> {
  const url = apiEventStream("/chat");
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify(req),
    signal,
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`POST /chat ${res.status}: ${detail}`);
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() ?? ""; // keep incomplete chunk

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed.startsWith("data: ")) continue;

      try {
        const data = JSON.parse(trimmed.slice(6)) as ChatStreamEvent;
        yield data;
      } catch {
        // skip malformed JSON
      }
    }
  }

  // flush remaining buffer
  if (buffer.trim().startsWith("data: ")) {
    try {
      const data = JSON.parse(buffer.trim().slice(6)) as ChatStreamEvent;
      yield data;
    } catch {
      // skip
    }
  }
}
