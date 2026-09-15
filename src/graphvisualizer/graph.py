from collections import defaultdict


class Graph:

    def __init__(
        self, vertices, is_directed=False, weighted=False, representation="list"
    ):

        self.vertices = vertices
        self.represent = representation
        self.directed=is_directed 
        self.weighted=weighted

        if self.represent == "matrix":

            self.adjMatrix = [[0] * self.vertices for _ in range(vertices)]

        elif self.represent == "list":

            if self.weighted:

                self.adjList = defaultdict(dict)
            else:

                self.adjList = defaultdict(set)

    def addVertex(self, vertex):

        if self.represent == "list":

            if self.weighted:

                if vertex not in self.adjList:

                    self.adjList[vertex] = dict()

            else:

                if vertex not in self.adjList:

                    self.adjList[vertex] = set()

    def addEdge(self, start, end, weight=1):

        if self.represent == "matrix":

            val = weight if self.weighted else 1

            self.adjMatrix[start][end] = val

            if not self.directed:

                self.adjMatrix[end][start] = val

        else:

            self.addVertex(start)

            self.addVertex(end)

            if self.weighted:

                self.adjList[start][end] = weight

                if not self.directed:

                    self.adjList[end][start] = weight

            else:

                self.adjList[start].add(end)

                if not self.directed:

                    self.adjList[end].add(start)


    def removeEdge(self, start, end):

        if self.represent == "matrix":

            self.adjMatrix[start][end] = 0
            if not self.directed:
                self.adjMatrix[end][start] = 0

        elif self.represent == "list":

            if start in self.adjList:
                if self.weighted:

                    self.adjList[start].pop(end, None)
                else:

                    self.adjList[start].discard(end)

            if not self.directed and end in self.adjList:

                if self.weighted:
                    self.adjList[end].pop(start, None)
                else:
                    self.adjList[end].discard(start)
    