/** Simple Markdown �?JSX renderer.
 *
 * Handles: headings, bold, italic, inline code, code blocks,
 * bullet/numbered lists, paragraphs, and file:line citations.
 * Does NOT handle HTML, tables, images, or nested inline formatting.
 */

import React from "react";

// Matches file.py:10-42 style citations


/** Escape HTML in plain text to prevent injection. */
function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

/** Render Markdown text into React nodes. */
export function renderMarkdown(md: string): React.ReactNode {
  const lines = md.split("\n");
  const nodes: React.ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // ── code fence (```) ──────────────────────────────
    if (line.trimStart().startsWith("```")) {
      const lang = line.trimStart().slice(3).trim();
      i++;
      const codeLines: string[] = [];
      while (i < lines.length && !lines[i].trimStart().startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // skip closing ```
      nodes.push(
        <pre key={nodes.length} className="md-code-block">
          {lang && <span className="md-code-lang">{lang}</span>}
          <code>{escapeHtml(codeLines.join("\n"))}</code>
        </pre>,
      );
      continue;
    }

    // ── blank line �?paragraph separator ──────────────
    if (line.trim() === "") {
      i++;
      continue;
    }

    // ── heading ───────────────────────────────────────
    const hMatch = line.match(/^(#{1,4})\s+(.*)/);
    if (hMatch) {
      const level = hMatch[1].length;
      const text = renderInline(hMatch[2]);
      const Tag = `h${level}` as keyof React.JSX.IntrinsicElements;
      nodes.push(
        <Tag key={nodes.length} className="md-heading">
          {text}
        </Tag>,
      );
      i++;
      continue;
    }

    // ── bullet list ───────────────────────────────────
    if (/^[\-\*]\s+/.test(line)) {
      const items: React.ReactNode[] = [];
      while (i < lines.length && /^[\-\*]\s+/.test(lines[i])) {
        const itemText = lines[i].replace(/^[\-\*]\s+/, "");
        items.push(
          <li key={items.length} className="md-li">
            {renderInline(itemText)}
          </li>,
        );
        i++;
      }
      nodes.push(
        <ul key={nodes.length} className="md-ul">
          {items}
        </ul>,
      );
      continue;
    }

    // ── numbered list ─────────────────────────────────
    if (/^\d+\.\s+/.test(line)) {
      const items: React.ReactNode[] = [];
      while (i < lines.length && /^\d+\.\s+/.test(lines[i])) {
        const itemText = lines[i].replace(/^\d+\.\s+/, "");
        items.push(
          <li key={items.length} className="md-li">
            {renderInline(itemText)}
          </li>,
        );
        i++;
      }
      nodes.push(
        <ol key={nodes.length} className="md-ol">
          {items}
        </ol>,
      );
      continue;
    }

    // ── paragraph (collect contiguous non-empty lines) ─
    const paraLines: string[] = [];
    while (
      i < lines.length &&
      lines[i].trim() !== "" &&
      !lines[i].trimStart().startsWith("```") &&
      !/^(#{1,4})\s+/.test(lines[i]) &&
      !/^[\-\*]\s+/.test(lines[i]) &&
      !/^\d+\.\s+/.test(lines[i])
    ) {
      paraLines.push(lines[i]);
      i++;
    }
    if (paraLines.length > 0) {
      nodes.push(
        <p key={nodes.length} className="md-p">
          {renderInline(paraLines.join("\n"))}
        </p>,
      );
    }
  }

  return <>{nodes}</>;
}

/** Render inline Markdown: **bold**, *italic*, `code`, citations, line breaks. */
export function renderInline(text: string): React.ReactNode {
  // Split by inline code first
  const parts = text.split(/(`[^`]+`)/g);
  return parts.map((seg, i) => {
    if (seg.startsWith("`") && seg.endsWith("`")) {
      return <code key={i}>{escapeHtml(seg.slice(1, -1))}</code>;
    }
    // Render **bold** and *italic* with a simple regex split
    return <span key={i}>{renderFormatted(seg)}</span>;
  });
}

/** Render bold/italic/citation within a plain text snippet. */
function renderFormatted(text: string): React.ReactNode {
  const result: React.ReactNode[] = [];
  let remaining = text;
  let key = 0;

  while (remaining.length > 0) {
    // Try citation first
    const citMatch = remaining.match(/^([\w./\\\-]+):(\d+)-(\d+)([,\s]?)/);
    if (citMatch) {
      const [full, file, start, end, trailing] = citMatch;
      result.push(
        <code key={key++} className="citation-chip" title={`${file}:${start}-${end}`}>
          {file}:{start}-{end}
        </code>,
      );
      if (trailing) result.push(trailing);
      remaining = remaining.slice(full.length);
      continue;
    }

    // Try **bold**
    const boldMatch = remaining.match(/^\*\*(.+?)\*\*/);
    if (boldMatch) {
      result.push(<strong key={key++}>{boldMatch[1]}</strong>);
      remaining = remaining.slice(boldMatch[0].length);
      continue;
    }

    // Try *italic* (but not **)
    const italicMatch = remaining.match(/^\*(.+?)\*/);
    if (italicMatch) {
      result.push(<em key={key++}>{italicMatch[1]}</em>);
      remaining = remaining.slice(italicMatch[0].length);
      continue;
    }

    // Plain text until next special char
    const nextSpecial = remaining.search(/[*`]|[\w./\\\-]+:\d+-\d+/);
    if (nextSpecial === -1) {
      // Check for citation without anchor (global search)
      const gCit = remaining.match(/([\w./\\\-]+:\d+-\d+)/);
      if (gCit && gCit.index !== undefined) {
        if (gCit.index > 0) {
          result.push(remaining.slice(0, gCit.index));
        }
        const [full, cit] = gCit;
        const m = cit.match(/^([\w./\\\-]+):(\d+)-(\d+)$/);
        if (m) {
          result.push(
            <code key={key++} className="citation-chip" title={cit}>
              {cit}
            </code>,
          );
        } else {
          result.push(full);
        }
        remaining = remaining.slice(gCit.index + full.length);
        continue;
      }
      result.push(remaining);
      break;
    }
    result.push(remaining.slice(0, nextSpecial));
    remaining = remaining.slice(nextSpecial);
  }

  return <>{result}</>;
}
