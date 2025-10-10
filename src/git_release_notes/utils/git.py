"""
Git utility functions for extracting commit metadata from a local repository.

Includes:
- extract_commits_from_git: fallback data source when no spreadsheet is provided.
- get_commit_parents_and_children: Return the parent and child SHAs for a given commit.
"""

import fnmatch
import logging
import re
import subprocess
from collections import defaultdict
from functools import lru_cache
from time import perf_counter
from types import SimpleNamespace
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def run_git(repo_path: str, *args: str, **kwargs) -> subprocess.CompletedProcess:
    """
    Centralized Git runner.

    Returns CompletedProcess, just like subprocess.run.

    Keeps cwd pinned to the repo.
    """
    start = perf_counter()
    cp = subprocess.run(["git", *args], cwd=repo_path, text=True, capture_output=True, **kwargs)

    dt_ms = (perf_counter() - start) * 1000.0
    _record_git_stat(args, dt_ms)
    _maybe_log_slow(args, dt_ms)
    return cp


_git_stats: Dict[Tuple[str, ...], Dict[str, float]] = defaultdict(
    lambda: {"count": 0, "total_ms": 0.0, "max_ms": 0.0}
)


def _record_git_stat(args: Tuple[str, ...], dt_ms: float) -> None:
    s = _git_stats[tuple(args)]
    s["count"] += 1
    s["total_ms"] += dt_ms
    if dt_ms > s["max_ms"]:
        s["max_ms"] = dt_ms


def _maybe_log_slow(args: Tuple[str, ...], dt_ms: float, threshold_ms: float = 150.0) -> None:
    # Adjust threshold_ms if needed, or read from settings/env later.
    if dt_ms >= threshold_ms:
        logger.warning("GIT SLOW (%.1f ms): git %s", dt_ms, " ".join(args))


def get_git_stats(sort_by: str = "total_ms") -> list[tuple[Tuple[str, ...], Dict[str, float]]]:
    """
    Returns a sorted list of (args_tuple, stats_dict) where stats_dict has count/total_ms/max_ms.
    sort_by ∈ {'total_ms','count','max_ms'}
    """
    key = {
        "total_ms": lambda kv: kv[1]["total_ms"],
        "count": lambda kv: kv[1]["count"],
        "max_ms": lambda kv: kv[1]["max_ms"],
    }[sort_by]

    return sorted(_git_stats.items(), key=key, reverse=True)


def reset_git_stats() -> None:
    _git_stats.clear()


def extract_commits_from_git(repo_path: str) -> list[dict]:
    """
    Extract commit metadata directly from the Git repository.

    Returns a list of dictionaries with keys:
    id, sha, release, message, author_date, and touched_paths.
    """
    result = run_git(
        repo_path,
        "log",
        "-z",
        "--name-only",
        "--pretty=format:%H%x09%ad%x09%s%x00",
        "--date=iso",
        check=True,
    )

    logger.debug("raw git log output (escaped): %r", result.stdout)
    tokens = result.stdout.strip("\0").split("\0")

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("split into %d tokens", len(tokens))
        for i, token in enumerate(tokens):
            logger.debug("token[%d]: %r", i, token)

    rows = []
    idx = 0
    i = 0
    while i < len(tokens):
        header = tokens[i]
        if header.count("\t") < 2:
            logger.warning("Skipping malformed header token: %r", header)
            i += 1
            continue

        sha, author_date, message = header.split("\t", 2)
        i += 1

        # Collect touched paths until next header or end
        paths = []
        while i < len(tokens) and tokens[i].count("\t") < 2:
            path = tokens[i].strip()
            if path:
                paths.append(path)
            i += 1

        logger.debug("commit #%d: sha=%s, message=%r, files=%r", idx, sha, message, paths)
        rows.append(
            {
                "id": idx,
                "sha": sha,
                "author_date": author_date,
                "message": message,
                "release": "",
                "touched_paths": paths,
            }
        )
        idx += 1

    return rows


@lru_cache(maxsize=None)
def get_commit_parents_and_children(sha: str, repo_path: str) -> Tuple[List[str], List[str]]:
    """
    Return the parent and child SHAs for a given commit.

    - Parents are obtained directly via `git show`.
    - Children are computed by scanning `git rev-list --all --children`.

    Results are cached by (sha, repo_path).
    """
    parents = _get_parents(sha, repo_path)
    children = _get_children_map(repo_path).get(sha, [])
    return parents, children


def _get_parents(sha: str, repo_path: str) -> List[str]:
    result = run_git(repo_path, "show", "-s", "--format=%P", sha, check=True)
    return result.stdout.strip().split()


@lru_cache(maxsize=1)
def _get_children_map(repo_path: str) -> dict:
    """
    Build a mapping of commit SHA to its list of children.
    Only called once per repo_path (due to lru_cache).
    """
    result = run_git(repo_path, "rev-list", "--all", "--children", check=True)

    children_map = {}
    for line in result.stdout.strip().splitlines():
        parts = line.strip().split()
        if len(parts) > 1:
            parent, *children = parts
            children_map[parent] = children
    return children_map


def get_tag_commit_sha(tag: str, repo_path: str) -> str:
    return run_git(
        repo_path,
        "rev-list",
        "-n",
        "1",
        tag,
        check=True,
    ).stdout.strip


def find_follows_tag(sha: str, repo_path: str, tag_pattern: str) -> SimpleNamespace | None:
    """
    Finds the nearest matching tag that precedes the given commit (excluding its own tag).

    Returns:
        A SimpleNamespace with:
            - base_tag (str): the matching tag name
            - tag_sha (str): commit SHA of the tag
            - count (int): number of commits between the tag and the target
        Returns None if no matching prior tag is found.
    """
    logger.debug("Resolving Follows tag for commit: %s", sha)

    try:
        tag_shas = get_matching_tag_commits(repo_path, tag_pattern)
        if not tag_shas:
            return None

        rev_list = get_topo_ordered_commits(repo_path)
        if sha not in rev_list:
            logger.warning("Commit %s not found in topo-ordered rev-list", sha)
            return None

        i = rev_list.index(sha)
        prior_shas = rev_list[:i][::-1]  # Walk backwards from sha

        for count, ancestor_sha in enumerate(prior_shas, 1):
            if ancestor_sha in tag_shas:
                tag = tag_shas[ancestor_sha]
                logger.debug("Found Follows tag: %s at SHA %s", tag, ancestor_sha)
                return SimpleNamespace(base_tag=tag, tag_sha=ancestor_sha, count=count)

        logger.debug("No Follows tag found before commit %s", sha)
        return None

    except subprocess.SubprocessError as e:
        logger.debug("Error resolving Follows for %s: %s", sha, e)
        return None


def find_precedes_tag(sha: str, repo_path: str, tag_pattern: str) -> SimpleNamespace | None:
    """
    Walks the commit graph forward from the given SHA to find the first descendant
    with a tag matching the given pattern.

    Returns:
        A SimpleNamespace with:
            - base_tag (str): the matching tag name
            - tag_sha (str): commit SHA of the tag
        Returns None if no matching descendant tag is found.
    """
    logger.debug("Resolving Precedes tag for commit: %s", sha)

    try:
        tag_shas = get_matching_tag_commits(repo_path, tag_pattern)

        for tag_commit_sha, tag in tag_shas.items():
            logger.debug("Available tag: %s -> %s", tag, tag_commit_sha)

        if not tag_shas:
            return None

        rev_list = get_topo_ordered_commits(repo_path)

        logger.debug("rev-list contains %d commits", len(rev_list))
        if sha not in rev_list:
            logger.warning("Commit %s not found in rev-list --topo-order --reverse", sha)

        try:
            i = rev_list.index(sha)
        except ValueError:
            return None

        for descendant_sha in rev_list[i + 1 :]:
            logger.debug("Checking descendant SHA: %s", descendant_sha)

            if descendant_sha in tag_shas:
                # Verify this is truly a descendant, not an ancestor or unrelated
                logger.debug(
                    "Running: git merge-base --is-ancestor %s %s",
                    descendant_sha,
                    sha,
                )

                if is_ancestor(descendant_sha, sha, repo_path):
                    logger.debug(
                        "Skipping tag SHA %s — it's actually an ancestor of %s",
                        descendant_sha,
                        sha,
                    )
                    continue

                tag = tag_shas[descendant_sha]
                logger.debug("Found descendant tag: %s at SHA: %s", tag, descendant_sha)

                return SimpleNamespace(base_tag=tag, tag_sha=descendant_sha)

        logger.debug("No matching Precedes tag found for commit: %s", sha)

    except subprocess.SubprocessError as e:
        # Likely due to tag lookup or invalid rev-list index
        logger.debug("Subprocess error during precedes resolution for %s: %s", sha, e)

    return None


def get_describe_name(repo_path: str, sha: str, match: str = "rel-*") -> str | None:
    try:
        result = run_git(
            repo_path,
            "describe",
            "--tags",
            "--match",
            match,
            sha,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


@lru_cache(maxsize=1)
def _get_all_tag_commits(repo_path: str) -> dict[str, str]:
    """
    Return mapping of tag names -> commit SHAs (peeled).
    Cached once per repo_path.
    """
    result = run_git(
        repo_path,
        "for-each-ref",
        "--format=%(refname:strip=2) %(objectname)",
        "refs/tags",
        check=True,
    )
    mapping: dict[str, str] = {}
    for line in result.stdout.strip().splitlines():
        if not line.strip():
            continue
        tag_name, obj = line.split()
        # peel annotated tags if necessary
        peel = run_git(
            repo_path,
            "rev-parse",
            f"{tag_name}^{{}}",
            check=False,
        )
        sha = peel.stdout.strip() if peel.returncode == 0 else obj
        mapping[tag_name] = sha
    return mapping


def get_matching_tag_commits(repo_path: str, pattern: str) -> dict[str, str]:
    """
    Return a mapping of tag commit SHAs to tag names for tags matching the pattern.
    """
    all_tags = _get_all_tag_commits(repo_path)
    tag_shas: dict[str, str] = {}
    for tag_name, sha in all_tags.items():
        if fnmatch.fnmatch(tag_name, pattern):
            tag_shas[sha] = tag_name
    logger.debug("Filtered %d matching tags for pattern '%s'", len(tag_shas), pattern)
    return tag_shas


@lru_cache(maxsize=1)
def get_topo_ordered_commits(repo_path: str) -> list[str]:
    """
    Return all commit SHAs in topological order (oldest to newest).
    """
    result = run_git(
        repo_path,
        "rev-list",
        "--topo-order",
        "--reverse",
        "--all",
        check=True,
    )
    commits = result.stdout.strip().splitlines()
    logger.debug("Loaded %d commits into topo-order cache", len(commits))
    return commits


def is_ancestor(ancestor_sha: str, descendant_sha: str, repo_path: str) -> bool:
    """
    Return True if ancestor_sha is an ancestor of descendant_sha.
    """
    return (
        run_git(
            repo_path,
            "merge-base",
            "--is-ancestor",
            ancestor_sha,
            descendant_sha,
            check=False,
        ).returncode
        == 0
    )


def parse_describe_output(raw: str) -> tuple[str, int] | None:
    """
    Parse the output of `git describe` into a (tag, count) tuple.

    Args:
        raw: A string like "rel-1.2.3-4-gabcdef0" from `git describe`.

    Returns:
        A tuple of (base_tag, count) if the input includes a commit count,
        or None if the input appears to be a direct tag (e.g., "rel-1.2.3").
    """
    m = re.match(r"(.+)-(\d+)-g([0-9a-f]{7,})", raw)
    if m:
        base_tag, count, _ = m.groups()
        return base_tag, int(count)
    return None
