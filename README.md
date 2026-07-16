# Robotics & AI Tech Tree

A static learning site: topics and hands-on projects arranged in a
dependency tree. Built with MkDocs Material, Cytoscape.js, and one
small Python script. Deploys to GitHub Pages on every push.

## Local development

```bash
uv sync                                # install dependencies
uv run python scripts/build_graph.py   # regenerate docs/assets/graph.json
uv run mkdocs serve                    # live preview at http://127.0.0.1:8000
```

## Adding content

1. Create a Markdown file in `docs/topics/` or `docs/projects/`.
2. Fill in the frontmatter:

   ```yaml
   ---
   id: slam                       # unique, stable, never change it
   title: SLAM
   type: topic                    # topic | project
   category: ai-ml                # drives node color on the tree
   tree_icon: map-2               # Tabler icon name (tabler.io/icons), optional
   prerequisites: [ros2-basics, linear-algebra]
   video: https://youtu.be/...    # optional, counted on the node card
   ---
   ```

3. Add the page to `nav:` in `mkdocs.yml`.
4. Run `uv run python scripts/build_graph.py` (CI also runs it on push).
5. Push. Done.

The build fails loudly if a prerequisite id has a typo, an id is
duplicated, or the graph contains a cycle.

## The tree page

`docs/tree/index.html` is a standalone full-page renderer (no MkDocs
theme): ELK computes the layered layout and orthogonal edge routes,
nodes are HTML cards, edges are one SVG layer, pan/zoom is custom.
MkDocs copies it verbatim to `/tree/`. It reads `assets/graph.json`,
so content changes flow through automatically; only design changes
touch this file. Category colors live in the `:root` CSS variables
at the top of the file.

## Design notes

- Node ids are the stable identity of every topic/project. Progress
  tracking (phase 2) will store sets of these ids, first in
  localStorage, later per account. Never rename an id once published;
  add a new node instead.
- The graph renderer lives in `docs/js/tech-tree.js` and only activates
  on pages containing `<div id="tech-tree">`.
- Cytoscape and dagre load from CDNs (see `extra_javascript` in
  `mkdocs.yml`). Vendor them into `docs/js/` if you prefer no CDN.

## One-time GitHub Pages setup

Repo Settings -> Pages -> Source: "GitHub Actions". Then update
`site_url` in `mkdocs.yml` to your real URL.
