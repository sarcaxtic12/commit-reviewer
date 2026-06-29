"""Git handler module for commit-reviewer.

Responsible for cloning remote repositories and extracting commit history.
"""

import shutil
import tempfile
import click
import git

def get_local_commits(path: str, limit: int) -> list[dict]:
    """Retrieve recent commits from a local git repository.

    Args:
        path: Path to the local git repository.
        limit: Maximum number of commits to retrieve.

    Returns:
        A list of dictionaries representing the commits.
    """
    try:
        repo = git.Repo(path, search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        raise click.ClickException(f"Not a valid git repository: {path}")
    except git.exc.NoSuchPathError:
        raise click.ClickException(f"Path does not exist: {path}")

    commits = []
    try:
        for commit in repo.iter_commits(max_count=limit):
            commits.append({
                "hash": commit.hexsha[:7],
                "message": commit.message.strip(),
                "author": commit.author.name,
                "timestamp": commit.committed_datetime.isoformat(),
            })
    except (git.exc.GitCommandError, ValueError):
        # Catch errors if it's a newly initialized repository with no commits
        raise click.ClickException("No commits found in this repository.")

    return commits

def get_remote_commits(url: str, limit: int) -> list[dict]:
    """Clone a remote repository to a temp directory and retrieve its recent commits.

    Args:
        url: URL of the remote Git repository.
        limit: Maximum number of commits to retrieve.

    Returns:
        A list of dictionaries representing the commits.
    """
    tmp_dir = tempfile.mkdtemp()
    try:
        git.Repo.clone_from(url, tmp_dir)
        return get_local_commits(tmp_dir, limit)
    except git.exc.GitCommandError:
        raise click.ClickException("Failed to clone repo. Check the URL and your internet connection.")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
