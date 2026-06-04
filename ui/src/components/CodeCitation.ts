/** Parse file:start-end citations from agent answer text. */

export interface Citation {
  file: string;
  startLine: number;
  endLine: number;
}

// Matches patterns like `file.py:42-56` or `src/main.go:10-25`
const CITATION_RE = /([\w./\\\-]+):(\d+)-(\d+)/g;

// Pattern for # path:start-end lines
const HASH_CITATION_RE = /^#\s+([\w./\\\-]+):(\d+)-(\d+)$/gm;

/** Extract all citations from an answer string, deduplicated. */
export function extractCitations(text: string): Citation[] {
  const seen = new Set<string>();
  const citations: Citation[] = [];

  // First try hash-style lines
  let match: RegExpExecArray | null;
  const hashRe = new RegExp(HASH_CITATION_RE.source, "gm");
  while ((match = hashRe.exec(text)) !== null) {
    const key = `${match[1]}:${match[2]}-${match[3]}`;
    if (!seen.has(key)) {
      seen.add(key);
      citations.push({
        file: match[1],
        startLine: Number(match[2]),
        endLine: Number(match[3]),
      });
    }
  }

  // Then inline citations in code blocks or text
  const inlineRe = new RegExp(CITATION_RE.source, "g");
  while ((match = inlineRe.exec(text)) !== null) {
    const key = `${match[1]}:${match[2]}-${match[3]}`;
    if (!seen.has(key)) {
      seen.add(key);
      citations.push({
        file: match[1],
        startLine: Number(match[2]),
        endLine: Number(match[3]),
      });
    }
  }

  return citations;
}

/** Split answer text into segments — plain text and citation markers. */
export type AnswerSegment =
  | { type: "text"; content: string }
  | { type: "citation"; citation: Citation };

export function segmentAnswer(text: string): AnswerSegment[] {
  const segments: AnswerSegment[] = [];
  const parts = text.split(/([\w./\\\-]+:\d+-\d+)/g);

  for (const part of parts) {
    const m = part.match(/^([\w./\\\-]+):(\d+)-(\d+)$/);
    if (m) {
      segments.push({
        type: "citation",
        citation: { file: m[1], startLine: Number(m[2]), endLine: Number(m[3]) },
      });
    } else if (part) {
      segments.push({ type: "text", content: part });
    }
  }

  return segments;
}
