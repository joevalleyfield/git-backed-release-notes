import logging
import re

logger = logging.getLogger(__name__)


# Directives followed by optional `#`, a slug, and optional `.md`
DIRECTIVE_RE = re.compile(
    r"""
    \b
    (?P<verb>
        (?i:fix(?:es|ed)?
        |close[sd]?
        |resolve[sd]?
        |implement(?:ed|s)?
        |open(?:ed|s)?)
    )
    \b[:]?
    \s+
    \#?
    (?P<slug>
        [a-z0-9]+(?:-[a-z0-9]+)*
    )
    (?:\.md)?          # optional .md
    (?!\.\w)           # no other extension allowed
    \b
    """,
    re.VERBOSE,
)


SLUG_RE = re.compile(
    r"""
    (?:Fixes|Mentions|Implements|Touches|References|Touch)?    # optional prefix
    [^\w#-]*                                                   # optional junk separator
    (?:
        \#(?P<hash>[a-z0-9][a-z0-9_-]*)                        # #slug or #slug.md
        (?:\.md)?                                              # optional .md
      |
        (?P<md>[a-z0-9][a-z0-9_-]*)\.md                        # bare.md
      |
        (?P<kabob>[a-z0-9]+(?:-[a-z0-9]+)+)                    # kabob-case
    )
    """,
    re.VERBOSE,
)


def extract_issue_slugs(message: str) -> tuple[str | None, list[str]]:
    directive_matches = list(DIRECTIVE_RE.finditer(message))
    logger.debug("directive_matches={}".format((directive_matches,)))
    directive_match = min(directive_matches, key=lambda m: m.start()) if directive_matches else None
    primary = directive_match.group("slug") if directive_match else None

    all_matches = []
    for m in SLUG_RE.finditer(message):
        for val in m.groups():
            if val:
                all_matches.append(val)
                break

    return primary, list(dict.fromkeys(all_matches))
