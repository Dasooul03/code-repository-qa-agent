/** Base API client configuration.
 *
 * In development, Vite proxies /api → http://localhost:8000.
 * In production, nginx proxies /api → api:8000.
 * Set VITE_API_BASE_URL to override (e.g. http://localhost:8000 without proxy).
 */

const BASE = import.meta.env.VITE_API_BASE_URL ?? "";
const API_PREFIX = "/api";

function apiUrl(path: string): string {
  return `${BASE}${API_PREFIX}${path}`;
}

export async function apiGet<T>(path: string): Promise<T> {
  const url = apiUrl(path);
  const res = await fetch(url, {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`GET ${path} ${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export async function apiPost<T>(
  path: string,
  body: unknown,
): Promise<T> {
  const url = apiUrl(path);
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`POST ${path} ${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export function apiEventStream(path: string): string {
  return apiUrl(path);
}
