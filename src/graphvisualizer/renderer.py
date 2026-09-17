import pygame 
from graphvisualizer.config import Colors 
class Render:

    def __init__(self,graph:Graph,screen):
        
        self.graph=graph
        self.screen=screen 

    
    def draw_graph(self):

        for edge in self.graph.edges:

            start_pos=(edge.start_node.cords.x,edge.start_node.cords.y)
            end_pos=(edge.end_node.cords.x,edge.end_node.cords.y)
            pygame.draw.line(self.screen,Colors.ORANGE,start_pos,end_pos,edge.thickness)
        
         
        for vertex_id in self.graph.vertices:

            vertex=self.graph.vertices[vertex_id] 

            pos=(vertex.cords.x,vertex.cords.y)

            pygame.draw.circle(self.screen,Colors.WHITE,pos,vertex.radius)
            font = pygame.font.Font(None, 20)

            text_surface = font.render(f"{vertex.data}", True, (0, 0, 0))

            text_rect = text_surface.get_rect()
            text_rect.center = pos  

            self.screen.blit(text_surface, text_rect)
        
    
    def animate_bfs(self):
        
        pass
    
    def animate_dfs(self):
        pass 

    
   
        


