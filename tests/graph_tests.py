import unittest
from graphvisualizer.graph import Graph 

class TestGraph(unittest.TestCase):
    
    def test_matrix_undirected_unweighted(self):
        # Test 3 vertices, undirected, unweighted using matrix
        g = Graph(vertices=3, is_directed=False, weighted=False, representation="matrix")
        g.addEdge(0, 1)
        g.addEdge(1, 2)
        
        self.assertEqual(g.adjMatrix[0][1], 1)
        self.assertEqual(g.adjMatrix[1][0], 1)  # Check symmetry
        self.assertEqual(g.adjMatrix[1][2], 1)
        self.assertEqual(g.adjMatrix[2][1], 1)
        self.assertEqual(g.adjMatrix[0][2], 0)  # No edge

    def test_matrix_directed_weighted(self):
        # Test directed, weighted graph using matrix
        g = Graph(vertices=3, is_directed=True, weighted=True, representation="matrix")
        g.addEdge(0, 1, weight=5)
        
        self.assertEqual(g.adjMatrix[0][1], 5)
        self.assertEqual(g.adjMatrix[1][0], 0)  # Directed, so reverse should be 0

    def test_list_undirected_unweighted(self):
        # Test undirected, unweighted graph using adjacency list
        g = Graph(vertices=3, is_directed=False, weighted=False, representation="list")
        g.addEdge(0, 1)
        g.addEdge(0, 2)
        
        self.assertIn(1, g.adjList[0])
        self.assertIn(2, g.adjList[0])
        self.assertIn(0, g.adjList[1])  # Check bidirectional addition
        self.assertIn(0, g.adjList[2])

    def test_list_directed_weighted(self):
        # Test directed, weighted graph using adjacency list
        g = Graph(vertices=3, is_directed=True, weighted=True, representation="list")
        g.addEdge(0, 1, weight=10)
        
        self.assertEqual(g.adjList[0][1], 10)
        self.assertNotIn(0, g.adjList[1])  # Directed, so no reverse edge

    def test_remove_edge(self):
        # Test edge removal for both matrix and list
        # Matrix test
        g_mat = Graph(vertices=3, is_directed=False, weighted=False, representation="matrix")
        g_mat.addEdge(0, 1)
        g_mat.removeEdge(0, 1)
        self.assertEqual(g_mat.adjMatrix[0][1], 0)
        self.assertEqual(g_mat.adjMatrix[1][0], 0)

        # List test
        g_list = Graph(vertices=3, is_directed=False, weighted=False, representation="list")
        g_list.addEdge(0, 1)
        g_list.removeEdge(0, 1)
        self.assertNotIn(1, g_list.adjList[0])
        self.assertNotIn(0, g_list.adjList[1])

if __name__ == "__main__":
    unittest.main() 
    