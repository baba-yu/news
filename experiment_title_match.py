"""Dry-run experiment: title-based vs summary-based IDF matching.

One-shot exploration spawned from moushiokuri-rename-future-titles.md
§ matcher fix (a). NOT a production skill — delete after evaluation.

For each prediction in the active corpus (2026-04-19 .. 2026-05-04),
run _pick_theme_per_scope twice (once on title, once on summary) and
diff the resulting scope assignments. Highlights cases where the
matcher output differs.

Usage:
    python experiment_title_match.py
    python experiment_title_match.py --pid prediction.9d68206f94f7d87d
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

# Reuse the production matcher implementation directly so the experiment
# stays honest — any drift would invalidate the comparison.
from app.src.ingest import (
    SECONDARY_SCOPE_MIN_RATIO,
    ThemeRow,
    _load_themes,
    _pick_theme_per_scope,
    _idf_score,
    _theme_keywords,
    _tokens,
)


REPO_ROOT = Path(__file__).resolve().parent
DB_PATH = REPO_ROOT / "app" / "data" / "analytics.sqlite"
SOURCEDATA_DIR = REPO_ROOT / "app" / "sourcedata"


def load_predictions() -> list[dict]:
    """Return all predictions across dated sourcedata directories.

    Each entry has: id, title, summary, scope_hint, prediction_date.
    """
    out: list[dict] = []
    for date_dir in sorted(SOURCEDATA_DIR.iterdir()):
        if not date_dir.is_dir() or not date_dir.name.startswith("2026"):
            continue
        pf = date_dir / "predictions.json"
        if not pf.is_file():
            continue
        data = json.loads(pf.read_text(encoding="utf-8"))
        for p in data.get("predictions", []):
            out.append(
                {
                    "id": p["id"],
                    "title": p.get("title", ""),
                    "summary": p.get("summary", ""),
                    "scope_hint": p.get("scope_hint"),
                    "prediction_date": data["date"],
                }
            )
    return out


def score_per_theme(text: str, themes: list[ThemeRow]) -> dict[str, float]:
    """Run IDF scoring against every theme. Returns {theme_id: score}."""
    tokens = _tokens(text)
    theme_tokens = [_theme_keywords(t) for t in themes]
    df: dict[str, int] = {}
    for ts in theme_tokens:
        for tok in ts:
            df[tok] = df.get(tok, 0) + 1
    return {
        t.theme_id: _idf_score(tokens, tt, df)
        for t, tt in zip(themes, theme_tokens)
    }


def summarize_pick(picked: dict[str, ThemeRow]) -> str:
    if not picked:
        return "(no match)"
    parts = []
    for scope, theme in picked.items():
        parts.append(f"{scope}:{theme.theme_id}")
    return ", ".join(parts)


def primary_scope(picked: dict[str, ThemeRow], scores_by_scope: dict[str, float]) -> str | None:
    """Return the scope whose top theme has the highest IDF score."""
    if not picked:
        return None
    return max(picked.keys(), key=lambda s: scores_by_scope.get(s, 0.0))


def run(args: argparse.Namespace) -> int:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    themes = _load_themes(conn)
    conn.close()

    preds = load_predictions()
    if args.pid:
        preds = [p for p in preds if p["id"] == args.pid]
        if not preds:
            print(f"FAIL: no prediction with id={args.pid}", file=sys.stderr)
            return 1

    diff_count = 0
    flip_count = 0  # primary scope flipped

    for p in preds:
        # Run both matchings.
        picked_summary = _pick_theme_per_scope(p["summary"], themes)
        picked_title = _pick_theme_per_scope(p["title"], themes)

        # Compute per-scope top score for primary determination.
        all_scores_summary = score_per_theme(p["summary"], themes)
        all_scores_title = score_per_theme(p["title"], themes)
        top_per_scope_summary = {
            s: max(
                (all_scores_summary[t.theme_id] for t in themes if t.scope_id == s),
                default=0.0,
            )
            for s in {"tech", "business"}
        }
        top_per_scope_title = {
            s: max(
                (all_scores_title[t.theme_id] for t in themes if t.scope_id == s),
                default=0.0,
            )
            for s in {"tech", "business"}
        }

        primary_summary = primary_scope(picked_summary, top_per_scope_summary)
        primary_title = primary_scope(picked_title, top_per_scope_title)

        differs = (
            primary_summary != primary_title
            or set(picked_summary.keys()) != set(picked_title.keys())
        )
        flipped = primary_summary != primary_title and primary_summary and primary_title

        if differs:
            diff_count += 1
        if flipped:
            flip_count += 1

        if args.only_diff and not differs:
            continue
        if args.only_flip and not flipped:
            continue

        # Print compact comparison.
        title_short = p["title"][:70] + ("..." if len(p["title"]) > 70 else "")
        print(f"\n[{p['prediction_date']}] {p['id']}  hint={p['scope_hint']}")
        print(f"  title: {title_short}")
        print(
            f"  SUMMARY-match -> primary={primary_summary} "
            f"scopes={list(picked_summary.keys())} "
            f"top={top_per_scope_summary}"
        )
        print(
            f"    picks: {summarize_pick(picked_summary)}"
        )
        print(
            f"  TITLE-match   -> primary={primary_title} "
            f"scopes={list(picked_title.keys())} "
            f"top={top_per_scope_title}"
        )
        print(
            f"    picks: {summarize_pick(picked_title)}"
        )
        if flipped:
            print(f"  >> FLIPPED: {primary_summary} -> {primary_title}")

    n = len(preds)
    print(f"\n=== Summary ===")
    print(f"  predictions evaluated: {n}")
    print(f"  differing (any): {diff_count}/{n}")
    print(f"  primary-scope flips: {flip_count}/{n}")
    return 0


def find_tech_dropouts() -> int:
    """Find predictions where hint suggests tech but summary-match drops tech.

    Two failure modes worth flagging:
      A. hint in {tech, cross} AND summary-match primary == business
         (matcher overrules a tech-leaning LLM hint)
      B. hint in {tech, cross} AND tech is missing from the picked set
         (the prediction won't appear in tech graph at all)
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    themes = _load_themes(conn)
    conn.close()
    preds = load_predictions()

    tech_intent = [p for p in preds if p["scope_hint"] in ("tech", "cross")]

    flipped: list[dict] = []  # primary != tech
    dropped: list[dict] = []  # tech not in picked scopes

    for p in tech_intent:
        picked = _pick_theme_per_scope(p["summary"], themes)
        all_scores = score_per_theme(p["summary"], themes)
        top_per_scope = {
            s: max(
                (all_scores[t.theme_id] for t in themes if t.scope_id == s),
                default=0.0,
            )
            for s in {"tech", "business"}
        }
        primary = primary_scope(picked, top_per_scope)
        scopes_kept = list(picked.keys())
        rec = {
            "id": p["id"],
            "date": p["prediction_date"],
            "title": p["title"],
            "hint": p["scope_hint"],
            "primary": primary,
            "scopes": scopes_kept,
            "tech_score": top_per_scope["tech"],
            "biz_score": top_per_scope["business"],
            "tech_pick": picked.get("tech").theme_id if "tech" in picked else None,
            "biz_pick": picked.get("business").theme_id if "business" in picked else None,
        }
        if primary != "tech":
            flipped.append(rec)
        if "tech" not in scopes_kept:
            dropped.append(rec)

    print(f"=== Predictions with tech-leaning hint (tech|cross): {len(tech_intent)} ===\n")

    print(f"--- (A) Matcher made primary != tech ({len(flipped)} cases) ---")
    for r in flipped:
        title = r["title"][:75] + ("..." if len(r["title"]) > 75 else "")
        margin = r["biz_score"] - r["tech_score"]
        print(
            f"  [{r['date']}] hint={r['hint']:8s} primary={r['primary']:8s} "
            f"scores tech={r['tech_score']:.2f} biz={r['biz_score']:.2f} (biz-tech={margin:+.2f})"
        )
        print(f"    title: {title}")
        print(f"    picks: tech={r['tech_pick']} biz={r['biz_pick']}")

    print(f"\n--- (B) Tech entirely dropped (won't appear in tech graph) "
          f"({len(dropped)} cases) ---")
    for r in dropped:
        title = r["title"][:75] + ("..." if len(r["title"]) > 75 else "")
        print(
            f"  [{r['date']}] hint={r['hint']:8s} scopes={r['scopes']} "
            f"tech={r['tech_score']:.2f} biz={r['biz_score']:.2f}"
        )
        print(f"    title: {title}")

    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--pid", help="Limit to a single prediction id")
    p.add_argument("--only-diff", action="store_true", help="Print only differing rows")
    p.add_argument("--only-flip", action="store_true", help="Print only primary-flipped rows")
    p.add_argument(
        "--tech-dropouts",
        action="store_true",
        help="Find predictions where hint=tech|cross but matcher demoted tech",
    )
    args = p.parse_args()
    if args.tech_dropouts:
        return find_tech_dropouts()
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
