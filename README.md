# Robotics & AI Tech Tree

A static learning site: topics and hands-on projects arranged in a
dependency tree. Built with MkDocs Material, Cytoscape.js, and one
small Python script. Deploys to GitHub Pages on every push.

# Your Journey To Physical AI

Welcome to **Back To Engineering**! This is your roadmap from curiosity to building intelligent robots. Whether you're coming from software, AI/ML, or starting fresh, this tech tree organizes everything you need to learn robotics and physical AI in 2026.

## How This Works

This isn't a traditional course - it's a **choose-your-own-adventure learning path**:

- **Click any topic card** to explore concepts, watch tutorials, and find resources
- **Follow the arrows** - they show prerequisites (what you need to know first)
- **Star-shaped nodes** are hands-on projects where theory meets reality
- **Color-coded by discipline** - Electronics 🟡, Mechanical ⚪, Programming 🟢, Data Science 🟣, AI & ML 🔴
- **Scroll to zoom** and drag to pan around the graph
- **Hover over nodes** to see prerequisite connections glow

Start with **Curiosity** on the left and work your way right through the eras. Or jump to what interests you - the graph shows what knowledge you'll need.

## The Philosophy

My approach mixes **practical building** with **industry best practices**. You'll start simple (blinking an LED, cardboard robot arms) and progressively add complexity (ROS 2, AI-driven manipulation, VLAs). Each layer teaches you *why* we use professional tools, not just how.

By the end, you'll understand the full stack: from servo control to vision-language-action models deployed on real hardware.

## Featured Project

Check out the [Robot Arm Project](projects/robot-arm.md) to see the full journey: 7 episodes from scratch-built cardboard prototypes to AI-powered LeRobot arms trained on custom datasets.

---

<a href="/" style="display: block; text-decoration: none; border: 1px solid rgba(95,191,130,0.4); border-radius: 12px; padding: 2rem; text-align: center; background: linear-gradient(135deg, rgba(95,191,130,0.08), transparent);">
  <span style="display: block; font-size: 1.4rem; font-weight: 600; margin-bottom: 0.4rem;">Open the Tech Tree →</span>
  <span style="display: block; opacity: 0.75;">30 topics and projects, from Curiosity to a walking robot dog. Full screen, Civ-style.</span>
</a>




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

## Analytics

The site supports Umami analytics without requiring credentials for
local builds. Create a site in Umami, then add these GitHub repository
variables under Settings -> Secrets and variables -> Actions -> Variables:

```text
UMAMI_SCRIPT_URL=https://your-umami-host.example/script.js
UMAMI_WEBSITE_ID=your-website-id
UMAMI_DOMAINS=www.backtoengineering.com,backtoengineering.com
```

When those variables are present, the deploy workflow injects the Umami
tracker into the built pages. The site also sends custom events for
tree navigation, next-node clicks, external links, video interactions,
and tree node detail opens.
