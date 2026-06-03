"""Tests for git MCP tools."""

from unittest.mock import MagicMock, patch

from src.mcp.git.tools import git_blame, git_diff, git_log


def test_git_log_returns_commits() -> None:
    fake_output = "abc1234|Alice|alice@example.com|2024-01-01|Initial commit"
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=fake_output, stderr="")
        result = git_log("/repo")
    assert len(result["commits"]) == 1
    assert result["commits"][0]["hash"] == "abc1234"
    assert result["commits"][0]["author"] == "Alice"
    assert result["commits"][0]["subject"] == "Initial commit"


def test_git_log_error_propagates() -> None:
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="not a git repo"
        )
        result = git_log("/repo")
    assert "error" in result


def test_git_blame_parses_output() -> None:
    porcelain = "abc1234 1 1 1\nauthor Bob\nauthor-time 1700000000\n\tsome code here\n"
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=porcelain, stderr="")
        result = git_blame("/repo", "foo.py")
    assert result["path"] == "foo.py"
    assert len(result["lines"]) == 1
    assert result["lines"][0]["content"] == "some code here"


def test_git_blame_requires_path() -> None:
    result = git_blame("/repo", "")
    assert "error" in result


def test_git_diff_returns_diff() -> None:
    fake_diff = "diff --git a/foo.py b/foo.py\n--- a/foo.py\n+++ b/foo.py"
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=fake_diff, stderr="")
        result = git_diff("/repo")
    assert result["diff"] == fake_diff
    assert result["ref_a"] == "HEAD~1"
    assert result["ref_b"] == "HEAD"


def test_git_diff_timeout_returns_error() -> None:
    import subprocess

    with patch(
        "subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=15)
    ):
        result = git_diff("/repo")
    assert "error" in result
