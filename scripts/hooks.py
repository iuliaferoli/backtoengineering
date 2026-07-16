"""MkDocs hook: embed YouTube videos and append tech-tree successor links.

Add to any page's frontmatter:

    videos:
      - https://youtu.be/abc123
      - https://www.youtube.com/watch?v=abc123
      - https://www.youtube.com/playlist?list=PL...

Players render wherever the page body contains the marker
`<!-- videos -->`; without a marker they appear in a "Watch"
section appended at the end. Non-YouTube URLs render as plain
links. The single `video:` key (one URL) also works.

Registered in mkdocs.yml via:  hooks: [scripts/hooks.py]
"""

import json
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qs, urlparse

NOCOOKIE = "https://www.youtube-nocookie.com"
GRAPH_FILE = Path(__file__).resolve().parent.parent / "docs" / "assets" / "graph.json"


@lru_cache(maxsize=1)
def _graph():
    """Load graph.json once; returns ({id: data}, {id: [successor ids]})."""
    data = json.loads(GRAPH_FILE.read_text(encoding="utf-8"))
    nodes = {n["data"]["id"]: n["data"] for n in data["nodes"]}
    successors = {node_id: [] for node_id in nodes}
    for edge in data["edges"]:
        successors[edge["data"]["source"]].append(edge["data"]["target"])
    for node_id in successors:
        successors[node_id].sort(key=lambda s: (nodes[s]["tier"], nodes[s]["label"]))
    return nodes, successors


def _next_nodes_block(page) -> str:
    """Return "Next in the tree" buttons linking to this page's successors."""
    page_id = (page.meta or {}).get("id")
    if not page_id:
        return ""

    nodes, successors = _graph()
    next_ids = successors.get(page_id) or []
    if not next_ids:
        return ""

    links = []
    for successor_id in next_ids:
        node = nodes[successor_id]
        target_url = "/" + node["url"].lstrip("/")
        kind = "project" if node["type"] == "project" else "topic"
        links.append(
            f'<a class="next-node {kind}" href="{target_url}">'
            f'{node["label"]} &rarr;</a>'
        )

    return (
        "\n\n## Next in the tree\n\n"
        '<div class="next-nodes" markdown>\n' + "\n".join(links) + "\n</div>\n"
    )


def _tree_link_block(page) -> str:
    """Return a link back to the full tree with this page's node selected."""
    page_id = (page.meta or {}).get("id")
    if not page_id:
        return ""
    return (
        "\n\n"
        f'<p class="tree-node-action"><a class="tree-node-link" '
        f'href="/tree/?node={page_id}">See in tree &rarr;</a></p>\n'
    )


def _embed_src(url: str) -> str | None:
    """Return an embeddable player URL for a YouTube link, else None."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if "list" in query:
        return f"{NOCOOKIE}/embed/videoseries?list={query['list'][0]}"
    if parsed.netloc.endswith("youtu.be"):
        video_id = parsed.path.strip("/").split("/")[0]
        return f"{NOCOOKIE}/embed/{video_id}" if video_id else None
    if "youtube.com" in parsed.netloc:
        if "v" in query:
            return f"{NOCOOKIE}/embed/{query['v'][0]}"
        if parsed.path.startswith("/embed/"):
            return f"{NOCOOKIE}{parsed.path}"
    return None


def _player(url: str) -> str:
    src = _embed_src(url)
    if src is None:
        return f"- [{url}]({url})"
    return (
        f'<div class="video-embed"><iframe src="{src}" title="YouTube video" '
        f'loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; '
        f'gyroscope; picture-in-picture" allowfullscreen></iframe></div>'
    )


def on_page_markdown(markdown, page, config, files):
    meta = page.meta or {}
    videos = meta.get("videos") or ([meta["video"]] if meta.get("video") else [])
    if isinstance(videos, list) and videos:
        block = "\n\n".join(_player(video) for video in videos)
        marker = "<!-- videos -->"
        if marker in markdown:
            markdown = markdown.replace(marker, block)
        else:
            markdown = markdown + "\n\n## Watch\n\n" + block + "\n"
    return markdown + _tree_link_block(page) + _next_nodes_block(page)
