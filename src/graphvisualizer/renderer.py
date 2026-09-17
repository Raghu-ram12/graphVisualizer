import pygame
from graphvisualizer.config import Colors


class Render:

    def __init__(self, graph: Graph, screen):

        self.graph = graph
        self.screen = screen
        self.animationIndex = 0
        self.animationTimer = 0
        self.animationSpeed = 500
        self.orderList = None 
        self.prev=None

    def draw_graph(self):

        for edge in self.graph.edges:

            start_pos = (edge.start_node.cords.x, edge.start_node.cords.y)

            end_pos = (edge.end_node.cords.x, edge.end_node.cords.y)

            pygame.draw.line(
                self.screen, Colors.ORANGE, start_pos, end_pos, edge.thickness
            )

        for vertex_id in self.graph.vertices:

            vertex = self.graph.vertices[vertex_id]

            pos = (vertex.cords.x, vertex.cords.y)

            pygame.draw.circle(self.screen, vertex.color, pos, vertex.radius)

            font = pygame.font.Font(None, 20)

            text_surface = font.render(f"{vertex.data}", True, (0, 0, 0))

            text_rect = text_surface.get_rect()

            text_rect.center = pos

            self.screen.blit(text_surface, text_rect)

    def startAnimation(self, start_id, mode="DFS"):

        for vertex_id, vertex in self.graph.vertices.items():

            vertex.unHighlight()

        if mode == "BFS":

            self.orderList = self.graph.bfs(start_id)
        else:

            self.orderList = self.graph.dfs_iterative(start_id)

        self.animationIndex = 0
        self.animationTimer = 0

    def updateAnimation(self, clock):

        if self.orderList and self.animationIndex < len(self.orderList):

            self.animationTimer += clock.get_time()

        if self.animationTimer >= self.animationSpeed:

            current_id = self.orderList[self.animationIndex]
            if self.prev is not None:
                self.prev.color=Colors.HOVERED

            self.prev=self.graph.vertices[current_id]
            self.prev.highlight()
            self.animationIndex += 1
            self.animationTimer = 0
