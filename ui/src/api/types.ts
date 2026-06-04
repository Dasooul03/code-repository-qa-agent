/** Shared types used across the API layer. */

export interface MessageItem {
  role: "user" | "assistant";
  content: string;
}

export interface SessionResponse {
  session_id: string;
  messages: MessageItem[];
}

export interface RegisterResponse {
  repo_path: string;
  status: string;
}

export interface ChatRequest {
  query: string;
  session_id?: string;
  repo_root?: string;
}

/** SSE event from the chat stream. */
export type ChatStreamEvent =
  | { delta: string }
  | { done: true; session_id: string }
  | { error: string };
