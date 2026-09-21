# Adding a Physics Engine for Auto-Positioning Vertices

A force-directed layout engine makes your graph self-organise into a readable, aesthetically pleasing arrangement — no manual dragging required. This guide walks you through every step, from theory to a working implementation that plugs directly into your existing `graphvisualizer` codebase.

---

## Table of Contents

1. [Why a Physics Engine?](#why-a-physics-engine)
2. [Choosing an Algorithm](#choosing-an-algorithm)
3. [Project Structure Overview](#project-structure-overview)
4. [Step 1 — Extend the Node with Physics State](#step-1--extend-the-node-with-physics-state)
5. [Step 2 — Create the Physics Engine Module](#step-2--create-the-physics-engine-module)
6. [Step 3 — Wire the Engine into the Renderer](#step-3--wire-the-engine-into-the-renderer)
7. [Step 4 — Add a UI Toggle](#step-4--add-a-ui-toggle)
8. [Step 5 — Run and Tune](#step-5--run-and-tune)
9. [Advanced Topics](#advanced-topics)
10. [Troubleshooting](#troubleshooting)

---

## Why a Physics Engine?

Force-directed layouts simulate a physical system:

| Force | Analogy | Effect |
|---|---|---|
| **Repulsion** | Like-charged electrons | Nodes push each other apart |
| **Attraction** | Springs (Hooke's law) | Connected nodes pull together |
| **Cooling** | Friction / temperature | System gradually settles |

After enough iterations the system reaches a low-energy state where nodes are evenly spaced, clusters are visible, and edge crossings are minimised. The result is an automatically laid-out graph that looks clean and professional.

---

## Choosing an Algorithm

Three popular options, ordered by complexity:

### 1. Fruchterman-Reingold (Recommended starting point)
- Classic force-directed algorithm
- O(n²) repulsion — fine for < 500 nodes
- Easy to implement, great visual results
- **This guide implements this one**

### 2. ForceAtlas2 (Gephi's engine)
- Faster approximations (Barnes-Hut)
- Handles thousands of nodes
- More parameters to tune
- Use the [`fa2`](https://pypi.org/project/fa2/) Python package if you outgrow FR

### 3. Kamada-Kawai
- Based on shortest-path distances
- Produces very symmetric layouts
- Requires all-pairs shortest paths upfront

**For this project Fruchterman-Reingold is the right fit** — small graphs, simple codebase, quick results.

---

## Project Structure Overview

Before we begin, here is the existing module map and where each new piece belongs:

```
src/graphvisualizer/
├── __init__.py
├── app.py              ← add UI toggle + import PhysicsEngine
├── graph.py            ← add physics fields to Node
├── renderer.py         ← call physics step before drawing
├── config.py           ← add physics colours (optional)
└── physics.py          ← NEW MODULE (created in Step 2)
```

> **Design principle:** `physics.py` is standalone — it knows nothing about Pygame, only about coordinates. The renderer calls it, not the other way round.

---

## Step 1 — Extend the Node with Physics State

Open `src/graphvisualizer/graph.py`. Every `Node` currently stores only `cords`, `color`, `radius`, and `id`. A physics simulation needs per-node velocity and force accumulators.

### Add fields to `Node.__init__`

```python
class Node:
    id_      = 0
    radius   = 10

    def __init__(self, x, y, data=None):
        self.color = Colors.NODE_DEFAULT
        self.cords = Coordinates(x, y)
        self.data  = data or Node.id_
        self.radius = Node.radius
        self.id    = Node.id_
        # ── NEW physics fields ──
        self.vx      = 0.0    # velocity x
        self.vy      = 0.0    # velocity y
        self.fx      = 0.0    # accumulated force x
        self.fy      = 0.0    # accumulated force y
        self.pinned  = False  # True if user dragged this node manually
        Node.id_ += 1
```

### Add helper methods

At the end of the `Node` class, add:

```python
    def reset_forces(self):
        """Zero the accumulated force for the next simulation step."""
        self.fx = 0.0
        self.fy = 0.0

    def apply_force(self, fx, fy):
        """Add a force vector to the accumulator."""
        self.fx += fx
        self.fy += fy

    def update_velocity(self, damping=0.9, dt=1.0):
        """
        Integrate force → velocity.
        `damping` acts as friction; higher = slower settling.
        """
        ax = self.fx * dt
        ay = self.fy * dt
        self.vx = (self.vx + ax) * damping
        self.vy = (self.vy + ay) * damping

        # Clamp velocity to prevent explosions
        max_speed = 15.0
        speed = (self.vx**2 + self.vy**2)**0.5
        if speed > max_speed:
            self.vx = (self.vx / speed) * max_speed
            self.vy = (self.vy / speed) * max_speed

        # Update position
        self.cords.x += self.vx
        self.cords.y += self.vy
```

### Update `addNode` to skip physics on initial placement

In `Graph.addNode`, leave velocity at zero by default — the simulation will move nodes on the first few frames, which is the desired behaviour (they "fly apart" and then settle).

---

## Step 2 — Create the Physics Engine Module

Create the file `src/graphvisualizer/physics.py`. This is a single-file implementation of Fruchterman-Reingold.

### Full implementation

```python
"""
Fruchterman-Reingold force-directed layout engine.

Pure coordinate math — no Pygame dependency.  The renderer calls
PhysicsEngine.tick(graph) once per frame while auto-layout is active.
"""

from math import sqrt


class PhysicsEngine:
    """
    Parameters
    ----------
    width, height : int
        The canvas dimensions (excluding the sidebar).  Used to keep nodes
        inside the visible area.
    temperature : float
        Initial "temperature" — higher values let nodes move more freely.
        Decreases over time (cooling schedule).
    repulsion : float
        Repulsive force constant (k² in the paper).  Larger = more spread out.
    attraction : float
        Spring constant for edges.  Larger = tighter clustering.
    damping : float
        Velocity multiplier applied each step (0.0–1.0).  < 1.0 = friction.
    """

    DEFAULT_REPULSION = 800.0
    DEFAULT_ATTRACTION = 0.008
    DEFAULT_DAMPING     = 0.90
    DEFAULT_TEMPERATURE = 100.0
    MIN_TEMPERATURE     = 0.1
    COOLING_FACTOR      = 0.995

    def __init__(self, width=1020, height=720,
                 repulsion=None, attraction=None,
                 damping=None, temperature=None):
        self.width       = width
        self.height      = height
        self.repulsion   = repulsion   or self.DEFAULT_REPULSION
        self.attraction  = attraction  or self.DEFAULT_ATTRACTION
        self.damping     = damping     or self.DEFAULT_DAMPING
        self.temperature = temperature or self.DEFAULT_TEMPERATURE
        self.running     = False        # toggle for auto-layout
        self.iterations = 0

    # ------------------------------------------------------------------ #
    #                        Public API                                    #
    # ------------------------------------------------------------------ #

    def tick(self, graph, delta_t=1.0):
        """
        Perform one full simulation step.
        Call this once per frame inside the main loop.

        Parameters
        ----------
        graph : Graph
            The graph whose vertices will be repositioned.
        delta_t : float
            Time scaling factor.  Pass `clock.get_time() / 16.0` to
            normalise for frame-rate.
        """
        if not self.running:
            return

        vertices = list(graph.vertices.values())
        n = len(vertices)
        if n == 0:
            return

        # 1. Reset all forces
        for v in vertices:
            v.reset_forces()

        # 2. Repulsion between every pair (O(n²))
        self._apply_repulsion(vertices)

        # 3. Attraction along edges
        self._apply_attraction(vertices, graph.edges)

        # 4. Centreing force (prevents drift)
        self._apply_centering(vertices)

        # 5. Integrate velocities and update positions
        for v in vertices:
            v.update_velocity(damping=self.damping, dt=delta_t)
            self._clamp_position(v)

        # 6. Cool down
        self.temperature *= self.COOLING_FACTOR
        if self.temperature < self.MIN_TEMPERATURE:
            self.temperature = self.MIN_TEMPERATURE
        self.iterations += 1

    def start(self):
        """Begin the simulation."""
        self.running = True
        self.temperature = self.DEFAULT_TEMPERATURE
        self.iterations = 0

    def stop(self):
        """Freeze the simulation in place."""
        self.running = False
        # Zero velocities so nothing jiggles
        for v in self._last_vertices:
            pass  # handled on next start

    def reset(self):
        """Reset temperature so the next start is fully energetic."""
        self.temperature = self.DEFAULT_TEMPERATURE
        self.iterations = 0

    # ------------------------------------------------------------------ #
    #                     Force Calculations                               #
    # ------------------------------------------------------------------ #

    def _distance(self, a, b):
        dx = b.cords.x - a.cords.x
        dy = b.cords.y - a.cords.y
        return sqrt(dx * dx + dy * dy)

    def _apply_repulsion(self, vertices):
        """
        Every pair of nodes repels each other.
        Force ∝ k² / d², direction = along the line connecting centres.
        """
        k = sqrt(self.repulsion)
        for i, a in enumerate(vertices):
            for b in vertices[i + 1:]:
                dx = b.cords.x - a.cords.x
                dy = b.cords.y - a.cords.y
                dist = max(self._distance(a, b), 0.01)
                # Avoid division by zero
                if dist == 0:
                    dist = 0.01
                    dx = 1.0
                # Repulsive force magnitude
                force = (self.repulsion * k) / (dist * dist)
                # Direction (unit vector pointing from a → b)
                ux = dx / dist
                uy = dy / dist
                # Apply equal and opposite forces
                a.apply_force(-force * ux, -force * uy)
                b.apply_force( force * ux,  force * uy)

    def _apply_attraction(self, vertices, edges):
        """
        Each edge acts like a spring pulling its endpoints together.
        Force ∝ d² / k, direction = along the edge.
        """
        k = sqrt(self.repulsion)
        for edge in edges:
            a = edge.start_node
            b = edge.end_node
            dx = b.cords.x - a.cords.x
            dy = b.cords.y - a.cords.y
            dist = max(self._distance(a, b), 0.01)
            # Attractive force magnitude
            force = (dist * dist) / (k * 100) * self.attraction
            ux = dx / dist
            uy = dy / dist
            a.apply_force( force * ux,  force * uy)
            b.apply_force(-force * ux, -force * uy)

    def _apply_centering(self, vertices):
        """Gentle pull towards the centre of the canvas."""
        cx = self.width  / 2.0
        cy = self.height / 2.0
        for v in vertices:
            dx = cx - v.cords.x
            dy = cy - v.cords.y
            dist = max(self._distance(v, type('C', (), {'x': cx, 'y': cy})()), 0.01)
            force = 0.001 * dist
            v.apply_force(force * dx / dist, force * dy / dist)

    def _clamp_position(self, node):
        """Keep nodes inside the canvas with a margin."""
        margin = 30
        node.cords.x = max(margin, min(self.width - margin, node.cords.x))
        node.cords.y = max(margin, min(self.height - margin, node.cords.y))
```

### A note on the centreing force

The `_apply_centering` helper above uses a small anonymous class just to reuse `_distance`.  In production code you'd want a cleaner approach — see **Advanced Topics** for the recommended refactor.

---

## Step 3 — Wire the Engine into the Renderer

Open `src/graphvisualizer/renderer.py`. We need to tick the physics engine before drawing each frame, but only when auto-layout is active.

### 3a. Store a reference to the engine 

In `Render.__init__`, add:

```python
    def __init__(self, graph, screen):
        self.graph          = graph
        self.screen         = screen
        self.animationIndex = 0
        self.animationTimer = 0
        self.animationSpeed = 500
        self.orderList      = None
        self.prev           = None
        # ── NEW: physics engine reference ──
        self.physics = None
```

### 3b. Add a physics-tick call inside `draw_graph`

The cleanest place is at the top of `draw_graph` so the layout updates before anything is rendered:

```python
    def draw_graph(self):
        # ── NEW: tick physics once per frame when active ──
        if self.physics is not None and self.physics.running:
            # Normalise for frame-rate: assume 60 fps target (16 ms)
            delta_t = 16.0 / 16.0  # ≈ 1.0 at 60 fps
            self.physics.tick(self.graph, delta_t=delta_t)

        # existing drawing code follows ...
        for edge in self.graph.edges:
            ...
```

### 3c. (Optional) Add a "freeze" button in the renderer

If you want the renderer to expose controls:

```python
    def toggle_physics(self):
        """Start or stop the physics simulation."""
        if self.physics is None:
            from graphvisualizer.physics import PhysicsEngine
            screen_w, screen_h = self.screen.get_size()
            self.physics = PhysicsEngine(
                width=screen_w - 240,   # subtract sidebar width
                height=screen_h,
            )
        self.physics.start()
        self.physics.reset()
        # Clear any traversal colours so layout is visible
        for v in self.graph.vertices.values():
            v.color = Colors.NODE_DEFAULT
```

---

## Step 4 — Add a UI Toggle

Open `src/graphvisualizer/app.py`. We add a **"Auto Layout"** button that toggles the physics simulation.

### 4a. Add the button

In `App.__addButtons`, alongside the existing buttons:

```python
    def __addButtons(self):
        px = 16
        bw = self.PANEL_WIDTH - px * 2
        # ... existing buttons stay as they are ...

        # ── NEW: Auto Layout button ──
        self.physics_button = SmallButton(
            px, 350, bw, 38, "Auto Layout",
            action=self._toggle_physics,
            active_color=Colors.ACCENT_ANIMATE,
        )
```

Adjust the `y` coordinate (350 here) to fit your layout — place it between the mode buttons and the danger button.

### 4b. Add the handler method

```python
    def _toggle_physics(self):
        """Start (or restart) the physics auto-layout."""
        from graphvisualizer.physics import PhysicsEngine

        if self.render.physics is None:
            screen_w, screen_h = self.screen.get_size()
            self.render.physics = PhysicsEngine(
                width=screen_w - self.PANEL_WIDTH,
                height=screen_h,
            )
            self.render.physics.start()
            self.render.physics.reset()
        else:
            # If already running, reset with fresh energy
            self.render.physics.reset()
            self.render.physics.start()

        # Reset any traversal colours so the layout is visible
        for v in self.graph.vertices.values():
            v.color = Colors.NODE_DEFAULT
```

### 4c. Add a keyboard shortcut (optional but nice)

In `App.handleUserInput`, inside the `KEYDOWN` block:

```python
            if event.type == pygame.KEYDOWN:
                # ... existing shortcuts ...
                if event.key == pygame.K_l:
                    self._toggle_physics()
```

This binds **L** to toggle auto-layout, consistent with `V`/`E`/`A`.

### 4d. Draw the button in `draw_buttons`

`draw_buttons` already iterates `self.mode_buttons`. Add the new button to that list in `__addButtons`:

```python
        self.mode_buttons = [
            Button(px, 130, bw, 40, "Add Vertex", ...),
            Button(px, 178, bw, 40, "Add Edge",   ...),
            Button(px, 226, bw, 40, "Animate",    ...),
            self.physics_button,    # ← add here
        ]
```

---

## Step 5 — Run and Tune

### Run the app

```bash
cd /graphvisualizer
uv run graphvisualizer
```

Click **Auto Layout** (or press **L**). Watch the nodes fly apart, settle, and form a clean arrangement.

### Tuning guide

| Parameter | Effect | Start with | When to change |
|---|---|---|---|
| `repulsion` | How far nodes push apart | `800.0` | Nodes too close → increase; too spread → decrease |
| `attraction` | How tightly edges pull | `0.008` | Graph too sparse → increase; too clustered → decrease |
| `damping` | Friction / settling speed | `0.90` | Never settles → decrease (e.g., `0.85`); too slow → increase |
| `temperature` | Initial energy | `100.0` | Nodes oscillate → lower; layout is too rigid → raise |
| `COOLING_FACTOR` | How fast the system cools | `0.995` | Cools too fast (jitter stops immediately) → increase; never settles → decrease |

**Quick tuning recipe:**

1. Add ~30 nodes and connect them randomly.
2. Click **Auto Layout**.
3. If the graph oscillates forever: decrease `temperature` to `50` or `damping` to `0.8`.
4. If nodes are clumped together: increase `repulsion` to `1200`.
5. If edges look stretched: increase `attraction` to `0.012`.

---

## Advanced Topics

### A. Barnes-Hut Approximation (for large graphs)

The repulsion step is O(n²).  For graphs with > 200 nodes, implement a quad-tree to approximate distant forces in O(n log n):

1. Build a quad-tree that encloses all nodes.
2. For each node, traverse the tree: if a cell is "far enough" (size / distance < θ, typically θ = 0.8), treat its centre-of-mass as a single repelling body. Otherwise, recurse into children.

Packages that do this out of the box:
```bash
pip install fa2   # ForceAtlas2 — supports 10k+ nodes
```
Then replace the `_apply_repulsion` body with `fa2`'s layout function.

### B. Pinned Nodes (user drags a node)

The `Node.pinned` field added in Step 1 enables this.  In `physics.py`, skip nodes with `pinned = True` during integration:

```python
    def _clamp_position(self, node):
        if node.pinned:
            return        # don't move pinned nodes
        ...
```

Set `pinned = True` in `App.detectNodeClick` when the user drags a node, and `False` on `MOUSEBUTTONUP`.

### C. Dynamic Cooling Schedule

Instead of a fixed `COOLING_FACTOR`, use a schedule that first allows fast exploration, then fine-tunes:

```python
    def tick(self, graph, delta_t=1.0):
        ...
        self.temperature *= self.COOLING_FACTOR
        # After 100 iterations, switch to aggressive cooling
        if self.iterations > 100:
            self.temperature *= 0.90
```

### D. Refactoring `_apply_centering`

Replace the anonymous-class hack with a proper helper:

```python
    def _apply_centering(self, vertices):
        cx = self.width  / 2.0
        cy = self.height / 2.0
        for v in vertices:
            dx = cx - v.cords.x
            dy = cy - v.cords.y
            dist = sqrt(dx * dx + dy * dy)
            if dist < 0.01:
                continue
            force = 0.001 * dist
            v.apply_force(force * dx / dist, force * dy / dist)
```

### E. Displacement Limiting

Some layouts "explode" because a single node receives too much force.  Cap the maximum displacement per step:

```python
    def _clamp_position(self, node):
        max_disp = 10.0
        dx = node.cords.x - node._last_x
        dy = node.cords.y - node._last_y
        disp = sqrt(dx*dx + dy*dy)
        if disp > max_disp:
            scale = max_disp / disp
            node.cords.x -= (node.cords.x - node._last_x) * scale
            node.cords.y -= (node.cords.y - node._last_y) * scale
```

(Remember to save `node._last_x = node.cords.x` before the position update.)

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Nodes fly off-screen | Temperature too high or no clamping | Lower `temperature`, verify `_clamp_position` runs |
| Graph never settles | Damping too high (close to 1.0) | Lower `damping` to `0.8`–`0.85` |
| All nodes collapse to centre | Repulsion < Attraction | Increase `repulsion` or decrease `attraction` |
| Jittery / never-stops animation | Temperature not cooling | Check `COOLING_FACTOR < 1.0`; verify `tick()` is called every frame |
| Nodes overlap edges | Edge drawing order — edges are drawn first, then nodes on top (this is already correct in your renderer) | No code change needed — nodes render after edges |
| `PhysicsEngine` not found | Module not created or path wrong | Verify `src/graphvisualizer/physics.py` exists and has no syntax errors |
| Graph looks identical before and after layout | `self.render.physics.running` is `False` | Verify the button handler calls `.start()` and `.reset()` |

### Debugging tips

Print the engine state every few frames to see if forces are being computed:

```python
    def tick(self, graph, delta_t=1.0):
        ...
        if self.iterations % 60 == 0:
            print(f"iter={self.iterations} temp={self.temperature:.2f} "
                  f"vx_max={max(abs(v.vx) for v in vertices):.2f}")
```

---

## Complete File Checklist

After following this guide, your modified/new files should be:

```
src/graphvisualizer/
├── graph.py            ← Node has vx, vy, fx, fy, pinned fields
├── physics.py          ← NEW — PhysicsEngine class (FR algorithm)
├── renderer.py         ← Render.physics reference + tick() call
└── app.py              ← Auto Layout button + keyboard shortcut
```

---

## Quick Reference — Minimal Diff

If you prefer to see only the changes, here is a compact summary of every edit:

### `graph.py` — add to `Node.__init__`
```python
self.vx = 0.0; self.vy = 0.0; self.fx = 0.0; self.fy = 0.0; self.pinned = False
```

### `graph.py` — add to `Node` class
```python
def reset_forces(self): self.fx = 0.0; self.fy = 0.0
def apply_force(self, fx, fy): self.fx += fx; self.fy += fy
def update_velocity(self, damping=0.9, dt=1.0):
    ax = self.fx * dt; ay = self.fy * dt
    self.vx = (self.vx + ax) * damping
    self.vy = (self.vy + ay) * damping
    self.cords.x += self.vx; self.cords.y += self.vy
```

### `renderer.py` — add to `Render.__init__`
```python
self.physics = None
```

### `renderer.py` — add at top of `draw_graph`
```python
if self.physics is not None and self.physics.running:
    self.physics.tick(self.graph)
```

### `app.py` — add button in `__addButtons`
```python
self.physics_button = SmallButton(px, 350, bw, 38, "Auto Layout",
                                   action=self._toggle_physics,
                                   active_color=Colors.ACCENT_ANIMATE)
```

### `app.py` — add handler
```python
def _toggle_physics(self):
    from graphvisualizer.physics import PhysicsEngine
    if self.render.physics is None:
        w, h = self.screen.get_size()
        self.render.physics = PhysicsEngine(width=w-240, height=h)
    self.render.physics.reset(); self.render.physics.start()
    for v in self.graph.vertices.values():
        v.color = Colors.NODE_DEFAULT
```

---

## Next Steps After This Guide

1. **Undo manual dragging** — implement pinned nodes (Advanced Topic B) so users can still nudge specific nodes after layout.
2. **Edge bundling** — group parallel edges visually for cleaner rendering.
3. **Incremental layout** — when a new node is added, warm-start the simulation rather than re-running from scratch.
4. **Export layout** — serialise final `cords` positions to JSON so the next session opens with the same arrangement.

---

*Happy laying out!*
