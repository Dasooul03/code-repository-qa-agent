/** Quota API — GET /quota. */

import { apiGet } from "./client";

export interface DailyTokenUsage {
  used: number;
  limit: number | null;
  date: string;
}

export interface QuotaUsage {
  daily_tokens: DailyTokenUsage;
  chat_calls: { used: number; limit: number | null };
  embedding_calls: { used: number; limit: number | null };
}

export async function getQuota(): Promise<QuotaUsage> {
  return apiGet<QuotaUsage>("/quota");
}
