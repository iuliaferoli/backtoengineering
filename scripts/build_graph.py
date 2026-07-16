#!/usr/bin/env python3
"""Build docs/assets/graph.json from topic and project frontmatter.

Scans docs/topics/ and docs/projects/ for Markdown files, reads their
YAML frontmatter, validates the dependency graph, and writes a JSON
file that the homepage tech tree (Cytoscape.js) consumes.

Run from the repo root:  python scripts/build_graph.py
Exits non-zero on any validation error so CI fails before deploying
a broken tree.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
CONTENT_DIRS = ["topics", "projects"]
OUTPUT_FILE = DOCS_DIR / "assets" / "graph.json"

REQUIRED_KEYS = {"id", "title", "type"}
VALID_TYPES = {"topic", "project"}

# Fallback icons per category when a page has no `icon:` in frontmatter.
# Icon names are Tabler outline icons: https://tabler.io/icons
CATEGORY_ICONS = {
    "core": "sparkles",
    "electronics": "bolt",
    "mechanical": "settings",
    "programming": "code",
    "data-science": "database",
    "ai-ml": "chart-dots",
}


def parse_frontmatter(path: Path) -> dict:
    """Return the YAML frontmatter of a Markdown file as a dict."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path}: no frontmatter block found")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path}: unterminated frontmatter block")
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        raise ValueError(f"{path}: frontmatter is not a mapping")
    return data


def page_blurb(path: Path) -> str:
    """First body paragraph after the H1, trimmed for the tree popup."""
    text = path.read_text(encoding="utf-8")
    body = text.split("---", 2)[2] if text.startswith("---") else text
    for para in body.split("\n\n"):
        para = " ".join(para.split())
        if not para or para.startswith(("#", "!!!", "<", "-", "|", "```", ">")):
            continue
        return para[:220] + ("…" if len(para) > 220 else "")
    return ""


def page_url(path: Path) -> str:
    """URL of the built page, relative to the site root.

    Matches MkDocs' default use_directory_urls behaviour:
    docs/topics/kinematics.md -> topics/kinematics/
    """
    rel = path.relative_to(DOCS_DIR).with_suffix("")
    return rel.as_posix() + "/"


def collect_nodes() -> list[dict]:
    nodes = []
    errors = []
    seen_ids: dict[str, Path] = {}

    for dirname in CONTENT_DIRS:
        for md_file in sorted((DOCS_DIR / dirname).glob("*.md")):
            if md_file.name == "index.md":
                continue
            try:
                fm = parse_frontmatter(md_file)
            except ValueError as exc:
                errors.append(str(exc))
                continue

            missing = REQUIRED_KEYS - fm.keys()
            if missing:
                errors.append(f"{md_file}: missing keys {sorted(missing)}")
                continue

            node_id = str(fm["id"])
            node_type = str(fm["type"])

            if node_type not in VALID_TYPES:
                errors.append(
                    f"{md_file}: type '{node_type}' must be one of {sorted(VALID_TYPES)}"
                )
            if node_id in seen_ids:
                errors.append(
                    f"{md_file}: duplicate id '{node_id}' (also in {seen_ids[node_id]})"
                )
            seen_ids[node_id] = md_file

            prereqs = fm.get("prerequisites") or []
            if not isinstance(prereqs, list):
                errors.append(f"{md_file}: prerequisites must be a list")
                prereqs = []

            category = str(fm.get("category", "core"))
            videos = fm.get("videos") or ([fm["video"]] if fm.get("video") else [])
            nodes.append(
                {
                    "id": node_id,
                    "title": str(fm["title"]),
                    "type": node_type,
                    "category": category,
                    "icon": str(fm.get("tree_icon") or CATEGORY_ICONS.get(category, "circle")),
                    "group": str(fm["group"]) if fm.get("group") else None,
                    "blurb": page_blurb(md_file),
                    "video_count": len(videos) if isinstance(videos, list) else 0,
                    "url": page_url(md_file),
                    "prerequisites": [str(p) for p in prereqs],
                }
            )

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)
    return nodes


def validate_graph(nodes: list[dict]) -> None:
    """Check that all prerequisites exist and the graph has no cycles."""
    ids = {n["id"] for n in nodes}
    errors = []

    for node in nodes:
        for prereq in node["prerequisites"]:
            if prereq not in ids:
                errors.append(
                    f"'{node['id']}' lists unknown prerequisite '{prereq}'"
                )

    # Cycle detection via iterative depth-first search.
    graph = {n["id"]: n["prerequisites"] for n in nodes}
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node_id: WHITE for node_id in graph}

    for start in graph:
        if color[start] != WHITE:
            continue
        stack = [(start, iter(graph[start]))]
        color[start] = GRAY
        while stack:
            node_id, children = stack[-1]
            advanced = False
            for child in children:
                if child not in graph:
                    continue  # already reported as unknown prerequisite
                if color[child] == GRAY:
                    errors.append(
                        f"dependency cycle detected involving '{child}'"
                    )
                elif color[child] == WHITE:
                    color[child] = GRAY
                    stack.append((child, iter(graph[child])))
                    advanced = True
                    break
            if not advanced:
                color[node_id] = BLACK
                stack.pop()

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)


def compute_tiers(nodes: list[dict]) -> dict[str, int]:
    """Tier = longest prerequisite chain from a root (the 'era' column)."""
    prereqs = {n["id"]: n["prerequisites"] for n in nodes}
    tiers: dict[str, int] = {}

    def tier_of(node_id: str) -> int:
        if node_id not in tiers:
            deps = prereqs.get(node_id, [])
            tiers[node_id] = 0 if not deps else 1 + max(tier_of(d) for d in deps)
        return tiers[node_id]

    for node_id in prereqs:
        tier_of(node_id)
    return tiers


def main() -> None:
    nodes = collect_nodes()
    validate_graph(nodes)
    tiers = compute_tiers(nodes)

    elements = {
        "nodes": [
            {
                "data": {
                    "id": n["id"],
                    "label": n["title"],
                    "type": n["type"],
                    "category": n["category"],
                    "icon": n["icon"],
                    "group": n["group"],
                    "blurb": n["blurb"],
                    "videoCount": n["video_count"],
                    "tier": tiers[n["id"]],
                    "prereqCount": len(n["prerequisites"]),
                    "url": n["url"],
                }
            }
            for n in nodes
        ],
        "edges": [
            {"data": {"source": prereq, "target": n["id"]}}
            for n in nodes
            for prereq in n["prerequisites"]
        ],
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(elements, indent=2), encoding="utf-8")
    print(
        f"Wrote {OUTPUT_FILE.relative_to(REPO_ROOT)}: "
        f"{len(elements['nodes'])} nodes, {len(elements['edges'])} edges"
    )


if __name__ == "__main__":
    main()
