# Graph Visualizer

An interactive graph visualizer built with Python and **pygame-ce**. Create nodes, connect them with edges, and watch **DFS** or **BFS** traversal animate step-by-step — all inside a resizable dark-themed window.

---

## Features

| Feature | Details |
|---|---|
| 🖱️ Interactive canvas | Click to place nodes, click two nodes to connect them |
| 🔵 Node states | Color-coded: default blue → selected pink → visited purple → current yellow |
| 🔗 Edge states | Muted gray at rest; highlighted purple along the traversal path |
| 🎬 DFS / BFS animation | Step-by-step traversal with configurable speed (100 ms – 1 000 ms) |
| 🔄 Algorithm toggle | Switch between DFS and BFS before starting — active algo highlighted in green |
| ⌨️ Keyboard shortcuts | `V` · `E` · `A` to switch modes instantly |
| 📊 Live stats | Node count, edge count, current step, and speed shown in the sidebar |
| 🗑️ Clear Graph | One-click button to wipe the canvas and start fresh |
| 🪟 Resizable window | Drag any edge or corner — all UI elements reflow automatically |
| 🌑 Dark theme | Near-black canvas with a faint dot grid; no harsh pure-black backgrounds |

---

## Project Structure

```
graphVisualizer/
├── src/
│   └── graphvisualizer/
│       ├── __init__.py      # Entry point — instantiates and runs App
│       ├── app.py           # Window, sidebar, buttons, event loop
│       ├── graph.py         # Node, Edge, Graph data structures + DFS/BFS
│       ├── renderer.py      # Pygame drawing: nodes, edges, animation
│       └── config.py        # All color constants (Colors class)
├── pyproject.toml           # Package metadata and dependencies
└── README.md
```

### Module responsibilities

- **`config.py`** — Single source of truth for every RGB color. Organized into sections: base palette, backgrounds, surfaces, node states, edge states, accents, text, and danger colors.
- **`graph.py`** — Pure data layer. `Node` stores position, color, radius and ID. `Edge` links two nodes with a weight and color. `Graph` holds vertices + adjacency list and exposes `dfs_iterative` and `bfs`.
- **`renderer.py`** — Drawing layer. Each frame it draws all edges (muted or visited) then all nodes (with state rings + white labels). Also owns the animation timer and step logic.
- **`app.py`** — UI layer. Manages the pygame event loop, the sidebar panel, all button objects, mode state, and calls into `Graph` and `Render` at the right moments.

---

## Installation

### Requirements

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/) (recommended) **or** pip

### With uv (recommended)

```bash
git clone https://github.com/Raghu-ram12/graphVisualizer.git
cd graphVisualizer
uv run graphvisualizer
```

### With pip

```bash
pip install pygame-ce
python -m graphvisualizer
```

---

## Usage

### 1 — Add nodes

Press **V** or click **Add Vertex** in the sidebar, then click anywhere on the dark canvas. Each node is assigned an auto-incrementing integer ID displayed as a white label inside the circle.

### 2 — Connect nodes

Press **E** or click **Add Edge**. Click a first node (it turns pink), then click a second — an undirected edge is drawn between them. The status bar at the bottom of the sidebar guides you through each step.

### 3 — Animate a traversal

Press **A** or click **Animate**. Choose your algorithm (**DFS** or **BFS** — the active one glows green) and adjust the step speed with **–** / **+**. Then click any node on the canvas to start from there.

During animation:

| Color | Meaning |
|---|---|
| Yellow ring | Node currently being processed |
| Purple fill | Node already visited |
| Purple edge | Edge that was traversed |

### 4 — Keyboard shortcuts

| Key | Action |
|---|---|
| V | Switch to Vertex mode |
| E | Switch to Edge mode |
| A | Switch to Animate mode |

### 5 — Clear the graph

Click **Clear Graph** (red button at the panel bottom) to remove all nodes and edges and reset the canvas.

---

## Sidebar Layout

```
┌──────────────────────┐
│  GRAPH VISUALIZER    │  <- title block
│  ● Vertex Mode       │  <- live mode badge (color matches active mode)
├──────────────────────┤
│  MODES               │
│  [Add Vertex]     V  │  <- blue accent strip
│  [Add Edge]       E  │  <- orange accent strip
│  [Animate]        A  │  <- green accent strip
├──────────────────────┤
│  STATS               │
│  Nodes:           4  │
│  Edges:           3  │
│  DFS step:     2 / 4 │  (animate mode only)
│  Speed:        500ms │  (animate mode only)
├──────────────────────┤
│  ANIMATION SPEED / ALGO   (animate mode only)
│  [-] [+]  [DFS] [BFS]│  <- active algo glows green
├──────────────────────┤
│  Click canvas to...  │  <- amber contextual hint
├──────────────────────┤
│     Clear Graph      │  <- danger button (always at bottom)
└──────────────────────┘
```

---

## Color Reference

All colors live in `src/graphvisualizer/config.py`.

| Constant | RGB | Used for |
|---|---|---|
| `NODE_DEFAULT` | `(0, 90, 210)` | Idle node fill |
| `NODE_SELECTED` | `(255, 64, 129)` | First node picked in edge mode |
| `NODE_VISITED` | `(106, 90, 205)` | Already traversed node |
| `NODE_CURRENT` | `(255, 204, 0)` | Current animation step |
| `EDGE_DEFAULT` | `(80, 80, 100)` | Idle edge (anti-aliased) |
| `EDGE_VISITED` | `(106, 90, 205)` | Edge on traversal path |
| `ACCENT_VERTEX` | `(0, 122, 255)` | Add Vertex button strip |
| `ACCENT_EDGE` | `(255, 149, 0)` | Add Edge button strip |
| `ACCENT_ANIMATE` | `(52, 199, 89)` | Animate button strip + active DFS/BFS |
| `BG_CANVAS` | `(12, 12, 18)` | Main canvas background |
| `BG_PANEL` | `(30, 30, 30)` | Sidebar background |
| `TEXT_STATUS` | `(255, 200, 0)` | Amber status bar hints |
| `DANGER` | `(100, 20, 20)` | Clear Graph button base |

---

## Architecture Notes

- **Separation of concerns** — `Graph` is pure Python with no pygame imports; `Renderer` owns all drawing; `App` owns all input and UI state.
- **Semantic color constants** — Every color is named by its purpose (`NODE_VISITED`, `EDGE_ACTIVE`) not its appearance (`PURPLE`, `ORANGE`), making future theme changes a one-file edit.
- **Dynamic layout** — The sidebar status bar and Clear Graph button recompute their y coordinates from `screen.get_height()` every frame, so the layout is correct at any window size.
- **Edge coloring via state** — Edges carry a `.color` field (`None` = muted default). The renderer checks this each frame; the animator sets it as the traversal progresses, giving a persistent visual trail without extra data structures.
- **Node rings** — State rings are drawn by rendering a slightly larger circle in the ring color first, then the filled node on top — a simple technique that avoids pygame's thin `width` circle rendering.

---

## License

MIT — free to use, modify, and distribute.
