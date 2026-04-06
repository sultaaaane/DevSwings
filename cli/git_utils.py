import os
import subprocess
from typing import List, Dict, Any, Optional


def is_git_repo(path: str = ".") -> bool:
    """Check if the path is a git repository."""
    try:
        subprocess.check_output(
            ["git", "rev-parse", "--is-inside-work-tree"],
            stderr=subprocess.STDOUT,
            cwd=path,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_git_commits(limit: int = 10, path: str = ".") -> List[Dict[str, str]]:
    """Get the latest commits from the current repository."""
    if not is_git_repo(path):
        return []

    try:
        # Format: hash|subject|timestamp
        output = subprocess.check_output(
            ["git", "log", f"-n {limit}", "--pretty=format:%H|%s|%ct"],
            stderr=subprocess.STDOUT,
            cwd=path,
        ).decode("utf-8")

        commits = []
        for line in output.split("\n"):
            if not line:
                continue
            sha, message, timestamp = line.split("|")
            commits.append(
                {
                    "sha": sha,
                    "message": message,
                    "created_at": timestamp,  # We might need to handle ISO format on server though
                }
            )
        return commits
    except Exception:
        return []


def get_repo_remote_url(path: str = ".") -> Optional[str]:
    """Get the remote origin URL of the git repository."""
    if not is_git_repo(path):
        return None
    try:
        return (
            subprocess.check_output(
                ["git", "config", "--get", "remote.origin.url"],
                stderr=subprocess.STDOUT,
                cwd=path,
            )
            .decode("utf-8")
            .strip()
        )
    except Exception:
        return None


def get_last_commit_sha(path: str = ".") -> Optional[str]:
    """Get the SHA of the most recent commit."""
    if not is_git_repo(path):
        return None
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], stderr=subprocess.STDOUT, cwd=path
            )
            .decode("utf-8")
            .strip()
        )
    except Exception:
        return None
