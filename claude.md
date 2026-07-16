# Build Process & Architecture

This document tracks the collaborative build process with Claude and the architectural decisions made for the Robotics & AI Tech Tree learning site.

## Project Genesis

**Goal**: Build a learning website for robotics and AI enthusiasts featuring:
- A visual dependency graph ("tech tree") showing prerequisite relationships between topics
- Hands-on projects mapped to required knowledge
- Single-person maintainability with minimal time investment
- Easy content addition/editing

**Key Requirements**:
- Simplicity in architecture and software stack
- Static site (no servers, databases, or backend complexity)
- Python-first tooling (maintainer's strongest language)
- Future-proof for phase 2 features (user progress tracking)

## Technical Stack Selection

### Final Stack
- **MkDocs with Material theme**: Content management and static site generation
- **Python build script** (`scripts/build_graph.py`): Frontmatter parser and graph validator
- **Cytoscape.js + dagre layout**: Interactive dependency graph rendering
- **GitHub Pages + GitHub Actions**: Zero-cost hosting with auto-deploy on push

### Why Not Hugo?
Hugo is written in Go, but users write Go templates (a quirky mini-language), not Go code. Since the maintainer knows Python best, MkDocs with Jinja2-like templates is more accessible. Hugo's popularity doesn't translate to editability for this use case.

### Why Not Pelican?
Pelican works but has a small, semi-abandoned plugin ecosystem. MkDocs Material has a massive community, excellent documentation, and active maintenance.

### Why Not Astro?
Astro's content collections would handle frontmatter validation natively, and interactive islands would simplify the graph page. However, it requires the Node ecosystem. Python comfort was prioritized for long-term maintainability.

## Architecture

### Content as Data
Every topic and project is a Markdown file with YAML frontmatter:

```yaml
---
id: slam                       # stable unique identifier
title: SLAM
type: topic                    # topic | project
category: ai-ml               # for color coding
prerequisites: [ros2-basics, linear-algebra]
video: https://youtu.be/...   # optional
---
```

**Critical design decision**: IDs are the stable identity. Never rename an ID after publishing; progress tracking (phase 2) will reference these IDs. Changing an ID breaks user progress.

### Build Pipeline

1. **Content scan**: `build_graph.py` recursively reads all `.md` files in `docs/topics/` and `docs/projects/`
2. **Frontmatter parsing**: Extracts YAML metadata using PyYAML
3. **Validation**:
   - All required fields present (`id`, `title`, `type`)
   - No duplicate IDs
   - All prerequisites reference existing IDs
   - No circular dependencies (cycle detection via DFS)
   - Build fails loudly if any validation fails (catches typos before deployment)
4. **Graph generation**: Writes `docs/assets/graph.json` with Cytoscape-compatible node/edge format
5. **Static site build**: MkDocs generates HTML from Markdown

### Graph Renderer

`docs/js/tech-tree.js` runs only on pages containing `<div id="tech-tree">` (the homepage):
- Fetches `graph.json` via AJAX
- Instantiates Cytoscape with dagre layout (left-to-right, prerequisites → unlocks)
- Styles nodes by category (color-coded branches like Civilization VI)
- Projects are hexagons, topics are rounded rectangles
- Click → navigate to page URL
- Hover → highlight incoming prerequisite edges

**Layout algorithm**: dagre automatically arranges nodes by dependency depth, creating "eras" without manual tier assignment. 21 nodes currently span 9 columns.

### Deployment

GitHub Actions workflow on every push to `main`:
1. Install uv and sync dependencies from `pyproject.toml`
2. Run `build_graph.py` (CI fails if graph is invalid)
3. Run `mkdocs build --strict` (CI fails on broken links or warnings)
4. Deploy to GitHub Pages

Zero servers, zero maintenance, zero cost.

**Dependency Management**: Uses [uv](https://docs.astral.sh/uv/) for fast, reliable Python dependency management. `pyproject.toml` defines dependencies, `uv.lock` pins exact versions.

## Content Structure (As Built)

**21 nodes** across **5 categories**:

- **Core** (indigo): `curiosity` (the root node)
- **Electronics** (amber): `electronics-fundamentals`, `logic-gates`, `circuits`
- **Mechanical** (grey): `mechanical-fundamentals`, `cad`, `3d-printing`
- **Programming** (green): `python-basics`, `cpp-basics`, `data-fundamentals`
- **Data Science** (purple): `statistics-modelling`
- **AI & ML** (red): `ml-fundamentals`, `neural-networks`, `computer-vision`, `nlp`, `llms`, `ai-agents`, `vla` (vision-language-action)

**3 projects**:
- `blink-led`: Requires `circuits`
- `print-a-gearbox`: Requires `cad`, `3d-printing`
- `object-sorter`: Requires `blink-led`, `computer-vision` (bridges electronics and AI)

### Design Notes on Dependencies

- **Granularity**: Small concepts (e.g., "resistance, shorting, power, ground") are checklists inside topic pages, not individual nodes. Civilization has ~70 chunky nodes, not 500 tiny ones. Every node is a page to maintain.
- **Projects as prerequisites**: `object-sorter` requires the `blink-led` project. This mirrors Civilization's structure (some techs require building specific units/buildings). Pedagogically: hands-on experience is sometimes a prerequisite for advanced theory.
- **Category colors**: Each branch has a distinct color, visible in both the graph legend and node fill. Dark mode support works automatically via Material theme's CSS variables.

## Phase 2 Upgrade Path

**Goal**: Track user progress (mark topics completed, show what's unlocked).

### Phase 2a: localStorage (still fully static)
- Add a checkbox to each topic page
- Clicking stores the topic ID in `localStorage`
- Homepage JS reads the stored IDs and grays out/highlights completed nodes
- **Zero backend**, maybe an afternoon of work
- **No migration needed**: same stable IDs, same graph structure

### Phase 2b: Real accounts (minimal backend)
- Swap localStorage for a tiny hosted backend (Supabase, Pocketbase)
- Backend stores "set of completed IDs per user"
- Site itself stays static; only progress sync talks to the backend
- **No content migration**: Markdown files unchanged, graph.json unchanged

**Nothing built in phase 1 gets thrown away.**

## Developer Workflow

### Adding Content
1. Create `docs/topics/my-topic.md` or `docs/projects/my-project.md`
2. Fill in frontmatter (copy from existing file as template)
3. Run `uv run python scripts/build_graph.py` locally (validates immediately)
4. Optional: `uv run mkdocs serve` to preview at `http://127.0.0.1:8000`
5. Push to GitHub → auto-deploy

**The graph updates itself.** No manual node placement, no separate graph editor, no config file to update.

### Editing Dependencies
Change one word in one frontmatter field:
```yaml
prerequisites: [old-prereq]  →  prerequisites: [new-prereq]
```
Re-run the build script. If `new-prereq` doesn't exist, the build fails with a clear error.

### Local Testing
```bash
uv sync                                # install dependencies from pyproject.toml
uv run python scripts/build_graph.py   # validates and writes graph.json
uv run mkdocs serve                    # live preview with hot reload
```

## Validation Features

The build script catches these errors **before deployment**:
- Missing required frontmatter fields
- Duplicate IDs
- Typo'd prerequisite IDs (references to non-existent nodes)
- Circular dependencies (A requires B, B requires C, C requires A)
- Invalid node types (must be `topic` or `project`)

**Philosophy**: Fail loudly at build time, never ship a broken graph.

## Technology Choices Deep Dive

### Why Cytoscape.js?
- **Mature**: 10+ years, huge ecosystem, production-ready
- **dagre layout**: Hierarchical graph layout (left-to-right flow) built-in via plugin
- **Interactivity**: Click, hover, zoom, pan out of the box
- **Lightweight**: ~200KB minified (loaded from CDN)

**Alternatives considered**:
- **Mermaid**: Too limited for interactivity (text-to-flowchart, no click handlers)
- **D3.js**: Overkill; would require writing the entire layout algorithm from scratch
- **vis.js**: Comparable to Cytoscape but smaller community

### Why MkDocs Material?
- **Largest MkDocs theme** by community size (critical for long-term support)
- **Search, dark mode, navigation, mobile** all built-in
- **Markdown extensions**: Admonitions, tabs, code highlighting pre-configured
- **Zero JavaScript config**: Material handles responsive navigation, search indexing

### Why Static?
- **Cost**: GitHub Pages is free forever
- **Speed**: Pre-rendered HTML, served from CDN (Cloudflare via GitHub Pages)
- **Security**: No backend = no SQL injection, no auth vulnerabilities, no server patches
- **Reliability**: No database to crash, no API rate limits
- **Maintainability**: Push Markdown file → site updates. No database migrations, no deploy scripts.

### Why Python for the Build Script?
- Maintainer's strongest language
- PyYAML (frontmatter parsing) and pathlib (file operations) are batteries-included
- 200 lines including validation, error handling, and comments
- Could be rewritten in 50 lines of Node/Deno if the stack shifts later (graph.json format is language-agnostic)

### Why uv for Dependency Management?
- **Fast**: 10-100x faster than pip for dependency resolution and installation
- **Reliable**: Lockfile (`uv.lock`) ensures reproducible builds across dev/CI
- **Simple**: Single `pyproject.toml` for dependencies, no separate `requirements.txt`
- **Modern**: PEP 621 compliant, compatible with standard Python packaging tools
- **Zero config**: Works out of the box, no virtual environment activation needed with `uv run`

## Known Limitations & Future Considerations

### MkDocs 2.0 Breaking Changes
MkDocs Material team has warned that MkDocs 2.0 will introduce breaking changes with no migration path. Current mitigation: `pyproject.toml` pins `mkdocs<2.0`. Before upgrading, review the Material team's migration guide.

### Manual Navigation Ordering
Pages must be listed in `mkdocs.yml`'s `nav:` section to control sidebar order. Alternative: the `awesome-pages` plugin auto-generates nav from folder structure but adds a dependency. Current choice: manual for explicitness.

### CDN Dependencies
Cytoscape and dagre load from CDNs (`cdnjs.cloudflare.com`, `jsdelivr.net`). If offline access or zero external dependencies are required, vendor the libraries into `docs/js/`. One-line change in `mkdocs.yml`'s `extra_javascript`.

### Mobile Experience
The graph is functional on mobile (touch to tap, pinch to zoom) but small screens compress 21 nodes into a tiny viewport. Future improvement: collapsible categories or a simplified mobile view.

### Search Doesn't Index Graph Metadata
MkDocs search indexes page content but not frontmatter fields. Searching for "requires kinematics" won't find pages listing kinematics as a prerequisite. Phase 2 could add a "search prerequisites" feature if needed.

## Content Gaps (Not Yet Implemented)

From the original sketch, the following are stubs or missing:
- **ROS2 branch**: Not in the current tree (wasn't on the sketch provided). Would hang off Programming and Electronics.
- **Robotics hardware topics**: Motors, sensors, microcontrollers, power systems (to be added).
- **Project videos**: Optional `video:` field exists in frontmatter but no pages use it yet.
- **Embedded video snippets**: Commented-out YouTube embed template exists in sample files but not activated.

## Testing Strategy

**Build-time validation**: `build_graph.py` is the test suite. If it writes `graph.json`, the graph is valid.

**Headless graph verification**: During initial build, Cytoscape was run in headless Node.js to verify:
- `graph.json` parses correctly
- dagre layout executes without errors
- 21 nodes arrange into 9 columns (dependency depth)
- Single root node (Curiosity) at column 0

**Smoke test command**:
```bash
uv run python scripts/build_graph.py && echo "Graph valid"
```

## Inspiration & Design References

**Civilization VI tech tree**: Primary UX reference for:
- Left-to-right flow (ancient → modern)
- Category colors (civics blue, tech orange)
- Node states (not yet available, available, researched)
- Swim lanes for parallel branches

**User sketch**: Hand-drawn robotics dependency graph with 5 swim lanes:
- Electronics (circuits, logic gates)
- Mechanical (CAD, 3D printing)
- Programming (Python, C++)
- Data Science (statistics, modeling)
- AI & ML (ML fundamentals → neural networks → vision/NLP → LLMs → agents → VLA)

## File Structure Summary

```
techtree/
├── .github/workflows/deploy.yml    # CI: validate graph → build → deploy
├── docs/
│   ├── assets/graph.json           # Generated: Cytoscape data (nodes + edges)
│   ├── js/tech-tree.js             # Graph renderer (Cytoscape + dagre)
│   ├── index.md                    # Homepage with graph embed
│   ├── topics/*.md                 # 18 topic pages with frontmatter
│   └── projects/*.md               # 3 project pages with frontmatter
├── scripts/build_graph.py          # Frontmatter → graph.json with validation
├── mkdocs.yml                      # MkDocs config (theme, nav, extensions)
├── pyproject.toml                  # Python dependencies (PEP 621 format)
├── uv.lock                         # Lockfile for reproducible builds
└── README.md                       # User-facing setup/usage guide
```

## Lessons Learned

1. **SSG is interchangeable; unique features are not**: The tech tree differentiates the site, not MkDocs. Any SSG could serve the content; the graph is the complexity budget.

2. **Stable IDs are the skeleton**: Everything else (titles, content, even URLs) can change. IDs cannot. They're the foreign key for progress tracking and the graph structure.

3. **Validate early, validate loud**: Build-time validation catches 90% of content errors. Better to fail in CI than ship a broken prerequisite link.

4. **Manual beats automatic when the domain is small**: 21 nodes × 1 maintainer = manual frontmatter is fine. At 200 nodes or 5 contributors, a CMS or validation UI becomes worth it.

5. **Future-proofing is cheap when the data model is right**: Phase 2 progress tracking requires zero changes to the content files. The `id` field was the entire investment.

6. **Civilization VI was the right reference**: Chunky nodes, color-coded branches, left-to-right flow, projects as prerequisites. All direct mappings from the game's UX.

## Next Steps (Proposed)

1. **Add ROS2 branch**: `ros2-basics`, `ros2-navigation`, `ros2-manipulation` (depends on Programming + Electronics)
2. **Hardware topics**: `microcontrollers`, `motor-control`, `sensors`, `power-systems`
3. **Flesh out checklists**: Current topic pages are stubs; expand "you can move on when..." lists
4. **Embed videos**: Activate the commented-out YouTube embed snippets for topics with video content
5. **Mobile testing**: Verify graph usability on phones/tablets, consider collapsible categories
6. **Real deployment**: Update `site_url` in `mkdocs.yml`, push to GitHub, enable Pages in repo settings
7. **Content from videos**: Link existing YouTube tutorial videos via the `video:` frontmatter field

## Claude's Role in This Build

Claude generated:
- Complete working skeleton (MkDocs config, build script, graph renderer, sample content, CI workflow)
- 21 topic/project stubs from hand-drawn sketch
- Validation logic (duplicate IDs, typo'd prerequisites, cycle detection)
- Headless Cytoscape smoke test
- Category color system with legend
- Civilization VI-style design decisions
- This documentation

Human provided:
- Requirements (static, Python, single maintainer, progress tracking future)
- UX reference (Civ VI tech tree screenshots)
- Domain expertise (robotics/AI dependency sketch)
- Design constraints (simplicity, maintainability)

## Build Metadata

- **Initial build**: 2026-07-12
- **Current node count**: 21 (18 topics, 3 projects)
- **Dependency edges**: 24
- **Graph depth**: 9 columns (Curiosity → VLA is longest path)
- **Technologies**: Python 3.13, uv 0.5+, MkDocs 1.6.1, Material 9.7.6, Cytoscape 3.30.2, dagre 0.8.5
- **Dependency management**: uv with `pyproject.toml` + `uv.lock`
- **Lines of code** (excluding content):
  - `build_graph.py`: 191 lines
  - `tech-tree.js`: 136 lines
  - `mkdocs.yml`: 42 lines
  - Total custom code: ~370 lines
