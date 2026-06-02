#!/usr/bin/env python3
"""Render README.md from profile.yml, refreshing the live news section.

News is pulled from Google News RSS (no API key required). Everything else is
stdlib except PyYAML (see requirements.txt). Run with:

    python scripts/update_profile.py

The script rewrites the region of README.md between the AUTO-GENERATED markers,
so any text you put outside those markers is preserved.
"""

from __future__ import annotations

import html
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PROFILE_PATH = ROOT / "profile.yml"
README_PATH = ROOT / "README.md"

BEGIN = "<!-- BEGIN AUTO-GENERATED: do not edit by hand, run scripts/update_profile.py -->"
END = "<!-- END AUTO-GENERATED -->"

USER_AGENT = "profile-updater/1.0 (+https://github.com)"
HTTP_TIMEOUT = 20


# ── News fetching ────────────────────────────────────────────────────────────


def fetch_news(topic: str, *, language: str, country: str, limit: int) -> list[dict]:
    """Return recent headlines for a topic via Google News RSS."""
    ceid = f"{country}:{language.split('-')[0]}"
    query = urllib.parse.urlencode(
        {"q": topic, "hl": language, "gl": country, "ceid": ceid}
    )
    url = f"https://news.google.com/rss/search?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            raw = resp.read()
    except Exception as exc:  # network hiccup, rate limit, etc.
        print(f"  ! could not fetch '{topic}': {exc}", file=sys.stderr)
        return []

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        print(f"  ! could not parse feed for '{topic}': {exc}", file=sys.stderr)
        return []

    items = []
    for item in root.findall(".//item")[:limit]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        source = item.findtext("{*}source") or ""
        pub_raw = item.findtext("pubDate") or ""
        if not title or not link:
            continue
        items.append(
            {
                "title": html.unescape(title),
                "link": link,
                "source": html.unescape(source.strip()),
                "published": parse_date(pub_raw),
                "topic": topic,
            }
        )
    return items


def parse_date(raw: str):
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (TypeError, ValueError):
        return None


def gather_news(cfg: dict) -> list[tuple[str, list[dict]]]:
    """Return news grouped as [(heading, items), ...] per config."""
    topics = cfg.get("topics") or []
    per_topic = int(cfg.get("per_topic", 4))
    language = cfg.get("language", "en-US")
    country = cfg.get("country", "US")
    merge = bool(cfg.get("merge", True))
    max_total = int(cfg.get("max_total", 10))

    collected = {}
    for topic in topics:
        print(f"  fetching news for '{topic}'…", file=sys.stderr)
        collected[topic] = fetch_news(
            topic, language=language, country=country, limit=per_topic
        )

    if merge:
        flat = [it for items in collected.values() for it in items]
        # Dedupe by title, newest first.
        seen, deduped = set(), []
        for it in sorted(flat, key=_sort_key, reverse=True):
            key = it["title"].lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(it)
        return [("Latest News", deduped[:max_total])]

    return [(topic, items) for topic, items in collected.items() if items]


def _sort_key(item: dict):
    return item["published"] or datetime.min.replace(tzinfo=timezone.utc)


# ── Rendering ─────────────────────────────────────────────────────────────────


def render_links(links: dict) -> str:
    label_url = [
        ("GitHub", links.get("github")),
        ("Website", links.get("website")),
        ("Twitter/X", links.get("twitter")),
        ("LinkedIn", links.get("linkedin")),
    ]
    parts = [f"[{label}]({url})" for label, url in label_url if url]
    email = links.get("email")
    if email:
        parts.append(f"[Email](mailto:{email})")
    return " · ".join(parts)


def render_news_block(groups: list[tuple[str, list[dict]]]) -> str:
    lines = []
    any_items = False
    for heading, items in groups:
        lines.append(f"### 📰 {heading}\n")
        if not items:
            lines.append("_No headlines available right now._\n")
            continue
        any_items = True
        for it in items:
            meta = []
            if it.get("source"):
                meta.append(it["source"])
            if it.get("published"):
                meta.append(it["published"].strftime("%Y-%m-%d"))
            suffix = f" — _{' · '.join(meta)}_" if meta else ""
            lines.append(f"- [{it['title']}]({it['link']}){suffix}")
        lines.append("")
    if not any_items and groups:
        return "_News feed unavailable right now — will refresh on the next run._\n"
    return "\n".join(lines).strip() + "\n"


def render(profile: dict, news_cfg: dict) -> str:
    p = profile
    links = p.get("links", {})
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    out = []
    out.append(f"# {p.get('name', 'Your Name')}")
    if p.get("tagline"):
        out.append(f"\n> {p['tagline']}")
    meta_bits = []
    if p.get("location"):
        meta_bits.append(f"📍 {p['location']}")
    link_line = render_links(links)
    if link_line:
        meta_bits.append(link_line)
    if meta_bits:
        out.append("\n" + "  \n".join(meta_bits))

    if p.get("about"):
        out.append("\n## About\n")
        out.append(p["about"].strip())

    now_items = p.get("now") or []
    if now_items:
        out.append("\n## What I'm up to\n")
        out.extend(f"- {item}" for item in now_items)

    out.append("\n## News\n")
    groups = gather_news(news_cfg)
    out.append(render_news_block(groups))

    out.append(f"\n---\n_Profile auto-updated on **{now_utc}**._")
    return "\n".join(out).strip() + "\n"


def splice_into_readme(generated: str) -> str:
    block = f"{BEGIN}\n\n{generated}\n{END}"
    if README_PATH.exists():
        text = README_PATH.read_text(encoding="utf-8")
        if BEGIN in text and END in text:
            head = text.split(BEGIN)[0].rstrip()
            tail = text.split(END, 1)[1].lstrip()
            pieces = [p for p in (head, block, tail) if p]
            return "\n\n".join(pieces).strip() + "\n"
    return block + "\n"


def main() -> int:
    if not PROFILE_PATH.exists():
        print(f"profile.yml not found at {PROFILE_PATH}", file=sys.stderr)
        return 1
    data = yaml.safe_load(PROFILE_PATH.read_text(encoding="utf-8")) or {}
    profile = data.get("profile", {})
    news_cfg = data.get("news", {})

    generated = render(profile, news_cfg)
    README_PATH.write_text(splice_into_readme(generated), encoding="utf-8")
    print(f"Wrote {README_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
