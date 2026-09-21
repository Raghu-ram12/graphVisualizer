import pygame
from graphvisualizer.config import Colors


class Render:

    def __init__(self, graph, screen):

        self.graph          = graph
        self.screen         = screen
        self.animationIndex = 0
        self.animationTimer = 0
        self.animationSpeed = 500
        self.orderList      = None
        self.prev           = None
        self.physics = None

   

    def _node_ring(self, pos, radius, ring_color, ring_thickness=3):
        """Draw a colored ring around a node by overdrawing a larger circle first."""
        pygame.draw.circle(self.screen, ring_color, pos, radius + ring_thickness)

    
    def toggle_physics(self):
        """Start or stop the physics simulation."""
        if self.physics is None:
            from graphvisualizer.physics import PhysicsEngine
            screen_w, screen_h = self.screen.get_size()
            self.physics = PhysicsEngine(
                width=screen_w - 240,
                height=screen_h,
            )
        if self.physics.running:
            self.physics.stop()
        else:
            self.physics.start()

    def draw_graph(self, delta_t=1.0):

        if self.physics is not None and self.physics.running:
            self.physics.tick(self.graph, delta_t=delta_t)

        for edge in self.graph.edges:

            start_pos = (edge.start_node.cords.x, edge.start_node.cords.y)
            end_pos   = (edge.end_node.cords.x,   edge.end_node.cords.y)

          
            color = edge.color if edge.color else Colors.EDGE_DEFAULT

            if color == Colors.EDGE_DEFAULT:
                
                pygame.draw.aaline(self.screen, color, start_pos, end_pos)
            else:
                pygame.draw.line(self.screen, color, start_pos, end_pos,
                                 edge.thickness + 1)

    
        font = pygame.font.SysFont("consolas", 16, bold=True)

        for vertex_id, vertex in self.graph.vertices.items():

            pos    = (vertex.cords.x, vertex.cords.y)
            radius = vertex.radius
            color  = vertex.color

          
            if color == Colors.NODE_SELECTED:
                self._node_ring(pos, radius, Colors.NODE_SELECTED, ring_thickness=4)
            elif color == Colors.NODE_VISITED:
                self._node_ring(pos, radius, Colors.NODE_VISITED, ring_thickness=3)
            elif color == Colors.NODE_CURRENT:
                self._node_ring(pos, radius, Colors.NODE_CURRENT, ring_thickness=4)

            
            pygame.draw.circle(self.screen, color, pos, radius)

            text_surface = font.render(str(vertex.data), True, Colors.TEXT_NODE)
            text_rect    = text_surface.get_rect(center=pos)
            self.screen.blit(text_surface, text_rect)

  

    def startAnimation(self, start_id, mode="DFS"):
        """Reset all node/edge colors then build the traversal order."""

        
        for vertex in self.graph.vertices.values():
            vertex.color = Colors.NODE_DEFAULT

        # Reset edges
        for edge in self.graph.edges:
            edge.color = None

        if mode == "BFS":
            self.orderList = self.graph.bfs(start_id)
        else:
            self.orderList = self.graph.dfs_iterative(start_id)

        self.animationIndex = 0
        self.animationTimer = 0
        self.prev           = None

    def _color_edge_between(self, id_a, id_b):
        """Color the edge(s) connecting two node IDs in the visited color."""
        for edge in self.graph.edges:
            a = edge.start_node.id
            b = edge.end_node.id
            if (a == id_a and b == id_b) or (a == id_b and b == id_a):
                edge.color     = Colors.EDGE_VISITED
                edge.thickness = 2

    def updateAnimation(self, clock):

        if not self.orderList or self.animationIndex >= len(self.orderList):
            return

        self.animationTimer += clock.get_time()

        if self.animationTimer >= self.animationSpeed:

            current_id = self.orderList[self.animationIndex]

            
            if self.prev is not None:
                self.prev.color = Colors.NODE_VISITED
                self._color_edge_between(self.prev.id, current_id)

           
            current_node       = self.graph.vertices[current_id]
            current_node.color = Colors.NODE_CURRENT
            self.prev          = current_node

            self.animationIndex += 1
            self.animationTimer  = 0
