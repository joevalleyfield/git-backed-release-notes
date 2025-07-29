import re

# Verb list can be extended
DIRECTIVE_RE = re.compile(
    r"(?i)\b(?:fix(?:es|ed)?|close[sd]?|resolve[sd]?|implement[sd]?)\b[:]?\s+(#[\w\-_]+)"
)

SLUG_RE = re.compile(r"#([\w\-_]+)")

def extract_issue_slugs(message: str) -> tuple[str | None, list[str]]:
    all_matches = SLUG_RE.findall(message)
    primary = None

    directive_match = DIRECTIVE_RE.search(message)
    if directive_match:
        primary = directive_match.group(1)[1:]  # Strip leading "#"

    return primary, list(dict.fromkeys(all_matches))  # Deduplicate, preserve order