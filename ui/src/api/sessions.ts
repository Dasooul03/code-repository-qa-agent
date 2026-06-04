/** Session API — GET /session/{id}. Sessions are created by POST /chat. */

import { apiGet } from "./client";
import type { SessionResponse } from "./types";

export async function getSession(sessionId: string): Promise<SessionResponse> {
  return apiGet<SessionResponse>(`/session/${sessionId}`);
}
