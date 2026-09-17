from graphvisualizer.graph import Graph
from graphvisualizer.renderer import Render
from collections import deque
import pygame


class App:

    __mode = "addVertex"

    def __init__(self):
        self.graph = Graph(20)
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.running = True
        self.render = Render(self.graph, self.screen)
        self.prevVertex = None
        self.start_id = None

    def detectNodeClick(self, pos):

        x, y = pos
        for vertex_id, vertex in self.graph.vertices.items():
            dx = x - vertex.cords.x
            dy = y - vertex.cords.y
            squared_dist = (dx**2) + (dy**2)

            if squared_dist < (vertex.radius**2):
                return vertex_id
        return None

    def handleUserInput(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_e:

                    App.setAppMode("addEdge")
                    print("MODE changed to: addEdge")

                elif event.key == pygame.K_v:

                    App.setAppMode("addVertex")
                    self.prevVertex = None
                    print("MODE changed to: addVertex")

                if event.key == pygame.K_a:

                    App.setAppMode("animate")
                    print("MODE changed to: Animate")

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    clicked_vertex = self.detectNodeClick(event.pos)

                    if App.getAppMode() == "addVertex":

                        if clicked_vertex is None:

                            x, y = event.pos
                            self.graph.addNode(x, y)
                            print(f"Added vertex at ({x}, {y})")

                    elif App.getAppMode() == "addEdge":

                        if clicked_vertex is not None:
                            if self.prevVertex is None:

                                self.prevVertex = clicked_vertex
                                vertex = self.graph.vertices[self.prevVertex]
                                vertex.highlight()
                                print(f"First vertex selected: {self.prevVertex}")
                            else:

                                print(
                                    f"Connecting: {self.prevVertex} <---> {clicked_vertex}"
                                )
                                self.graph.addEdge(self.prevVertex, clicked_vertex)
                                vertex = self.graph.vertices[self.prevVertex]
                                self.graph.vertices[clicked_vertex].unHighlight()
                                vertex.unHighlight()
                                self.prevVertex = None

                    elif App.getAppMode() == "animate":

                        if clicked_vertex is not None:

                            print("animation started")

                            self.render.startAnimation(clicked_vertex)

    @classmethod
    def setAppMode(cls, mode=None):
        cls.__mode = mode

    @classmethod
    def getAppMode(cls):
        return cls.__mode

    def run(self):

        while self.running:
            self.screen.fill((0, 0, 0))
            self.handleUserInput()
            self.render.draw_graph()
            self.render.updateAnimation(self.clock)
            pygame.display.flip()
            self.clock.tick(60)
