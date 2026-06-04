/** Repository API — POST /repo/register, GET /repo/status/{path}. */

import { apiGet, apiPost } from "./client";
import type { RegisterResponse } from "./types";

export async function registerRepository(
  repoPath: string,
): Promise<RegisterResponse> {
  return apiPost<RegisterResponse>("/repo/register", { repo_path: repoPath });
}

export async function getRepoStatus(
  repoPath: string,
): Promise<RegisterResponse> {
  return apiGet<RegisterResponse>(`/repo/status/${encodeURIComponent(repoPath)}`);
}
