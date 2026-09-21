"""
Fruchterman-Reingold force-directed graph layout engine.

Pure coordinate math — no Pygame dependency.  The renderer calls
``PhysicsEngine.tick(graph)`` once per frame while auto-layout is active.

Force model
-----------
Every pair of nodes repels:   F_rep = k² / d²
Every edge pulls its ends:    F_att = d / k

where ``k = sqrt(canvas_area / n)`` is the ideal separation for ``n``
nodes.  At ``d = k`` the two forces cancel, so the graph settles into an
even, readable arrangement.  A soft wall repulsion keeps nodes inside the
canvas, and a temperature-gated displacement cap prevents explosions.
"""

from math import sqrt


class PhysicsEngine:
    """Fruchterman-Reingold force-directed graph layout."""

    DEFAULT_REPULSION = 1.0
    DEFAULT_ATTRACTION = 1.0
    DEFAULT_DAMPING = 0.85
    DEFAULT_TEMPERATURE = 100.0
    MIN_TEMPERATURE = 0.5
    COOLING_FACTOR = 0.99
    WALL_REPULSION = 0.4
    MARGIN = 30.0
    MIN_OPTIMAL_DISTANCE = 20.0
    MAX_OPTIMAL_DISTANCE = 150.0

    def __init__(self, width=1020, height=720,
                 repulsion=None, attraction=None,
                 damping=None, temperature=None):
        self.width = width
        self.height = height
        self.repulsion = repulsion or self.DEFAULT_REPULSION
        self.attraction = attraction or self.DEFAULT_ATTRACTION
        self.damping = damping or self.DEFAULT_DAMPING
        self.temperature = temperature or self.DEFAULT_TEMPERATURE
        self.running = False
        self.iterations = 0

    # ------------------------------------------------------------------ #
    #  Public API                                                         #
    # ------------------------------------------------------------------ #

    def tick(self, graph, delta_t=1.0):
        """Perform one simulation step. Call once per frame."""
        if not self.running:
            return

        vertices = list(graph.vertices.values())
        n = len(vertices)
        if n == 0:
            return

        # Ideal separation — scales with canvas area and node count
        k = sqrt((self.width * self.height) / n)
        k = max(self.MIN_OPTIMAL_DISTANCE,
                min(k, self.MAX_OPTIMAL_DISTANCE))

        # 1. Reset force accumulators
        for v in vertices:
            v.reset_forces()

        # 2. Repulsion between every pair of nodes (F = k² / d²)
        self._apply_repulsion(vertices, k)

        # 3. Attraction along every edge (F = d / k)
        self._apply_attraction(graph.edges, k)

        # 4. Soft wall repulsion — keeps nodes inside the canvas
        self._apply_wall_repulsion(vertices)

        # 5. Integrate velocities → positions
        for v in vertices:
            if getattr(v, "pinned", False):
                continue
            prev_x, prev_y = v.cords.x, v.cords.y
            v.update_velocity(damping=self.damping, dt=delta_t)

            # Temperature-gated displacement cap (prevents explosions)
            dx = v.cords.x - prev_x
            dy = v.cords.y - prev_y
            disp = sqrt(dx * dx + dy * dy)
            max_disp = self.temperature * 0.15 * delta_t
            if disp > max_disp:
                scale = max_disp / disp
                v.cords.x = prev_x + dx * scale
                v.cords.y = prev_y + dy * scale

            self._clamp_position(v)

        # 6. Cool down
        self.temperature *= self.COOLING_FACTOR
        if self.temperature < self.MIN_TEMPERATURE:
            self.temperature = self.MIN_TEMPERATURE
        self.iterations += 1

    def start(self):
        """Begin (or resume) the simulation."""
        self.running = True
        self.temperature = self.DEFAULT_TEMPERATURE
        self.iterations = 0

    def stop(self):
        """Freeze the simulation in place."""
        self.running = False

    def reset(self):
        """Reset temperature so the next start is fully energetic."""
        self.temperature = self.DEFAULT_TEMPERATURE
        self.iterations = 0

    # ------------------------------------------------------------------ #
    #  Force helpers                                                      #
    # ------------------------------------------------------------------ #

    def _apply_repulsion(self, vertices, k):
        """Every pair of nodes repels each other (O(n²))."""
        k2 = k * k
        for i, a in enumerate(vertices):
            ax = a.cords.x
            ay = a.cords.y
            for b in vertices[i + 1:]:
                dx = b.cords.x - ax
                dy = b.cords.y - ay
                dist = max(sqrt(dx * dx + dy * dy), 0.01)
                force = k2 / (dist * dist) * self.repulsion
                ux = dx / dist
                uy = dy / dist
                a.apply_force(-force * ux, -force * uy)
                b.apply_force(force * ux, force * uy)

    def _apply_attraction(self, edges, k):
        """Each edge acts like a spring pulling its endpoints together."""
        for edge in edges:
            a = edge.start_node
            b = edge.end_node
            dx = b.cords.x - a.cords.x
            dy = b.cords.y - a.cords.y
            dist = max(sqrt(dx * dx + dy * dy), 0.01)
            force = (dist / k) * self.attraction
            ux = dx / dist
            uy = dy / dist
            a.apply_force(force * ux, force * uy)
            b.apply_force(-force * ux, -force * uy)

    def _apply_wall_repulsion(self, vertices):
        """Push nodes away from canvas edges so they don't pile up at the border."""
        m = self.MARGIN
        w = self.WALL_REPULSION
        for v in vertices:
            x, y = v.cords.x, v.cords.y
            if x < m:
                v.apply_force(w * (m - x), 0.0)
            elif x > self.width - m:
                v.apply_force(w * (self.width - m - x), 0.0)
            if y < m:
                v.apply_force(0.0, w * (m - y))
            elif y > self.height - m:
                v.apply_force(0.0, w * (self.height - m - y))

    def _clamp_position(self, node):
        """Hard safety clamp — keep nodes inside the canvas."""
        m = self.MARGIN
        node.cords.x = max(m, min(self.width - m, node.cords.x))
        node.cords.y = max(m, min(self.height - m, node.cords.y))
