from collections import deque

class Coordinates:
    
    def __init__(self,x,y):
        self.x=x
        self.y=y 
    def world_to_screen(self):
        pass

class Node:
    id_=0
    def __init__(self,x,y):

        self.color=None 
        self.cords=Coordinates(x,y)
        self.data=None 
        self.radius=None 
        self.id=Node.id_
        Node.id_+=1 
    



class Edge:

    def __init__(self,start,end,weight=1):

        self.color=None 
        self.weight=weight
        self.start_node=start 
        self.end_node=end
        self.thickness=2


class Graph:

    def __init__(self):

        self.vertices={}
        self.edges=[]
        self.adjList=[]

    def addNode(self,x,y):

        newNode=Node(x,y)

        self.vertices[newNode.id]=newNode 
        
        
    def addEdge(self,id1,id2,directed=False):

        if id1 in self.vertices and id2 in self.vertices:     

            vertex1=self.vertices[id1]
            vertex2=self.vertices[id2]
            newEdge=Edge(vertex1,vertex2) 
            
            self.adjList[id1].append(vertex2)

            if not directed:

                self.adj_list[id2].append(vertex1)

    
    
    def dfs(self,start_id,visited=None,order=None):

        if visited is None:

            visited=set()
        
        if order is None:

            order=[]
        
        visited.add(start_id) 
        order.append(start_id)
        vertex=self.vertices[start_id] 

        for neighbor in self.adjList[start_id]:

            if neighbor.id not in visited:

                self.dfs(neighbor.id,visited,order)
        
        return order 
    
    
    def bfs(self,start_id,visited=None,order=None):

        visited={[start_id]}

        order=[start_id] 

        queue=deque([start_id]) 

        while queue:
            current=queue.left_pop()
            order.append(current)

            for neighbor in self.adjList[current]:

                if neighbor.id not in visited:

                    visited.add(neighbor.id) 
                    queue.append(neighbor) 
        
        return order 
    

