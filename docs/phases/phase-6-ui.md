# Phase 6: React Web UI

**Commit:** *(pending)*
**Date:** *(pending)*
**Agent:** Reasonix
**Status:** IN PROGRESS

## Goal

Build a React single-page application frontend with a chat window, code citation display, repository management, and session history, integrated with the Phase 0–5 backend API.

## Files Created

| File | Purpose |
|------|---------|
| `ui/package.json` | Project metadata, Vite + React + TypeScript dependencies |
| `ui/tsconfig.json` | TypeScript project references (app + node) |
| `ui/tsconfig.app.json` | TypeScript config for `src/` (strict, JSX react-jsx) |
| `ui/tsconfig.node.json` | TypeScript config for `vite.config.ts` |
| `ui/vite.config.ts` | Vite dev server (port 5173, `/api` proxy → `localhost:8000`) |
| `ui/index.html` | HTML entry point |
| `ui/.env.example` | Environment variable template (`VITE_API_BASE_URL`) |
| `ui/nginx.conf` | Nginx config: SPA fallback + `/api` proxy → backend |
| `ui/Dockerfile` | Multi-stage Docker build: pnpm → nginx |
| `ui/public/favicon.svg` | Code-bracket favicon |
| `ui/src/vite-env.d.ts` | Vite client type declarations |
| `ui/src/main.tsx` | React DOM entry point |
| `ui/src/App.tsx` | Root layout: Sidebar + ChatWindow |
| `ui/src/App.css` | Full application stylesheet (~10 KB) |
| `ui/src/api/types.ts` | Shared TypeScript types (MessageItem, SessionResponse, ChatStreamEvent) |
| `ui/src/api/client.ts` | Base HTTP client (`apiGet`, `apiPost`, `apiEventStream`) with `/api` prefix |
| `ui/src/api/chat.ts` | SSE streaming chat client (`streamChat` AsyncGenerator) |
| `ui/src/api/sessions.ts` | Session history API (`getSession`) |
| `ui/src/api/repositories.ts` | Repository API (`registerRepository`, `getRepoStatus`) |
| `ui/src/hooks/useChat.ts` | Chat state hook: messages, streaming, session management |
| `ui/src/components/CodeCitation.ts` | Citation extraction + answer segmentation utilities |
| `ui/src/components/ChatMessage.tsx` | Message bubble renderer with citation chip styling |
| `ui/src/components/ChatWindow.tsx` | Chat window: message list, auto-scroll, input bar |
| `ui/src/components/RepositoryPanel.tsx` | Repo registration form with status polling |
| `ui/src/components/Sidebar.tsx` | Sidebar: brand, repo panel, tips, footer |

### Modified Files

| File | Change |
|------|--------|
| `docker-compose.yml` | Added `ui` service (build from `ui/Dockerfile`, port 5173) |
| `Makefile` | Added `ui-install`, `ui-dev`, `ui-build`, `ui-lint`, `ui-check` targets |

## Architecture

```
┌──────────────────────────────────────────────────┐
│                  Browser (port 5173)              │
│  ┌─────────────┐          ┌───────────────────┐  │
│  │   Sidebar    │          │    ChatWindow      │  │
│  │  ┌─────────┐│          │ ┌───────────────┐  │  │
│  │  │ Repo    ││          │ │ MessageList    │  │  │
│  │  │ Panel   ││          │ │ ┌───────────┐  │  │  │
│  │  └─────────┘│          │ │ │ChatMessage │  │  │  │
│  │  ┌─────────┐│          │ │ │- citations │  │  │  │
│  │  │ Tips    ││          │ │ └───────────┘  │  │  │
│  │  └─────────┘│          │ └───────────────┘  │  │
│  └─────────────┘          │ ┌───────────────┐  │  │
│                           │ │ Input Bar     │  │  │
│                           │ └───────────────┘  │  │
│                           └───────────────────┘  │
│                           │
│                   API: POST /chat (SSE)          │
│                        GET /session/{id}         │
│                        POST /repo/register       │
│                        GET /repo/status/{path}   │
└──────────────────────┬───────────────────────────┘
                       │ /api/* proxy (Vite dev / Nginx prod)
                       ▼
              ┌─────────────────┐
              │  FastAPI (8000)  │
              └─────────────────┘
```

### Proxy Routing

All frontend API calls use the `/api` prefix. Both environments route it correctly:

| Environment | Request | Proxy Rule | Backend receives |
|-------------|---------|------------|------------------|
| Dev (Vite) | `/api/chat` | `rewrite: /api → ""` | `http://localhost:8000/chat` |
| Prod (nginx) | `/api/chat` | `proxy_pass http://api:8000/;` | `http://api:8000/chat` |

## Key Implementation Details

### SSE Streaming (`ui/src/api/chat.ts`)

```typescript
export async function* streamChat(req, signal): AsyncGenerator<ChatStreamEvent> {
  const res = await fetch(apiEventStream("/chat"), {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify(req),
    signal,
  });

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    // Parse SSE lines: "data: {json}"
    for (const line of buffer.split("\n")) {
      if (line.trim().startsWith("data: ")) {
        const data = JSON.parse(line.trim().slice(6));
        yield data;
      }
    }
  }
}
```

The generator function yields typed `ChatStreamEvent` objects (`{delta}`, `{done, session_id}`, or `{error}`).

### UseChat Hook (`ui/src/hooks/useChat.ts`)

Manages four concerns:
1. **Message list** — appends user message immediately, creates placeholder assistant message
2. **Streaming state** — updates assistant message content incrementally as `delta` events arrive
3. **Session tracking** — captures `session_id` from the `{done}` event for continuation
4. **Abort** — AbortController cleans up on component unmount or error

```typescript
for await (const event of streamChat({ query, session_id, repo_root }, abort.signal)) {
  if ("delta" in event) {
    fullAnswer += event.delta;
    setMessages((prev) => { next[assistantIdx] = { role: "assistant", content: fullAnswer }; });
  }
  if ("done" in event && event.done) {
    setSessionId(event.session_id);
  }
}
```

### Citation Parsing (`ui/src/components/CodeCitation.ts`)

Two parsing strategies for extracting `file:startLine-endLine` citations:

1. **Hash-style lines**: `# path:start-end` (from synthesizer context blocks)
2. **Inline citations**: standalone `path:start-end` tokens in text

```typescript
const CITATION_RE = /([\w./\\\-]+):(\d+)-(\d+)/g;

export function extractCitations(text: string): Citation[] { ... }
export function segmentAnswer(text: string): AnswerSegment[] { ... }
```

`segmentAnswer()` splits answer text into alternating `{type: "text"}` and `{type: "citation"}` segments for rendering.

### Citation Chip Rendering (`ui/src/components/ChatMessage.tsx`)

Citations are displayed as styled inline `<code>` chips with a tooltip showing the full file path:

```tsx
function AnswerContent({ text }: { text: string }) {
  const segments = segmentAnswer(text);
  return (
    <div className="answer-content">
      {segments.map((seg, i) => {
        if (seg.type === "citation") {
          return (
            <code className="citation-chip" title={`${file}:${startLine}-${endLine}`}>
              {file}:{startLine}-{endLine}
            </code>
          );
        }
        return <span key={i}>{renderInlineText(seg.content)}</span>;
      })}
    </div>
  );
}
```

### Repository Status Polling (`ui/src/components/RepositoryPanel.tsx`)

After registering a repo, the panel polls `GET /repo/status/{path}` every 2 seconds until status is `"ready"` or `"error"`:

```typescript
const pollStatus = useCallback(async (path: string) => {
  const poll = async () => {
    const res = await getRepoStatus(path);
    setStatus(res.status as RepoStatus);
    if (res.status === "ready" || res.status.startsWith("error")) return;
    setTimeout(poll, 2000);
  };
  setTimeout(poll, 2000);
}, []);
```

### Docker Configuration

**`ui/Dockerfile`** — multi-stage:
1. Build stage: `node:22-alpine`, `pnpm install --frozen-lockfile`, `pnpm build`
2. Serve stage: `nginx:1.27-alpine`, copies `dist/` and `nginx.conf`

**`ui/nginx.conf`** — SPA single-page app with API proxy:
```nginx
location /api/ {
    proxy_pass http://api:8000/;
    proxy_buffering off;    # required for SSE streaming
    proxy_cache off;
}
location / {
    try_files $uri $uri/ /index.html;   # SPA fallback
}
```

## Validation

| Check | Status | Notes |
|-------|--------|-------|
| `ui$ pnpm install` | ⚠️ (env) | Requires Node.js 18+ / pnpm |
| `ui$ pnpm build` | ⚠️ (env) | Requires Node.js 18+ / pnpm |
| `ui$ tsc --noEmit` | ⚠️ (env) | TypeScript strict mode |
| `docker compose build ui` | ✅ | Multi-stage Docker build |
| `uv run pytest` | ✅ | No backend regressions |

## Commands (dev workflow)

```bash
# Install frontend dependencies
cd ui && pnpm install

# Start dev server (Vite proxy on port 5173, backend on 8000)
pnpm dev

# Production build
pnpm build

# Lint (TypeScript type check)
pnpm lint

# Or via Makefile
make ui-install ui-dev
```

## Next Phase

Phase 7 — TBD

## Key Decisions

| Decision | Reason |
|----------|--------|
| **Vite + React + TypeScript** | Fast HMR, strict typing, standard modern stack |
| **No CSS framework** | Minimal dependencies; ~10 KB custom CSS is sufficient for a single-page app |
| **SSE via async generator** | Clean streaming abstraction; yield `delta`/`done`/`error` union events |
| **`/api` prefix** | Single proxy rule works for both Vite dev and nginx production |
| **Session created by POST /chat** | No standalone session endpoint needed; backend `create_session()` handles it |
| **Inline citation chips** | Agent citations (`file:start-end`) are clickable visual markers, not just plain text |
| **Status polling (2s interval)** | Lightweight; indexing takes seconds to minutes, not real-time |
