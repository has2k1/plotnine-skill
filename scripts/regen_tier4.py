"""Regenerate tier-4 symbol files from plotnine.org.

Workflow
--------
1. Bump ``scripts/plotnine-version.txt`` to the plotnine release you want
   the skill pinned to.
2. Run ``uv run python scripts/regen_tier4.py``.
3. Review the diff. The script emits signature, parameters, and
   aesthetics (where applicable). ``## Examples`` and ``## See Also``
   are hand-curated — the script never touches existing example or
   see-also content beyond stubbing an empty See Also placeholder on
   first run.
4. Commit the pin bump and the regenerated parameter surfaces.

Design notes
------------
* **Source**: scrape ``https://plotnine.org/reference/<symbol>``. The
  rendered pages carry the authoritative signature and parameter
  surface; we don't use docstrings (they're dynamic templates).
* **Cache**: fetched HTML is stashed under
  ``scripts/cache/<version>/<symbol>.html`` so reruns are
  offline-reproducible and diffs are easier to audit.
* **Composability guardrail**: the script extracts each symbol's own
  parameter set from that symbol's page. It must not union a geom's
  parameters with its paired stat's — those live on distinct pages.
* **Examples are not auto-emitted**. Tier-4 examples are seeded from
  hand-curated tier-3 examples and grown over time.
* **URLs are stripped**: the skill is fully offline. Parameter
  descriptions scraped from plotnine.org contain RST-style hyperlink
  references (``<http://example.com>_``) and bare URL tokens; both
  forms are stripped during extraction.
* **Fail loud**: if a page is missing its parameters block or signature
  block, the script raises. A degraded file should not silently land.
"""

from __future__ import annotations

import re
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError

from selectolax.parser import HTMLParser, Node

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "scripts" / "plotnine-version.txt"
CACHE_DIR = ROOT / "scripts" / "cache"
API_DIR = ROOT / "skills" / "plotnine" / "references" / "api"

BASE_URL = "https://plotnine.org/reference"

PREFIXES = ("geom_", "stat_", "scale_", "coord_")


def load_version() -> str:
    return VERSION_FILE.read_text().strip()


def list_symbols() -> list[str]:
    """List every public plotnine symbol starting with an in-scope prefix."""
    import plotnine  # imported lazily — regen is optional on user machines

    return sorted(n for n in dir(plotnine) if n.startswith(PREFIXES))


def fetch_page(symbol: str, version: str) -> str | None:
    """Return HTML for a symbol, or None if the page does not exist.

    Uses an on-disk cache keyed by plotnine version.
    """
    cache_path = CACHE_DIR / version / f"{symbol}.html"
    if cache_path.exists():
        return cache_path.read_text()

    url = f"{BASE_URL}/{symbol}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            html = resp.read().decode("utf-8")
    except HTTPError as e:
        if e.code == 404:
            return None
        raise

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(html)
    return html


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------


@dataclass
class Param:
    name: str
    annotation: str
    default: str
    description: str


@dataclass
class PageContent:
    symbol: str
    summary: str
    signature: str
    params: list[Param]
    aesthetics_block: str  # HTML table from the `mapping` parameter's dd, if any


# URLs come through in scraped descriptions from RST-style hyperlink
# references (`<http://example.com>_` or `<http://example.com>__`) and
# from bare `https://example.com` tokens. The skill is fully offline,
# so strip them out of tier-4 output. Leave residual prose alone — it
# reads fine in context and any resulting "see the documentation ."
# dangling phrase is harmless for a parameter reference.
_URL_RST = re.compile(r"<https?://[^>]+>_*")
_URL_BARE = re.compile(r"https?://\S+")


def _strip_urls(text: str) -> str:
    cleaned = _URL_RST.sub("", text)
    cleaned = _URL_BARE.sub("", cleaned)
    # Collapse whitespace introduced by the removals.
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    # Clean trailing "at ." / ", ." style droppings.
    cleaned = re.sub(r"\s+([.,])", r"\1", cleaned)
    return cleaned


def _text(node: Node | None) -> str:
    return node.text().strip() if node else ""


def _parse_dt(dt: Node) -> tuple[str, str, str]:
    """Return (name, annotation, default) for a parameter <dt>.

    Geom/stat pages wrap each piece in ``doc-parameter-*`` spans.
    Scale/coord pages just put the raw ``name: type = default`` text
    inside a ``<code>`` element. Handle both.
    """
    name_node = dt.css_first("span.doc-parameter-name")
    ann_node = dt.css_first("span.doc-parameter-annotation")
    def_node = dt.css_first("span.doc-parameter-default")
    if name_node:
        return _text(name_node), _text(ann_node), _text(def_node)

    # Fallback: parse raw text of the <dt> as "name: annotation = default".
    raw = " ".join(dt.text().split())
    if "=" in raw:
        head, _, default = raw.partition("=")
        default = default.strip()
    else:
        head, default = raw, ""
    if ":" in head:
        name, _, annotation = head.partition(":")
    else:
        name, annotation = head, ""
    return name.strip(), annotation.strip(), default


def _find_summary_and_signature(root: HTMLParser, symbol: str) -> tuple[str, str]:
    """Return (one-line summary, signature string) from the page."""
    # Signature lives in a .doc-signature pre. It may be inside div.doc-text (geoms/stats)
    # or a sibling div (scales/coords).
    sig = root.css_first("div.doc-signature pre")
    if sig is None:
        raise RuntimeError(f"{symbol}: no .doc-signature block found")
    signature = " ".join(sig.text().split())

    # Summary is the first <p> inside div.doc-text. Each page has one.
    summary = ""
    for dt in root.css("div.doc-text"):
        p = dt.css_first("p")
        if p:
            summary = _text(p)
            break

    return summary, signature


def _params_from_dl(dl: Node) -> tuple[list[Param], str]:
    """Parse a <dl> under a doc-definition-items div into (params, aesthetics_html)."""
    aesthetics_html = ""
    out: list[Param] = []
    children: list[Node] = []
    ch = dl.child
    while ch is not None:
        if ch.tag in ("dt", "dd"):
            children.append(ch)
        ch = ch.next

    pairs = list(zip(children[::2], children[1::2]))
    for dt, dd in pairs:
        name, annotation, default = _parse_dt(dt)

        desc_parts: list[str] = []
        for p in dd.css("p"):
            desc_parts.append(_text(p))
        description = _strip_urls(" ".join(desc_parts).strip())

        if name == "mapping":
            tbl = dd.css_first("table")
            if tbl:
                aesthetics_html = tbl.html
            # Trailing sentence references the (now-separated) aesthetics table.
            description = description.replace(
                "The bold aesthetics are required.", ""
            ).strip()

        out.append(
            Param(
                name=name,
                annotation=annotation,
                default=default,
                description=description,
            )
        )

    return out, aesthetics_html


def _extract_params(root: HTMLParser, symbol: str) -> tuple[list[Param], str]:
    """Extract the parameter list and the aesthetics-table HTML (if any).

    Geom/stat pages use a single ``section#parameters``. Scale/coord pages
    split into ``section#init-parameters`` and ``section#parameter-attributes``;
    we merge them while preserving source order.
    """
    out: list[Param] = []
    aesthetics_html = ""

    for section_id in ("parameters", "init-parameters", "parameter-attributes"):
        section = root.css_first(f'section[id="{section_id}"]')
        if section is None:
            continue
        dl = section.css_first("div.doc-definition-items dl")
        if dl is None:
            continue
        part, aes = _params_from_dl(dl)
        out.extend(part)
        if aes and not aesthetics_html:
            aesthetics_html = aes

    return out, aesthetics_html


def extract(symbol: str, html: str) -> PageContent:
    tree = HTMLParser(html)
    summary, signature = _find_summary_and_signature(tree, symbol)
    params, aesthetics = _extract_params(tree, symbol)
    return PageContent(
        symbol=symbol,
        summary=summary,
        signature=signature,
        params=params,
        aesthetics_block=aesthetics,
    )


# ---------------------------------------------------------------------------
# Emit
# ---------------------------------------------------------------------------


def _aesthetics_table_to_markdown(html: str) -> str:
    """Convert the aesthetics table HTML to a Markdown table (best effort)."""
    if not html:
        return ""
    tree = HTMLParser(html)
    rows = tree.css("tr")
    md_rows: list[str] = []
    for r in rows:
        cells = [c.text().strip() for c in r.css("th,td")]
        md_rows.append("| " + " | ".join(cells) + " |")
    if len(md_rows) >= 2:
        # Insert header separator after first row
        cols = md_rows[0].count("|") - 1
        sep = "|" + "|".join(["---"] * cols) + "|"
        md_rows.insert(1, sep)
    return "\n".join(md_rows)


# Sections the scraper owns (it fully regenerates them every run). Any
# section whose heading does not appear here is considered hand-curated
# and is preserved verbatim on regeneration.
OWNED_SECTION_HEADINGS = frozenset({
    "## Signature",
    "## Parameters",  # ### Aesthetics is nested inside this section
})


def _split_preserved_sections(existing: str) -> dict[str, str]:
    """Return a mapping of "## Heading" → full section text (including
    heading and trailing blank line) for every top-level section the
    scraper does NOT own. Used to preserve hand-curated content across
    regenerations.
    """
    if not existing:
        return {}

    preserved: dict[str, str] = {}
    lines = existing.splitlines()

    # Find every "## " line that starts a top-level section.
    section_starts: list[tuple[int, str]] = []
    for i, ln in enumerate(lines):
        if ln.startswith("## ") and not ln.startswith("## #"):
            section_starts.append((i, ln))

    for idx, (start, heading) in enumerate(section_starts):
        if heading in OWNED_SECTION_HEADINGS:
            continue
        end = section_starts[idx + 1][0] if idx + 1 < len(section_starts) else len(lines)
        body = "\n".join(lines[start:end]).rstrip() + "\n"
        preserved[heading] = body

    return preserved


def _default_see_also() -> str:
    return "## See Also\n\n*(List related symbols here.)*\n"


def emit_markdown(page: PageContent, existing: str = "") -> str:
    lines: list[str] = []
    lines.append(f"# {page.symbol}")
    lines.append("")
    if page.summary:
        lines.append(page.summary)
        lines.append("")

    lines.append("## Signature")
    lines.append("")
    lines.append(f"`{page.signature}`")
    lines.append("")

    if page.params:
        lines.append("## Parameters")
        lines.append("")
        lines.append("| Param | Type | Default | Description |")
        lines.append("|-------|------|---------|-------------|")
        for p in page.params:
            name = f"`{p.name}`" if p.name else ""
            # Union types use "|" which collides with Markdown table separators; escape.
            ann = (p.annotation or "").replace("|", "\\|")
            default = f"`{p.default}`" if p.default else ""
            desc = p.description.replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {name} | {ann} | {default} | {desc} |")
        lines.append("")

        if page.aesthetics_block:
            lines.append("### Aesthetics")
            lines.append("")
            md_table = _aesthetics_table_to_markdown(page.aesthetics_block)
            if md_table:
                lines.append(md_table)
            lines.append("")

    # Preserve hand-curated sections (Examples, See Also, anything else a
    # human added). Order them as they appeared in the existing file,
    # with any missing sections backfilled at the end.
    preserved = _split_preserved_sections(existing)

    # Strip any leftover "## Example candidates" — that heading is deprecated.
    preserved.pop("## Example candidates", None)

    appended: list[str] = []
    saw_see_also = False
    for heading, body in preserved.items():
        appended.append(body)
        if heading == "## See Also":
            saw_see_also = True
    if not saw_see_also:
        appended.append(_default_see_also())

    upstream = "\n".join(lines)
    if not upstream.endswith("\n\n"):
        upstream = upstream.rstrip("\n") + "\n\n"
    return upstream + "\n".join(appended)


def emit_alias_stub(alias: str, canonical: str) -> str:
    return (
        f"# {alias}\n"
        f"\n"
        f"Alias of [`{canonical}`]({canonical}.md).\n"
    )


# ---------------------------------------------------------------------------
# Alias detection
# ---------------------------------------------------------------------------


def alias_target(symbol: str) -> str | None:
    """Return the canonical name for a known alias, or None if not an alias."""
    # British-spelling color aliases
    if symbol.startswith("scale_colour_"):
        return "scale_color_" + symbol[len("scale_colour_") :]
    # Naming variants
    return {
        "geom_bin2d": "geom_bin_2d",
        "stat_bin2d": "stat_bin_2d",
    }.get(symbol)




# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    only = set(argv) if argv else None

    version = load_version()
    API_DIR.mkdir(parents=True, exist_ok=True)

    symbols = list_symbols()
    if only:
        symbols = [s for s in symbols if s in only]

    generated = 0
    aliased = 0
    skipped = 0

    for sym in symbols:
        canonical = alias_target(sym)
        if canonical is not None:
            (API_DIR / f"{sym}.md").write_text(emit_alias_stub(sym, canonical))
            aliased += 1
            continue

        html = fetch_page(sym, version)
        if html is None:
            print(f"[skip] {sym}: 404 on plotnine.org", file=sys.stderr)
            skipped += 1
            continue

        try:
            page = extract(sym, html)
        except RuntimeError as e:
            print(f"[fail] {sym}: {e}", file=sys.stderr)
            raise

        target = API_DIR / f"{sym}.md"
        existing = target.read_text() if target.exists() else ""
        target.write_text(emit_markdown(page, existing))
        generated += 1

    print(f"generated: {generated}, aliased: {aliased}, skipped: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
