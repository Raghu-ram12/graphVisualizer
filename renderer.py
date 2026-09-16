class Render:

    def __init__(self,graph:Graph,screen):
        
        self.graph=graph
        self.screen=screen 

    
    def draw_graph(self):


        for edge in self.graph.edges:

            start_pos=(edge.start.cords.x,edge.start.cords.y)
            end_pos=(edge.end.cords.x,edge.end.cords.y)
            pygame.draw.line(screen,edge.color,start_pos,end_pos,edge.thickness)
        
        
        for vertex_id in self.graph.vertices:

            vertex=self.graph.vertices[vertex_id] 

            pos=(vertex.cords.x,vertex.cords.y)

            pygame.draw.circle(screen,vertex.color,pos,vertex.radius) 
    
    def animate_bfs(self):
        pass 
    
    def animate_dfs(self):
        pass 
    
   
        


