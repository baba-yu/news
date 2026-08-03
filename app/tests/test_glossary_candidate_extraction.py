"""Tests for candidate extraction — citation URLs must never become terms.

Regression guard for the recurring defect where bare citation hostnames
(`www.microsoft.com`, `zenity.io`, `www.tradingkey.com`, `pypi.org`,
`www.benzinga.com`, `blackhatonsite.informafestivals.com`) were harvested
as glossary candidates and then auto-promoted to `active` on the
`distinct_days_14d >= 3` rule, forcing a hand-retire on each run.

Those strings only ever occur inside link targets, so the extractor blanks
the target before tokenising and additionally rejects bare hostnames that
appear in visible prose or in a link label.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from skills.extract_glossary_candidates import (
    _is_hostname,
    extract_candidates,
    run,
    strip_link_targets,
)
from src import db


# A cut-down news file in the exact shape the daily flow produces: an
# inline `<a href="…">` citation inside the bullet, then the trailing
# reference-link block. Every hostname and path segment below matched the
# old `[a-z]+\.[a-z]+` token shape.
_NEWS_MD = """\
## News


### PyPI stops accepting new files on releases older than 14 days

- PyPI has quietly shut a door that AI tooling keeps walking through.
  <a href="https://blog.pypi.org/posts/2026-07-22-releases-reject-new-files/index.html">On
  July 22 the Python Package Index began rejecting new file uploads</a>, a change
  the Python Software Foundation framed as stripping an attacker of the ability to
  poison a long-stable version. LiteLLM is an LLM gateway wedged into countless
  agent stacks, and the TurboQuant loader ships an install.sh alongside it.
  [PyPI Blog - Releases now reject new files](https://blog.pypi.org/posts/2026-07-22-releases-reject-new-files/index.html),
  [Benzinga - AMD stock analysis](https://www.benzinga.com/markets/26/07/12345/amd-hardware.html),
  [Zenity - AI Agent Security Summit](https://zenity.io/events/summit/default.aspx),
  [Black Hat - AI Summit](https://blackhatonsite.informafestivals.com/register/build.htm),
  [Microsoft - Copilot security baseline](https://www.microsoft.com/en-us/security/blog/setup.sh)
"""


def test_citation_hostnames_are_not_candidates():
    counts = extract_candidates(_NEWS_MD)
    for host in (
        "blog.pypi.org",
        "pypi.org",
        "www.benzinga.com",
        "zenity.io",
        "blackhatonsite.informafestivals.com",
        "www.microsoft.com",
    ):
        assert host not in counts, f"citation hostname harvested as a term: {host}"


def test_url_path_segments_are_not_candidates():
    """The same token shape also matched filenames inside the URL path."""
    counts = extract_candidates(_NEWS_MD)
    for path_token in ("index.html", "default.aspx", "build.htm",
                       "amd-hardware.html", "hardware.html", "setup.sh"):
        assert path_token not in counts, f"URL path segment harvested: {path_token}"


def test_prose_and_link_labels_still_yield_terms():
    """Stripping targets must not cost us the visible text around them."""
    counts = extract_candidates(_NEWS_MD)
    # From prose, from inside the <a> label, and from a reference-link label.
    assert counts.get("PyPI", 0) >= 1
    assert counts.get("LiteLLM", 0) >= 1
    assert counts.get("TurboQuant", 0) >= 1
    assert counts.get("AMD", 0) >= 1
    # `install.sh` is prose here, not a link target — but it is still a
    # filename-shaped token, and `.sh` is a TLD, so the hostname guard
    # takes it. The point of this assertion is that the surrounding prose
    # survived; see the term assertions above.
    assert "install.sh" not in counts


def test_bare_hostname_in_prose_is_rejected():
    """A host typed into a sentence has no URL wrapper to strip."""
    text = "Maintainers moved the advisory feed to pypi.org and www.benzinga.com covered it."
    counts = extract_candidates(text)
    assert "pypi.org" not in counts
    assert "www.benzinga.com" not in counts


def test_dotted_terms_that_are_not_hostnames_survive():
    """A dotted term whose suffix isn't a TLD is untouched by the guard.

    `llama.cpp` is an active glossary term and the only `active` row that
    the `[a-z]+\\.[a-z]+` shape produces, so it is the one that has to keep
    working. (`ASP.NET` is not a counter-example: `_TOKEN_RE`'s all-caps
    alternative claims `ASP` before the dotted alternative is tried, so it
    never reaches the hostname guard as one token.)
    """
    text = "The llama.cpp runtime and torch.compile both shipped fixes."
    counts = extract_candidates(text)
    assert counts.get("llama.cpp", 0) == 1
    assert counts.get("torch.compile", 0) == 1


def test_strip_link_targets_keeps_label_drops_target():
    md = '<a href="https://lwn.net/Articles/1084218/">PyPI now rejects new files</a>'
    stripped = strip_link_targets(md)
    assert "lwn.net" not in stripped
    assert "PyPI now rejects new files" in stripped

    md2 = "[LWN.net - PyPI rejects new files](https://lwn.net/Articles/1084218/)"
    stripped2 = strip_link_targets(md2)
    assert "lwn.net" not in stripped2
    assert "LWN.net - PyPI rejects new files" in stripped2


def test_strip_link_targets_does_not_fuse_neighbours():
    """Targets are replaced with a space, not deleted."""
    assert "fooBar" not in strip_link_targets("[foo](https://example.com)Bar")


@pytest.mark.parametrize(
    "token",
    [
        "www.microsoft.com",
        "zenity.io",
        "www.tradingkey.com",
        "blackhatonsite.informafestivals.com",
        "pypi.org",
        "www.benzinga.com",
        "lwn.net",
        "neurips.cc",
        "blog.google",
        "tech.eu",
        "leginfo.legislature.ca",
        "www.artificialintelligence",  # truncated host — caught by the www rule
    ],
)
def test_is_hostname_true(token):
    assert _is_hostname(token) is True


@pytest.mark.parametrize(
    "token",
    [
        "llama.cpp",      # active glossary term
        "torch.compile",  # `.compile` is not a TLD
        "ASP.NET",        # caps rule: `.net` is a TLD, but hosts are lowercase
        "CHANGELOG.md",   # ditto for `.md`
        "LWN.net",
        "MCP",
        "ATT&CK",
        "CVE-2026-40372",
        "TurboQuant",
    ],
)
def test_is_hostname_false(token):
    assert _is_hostname(token) is False


def test_run_writes_no_hostname_rows(tmp_path: Path):
    """End-to-end: the promotion path never sees a hostname candidate."""
    db_path = tmp_path / "analytics.sqlite"
    db.init_db(db_path)
    news = tmp_path / "news-20260722.md"
    news.write_text(_NEWS_MD, encoding="utf-8")

    summary = run(news, db_path, None)
    assert summary["today"] == "2026-07-22"

    conn = sqlite3.connect(str(db_path))
    terms = {r[0] for r in conn.execute("SELECT term FROM glossary_terms")}
    occurrences = {r[0] for r in conn.execute("SELECT term FROM glossary_occurrences")}
    conn.close()

    assert not [t for t in terms if _is_hostname(t)], "hostname row reached glossary_terms"
    assert not [t for t in occurrences if _is_hostname(t)]
    # And the run did do its job.
    assert {"PyPI", "LiteLLM", "TurboQuant"} <= terms
