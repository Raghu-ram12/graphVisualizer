from collections import deque
import pygame
from graphvisualizer.config import Colors


class Coordinates:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def world_to_screen(self):
        pass


class Node:

    id_ = 0
    radius = 10

    def __init__(self, x, y, data=None):

        self.color = Colors.NODE_DEFAULT
        self.cords = Coordinates(x, y)
        self.data  = data or Node.id_
        self.radius = Node.radius
        self.id    = Node.id_
        self.vx      = 0.0    # velocity x
        self.vy      = 0.0    # velocity y
        self.fx      = 0.0    # accumulated force x
        self.fy      = 0.0    # accumulated force y
        self.pinned  = False  # True if user dragged this node manually
        Node.id_ += 1

    @classmethod
    def set_radius(cls, radius):
        cls.radius = radius

    def highlight(self):
        self.color = Colors.NODE_SELECTED

    def unHighlight(self): 
        self.color = Colors.NODE_DEFAULT 
    @classmethod
    def reset(cls):
        cls.id_=0
    
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

       
        max_speed = 15.0
        speed = (self.vx**2 + self.vy**2)**0.5
        if speed > max_speed:
            self.vx = (self.vx / speed) * max_speed
            self.vy = (self.vy / speed) * max_speed

        # Update position
        self.cords.x += self.vx
        self.cords.y += self.vy

class Edge:

    def __init__(self, start, end, weight=1):

        self.color = None
        self.weight = weight
        self.start_node = start
        self.end_node = end
        self.thickness = 2


from collections import deque


class Graph:

    def __init__(self, radius=None):

        if radius:
            Node.set_radius(radius)

        self.vertices = {}
        self.edges = []
        self.adjList = {}

    def addNode(self, x, y, data=None,vx=0,vy=0):

        newNode = Node(x, y, data)
        newNode.vx = vx
        newNode.vy = vy
        self.vertices[newNode.id] = newNode
        self.adjList[newNode.id] = []

        return newNode.id

    def addEdge(self, id1, id2, directed=False):

        if id1 not in self.vertices or id2 not in self.vertices:
            
            raise ValueError(f"Cannot add edge: {id1} or {id2} not in graph")

        vertex1 = self.vertices[id1]
        vertex2 = self.vertices[id2]

        newEdge = Edge(vertex1, vertex2)
        self.edges.append(newEdge)

        self.adjList[id1].append(vertex2)

        if not directed:
            self.adjList[id2].append(vertex1)
    
    def clearGraph(self):
      
        self.adjList.clear()
        self.vertices.clear() 
        self.edges.clear() 
        Node.reset()


    def dfs_iterative(self, start_id):
        

        if start_id not in self.vertices:
            raise ValueError(f"No node with id {start_id} in graph")

        visited = set()
        order = []
        stack = [start_id]

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            order.append(current)

            for neighbor in self.adjList[current]:
                if neighbor.id not in visited:
                    stack.append(neighbor.id)

        return order

    def bfs(self, start_id):

        if start_id not in self.vertices:
            raise ValueError(f"No node with id {start_id} in graph")

        visited = {start_id}
        order = []
        queue = deque([start_id])

        while queue:
            current = queue.popleft()
            order.append(current)

            for neighbor in self.adjList[current]:
                if neighbor.id not in visited:
                    visited.add(neighbor.id)
                    queue.append(neighbor.id)

        return order    