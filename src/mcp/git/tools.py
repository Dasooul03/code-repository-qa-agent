"""Git MCP tool implementations."""

import subprocess
from typing import Any


def _run_git(args: list[str], repo_root: str, timeout: int = 15) -> dict[str, Any]:
    """Run a git command and return stdout or an error dict."""
    cmd = ["git", "-C", repo_root] + args
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if proc.returncode != 0:
            return {"error": proc.stderr.strip() or "git command failed"}
        return {"output": proc.stdout.strip()}
    except subprocess.TimeoutExpired:
        return {"error": "git command timed out"}
    except FileNotFoundError:
        return {"error": "git executable not found"}


def git_log(
    repo_root: str,
    path: str = "",
    n: int = 20,
    since: str = "",
    author: str = "",
) -> dict[str, Any]:
    """Return the git commit log, optionally scoped to a file or author.

    Args:
        repo_root: Absolute path to the repository root.
        path: Optional file path to scope the log.
        n: Maximum number of commits to return.
        since: Optional ISO date string (e.g. '2024-01-01').
        author: Optional author name/email filter.

    Returns:
        Dict with keys: commits (list of dicts) or error.
    """
    args = ["log", f"-{n}", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=short"]
    if since:
        args += [f"--since={since}"]
    if author:
        args += [f"--author={author}"]
    if path:
        args += ["--", path]

    result = _run_git(args, repo_root)
    if "error" in result:
        return result

    commits: list[dict[str, str]] = []
    for line in result["output"].splitlines():
        if not line.strip():
            continue
        parts = line.split("|", 4)
        if len(parts) == 5:
            commits.append(
                {
                    "hash": parts[0],
                    "author": parts[1],
                    "email": parts[2],
                    "date": parts[3],
                    "subject": parts[4],
                }
            )
    return {"commits": commits, "path": path}


def git_blame(repo_root: str, path: str) -> dict[str, Any]:
    """Return per-line blame information for a file.

    Args:
        repo_root: Absolute path to the repository root.
        path: Relative file path to blame.

    Returns:
        Dict with keys: path, lines (list of dicts with hash/author/date/line/content).
    """
    if not path:
        return {"error": "path is required for git blame"}

    result = _run_git(
        ["blame", "--line-porcelain", path],
        repo_root,
    )
    if "error" in result:
        return result

    lines: list[dict[str, str]] = []
    current: dict[str, str] = {}
    line_no = 0
    for raw in result["output"].splitlines():
        if raw.startswith("\t"):
            line_no += 1
            lines.append(
                {
                    "line_no": str(line_no),
                    "hash": current.get("hash", ""),
                    "author": current.get("author", ""),
                    "date": current.get("author-time", ""),
                    "content": raw[1:],
                }
            )
            current = {}
        elif " " in raw:
            key, _, val = raw.partition(" ")
            if key == "author":
                current["author"] = val
            elif key in ("author-time", "hash"):
                current[key] = val
            elif len(key) == 40 and all(c in "0123456789abcdef" for c in key):
                current["hash"] = key

    return {"path": path, "lines": lines}


def git_diff(
    repo_root: str,
    path: str = "",
    ref_a: str = "HEAD~1",
    ref_b: str = "HEAD",
) -> dict[str, Any]:
    """Return the diff between two refs, optionally scoped to a file.

    Args:
        repo_root: Absolute path to the repository root.
        path: Optional file path to scope the diff.
        ref_a: Base ref (default: HEAD~1).
        ref_b: Target ref (default: HEAD).

    Returns:
        Dict with keys: ref_a, ref_b, path, diff (unified diff text) or error.
    """
    args = ["diff", ref_a, ref_b]
    if path:
        args += ["--", path]

    result = _run_git(args, repo_root)
    if "error" in result:
        return result

    return {"ref_a": ref_a, "ref_b": ref_b, "path": path, "diff": result["output"]}
