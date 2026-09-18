from graphvisualizer.graph import Graph
from graphvisualizer.renderer import Render
import pygame
from graphvisualizer.config import Colors




def draw_rounded_rect(surface, color, rect, radius=8):
    pygame.draw.rect(surface, color, rect, border_radius=radius)




class Button:
    """Mode button with a colored left-accent strip and a keyboard shortcut badge."""

    ACCENT_W = 4
    BADGE_W  = 26
    BADGE_H  = 22

    def __init__(self, x, y, width, height, text,
                 accent_color=Colors.BLUE,
                 shortcut: str = "",
                 action=None):

        self.rect         = pygame.Rect(x, y, width, height)
        self.text         = text
        self.accent_color = accent_color
        self.shortcut     = shortcut
        self.action       = action

        self.font       = pygame.font.SysFont("consolas", 17)
        self.badge_font = pygame.font.SysFont("consolas", 14, bold=True)

        self.is_hovered = False
        self.is_active  = False   

    def draw(self, surface):
        # Background
        if self.is_active:
            bg = Colors.SURFACE_ACTIVE
        elif self.is_hovered:
            bg = Colors.SURFACE_HOVER
        else:
            bg = Colors.BG_PANEL

        draw_rounded_rect(surface, bg, self.rect, radius=8)

        
        strip_w = self.ACCENT_W + 2 if self.is_active else self.ACCENT_W
        strip_rect = pygame.Rect(self.rect.x, self.rect.y, strip_w, self.rect.height)
        draw_rounded_rect(surface, self.accent_color, strip_rect, radius=4)

        # Label
        text_surf = self.font.render(self.text, True, Colors.TEXT_PRIMARY)
        text_y    = self.rect.centery - text_surf.get_height() // 2
        surface.blit(text_surf, (self.rect.x + strip_w + 10, text_y))

        # Shortcut badge
        if self.shortcut:
            badge_rect = pygame.Rect(
                self.rect.right - self.BADGE_W - 6,
                self.rect.centery - self.BADGE_H // 2,
                self.BADGE_W, self.BADGE_H
            )
            draw_rounded_rect(surface, Colors.SHORTCUT_BADGE, badge_rect, radius=5)
            badge_surf = self.badge_font.render(self.shortcut, True, self.accent_color)
            bx = badge_rect.centerx - badge_surf.get_width()  // 2
            by = badge_rect.centery - badge_surf.get_height() // 2
            surface.blit(badge_surf, (bx, by))

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        """Returns True if this button consumed the click."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                return True
        return False


class SmallButton:

    """Compact +/– or toggle button used for animation controls."""

    def __init__(self, x, y, w, h, text, action=None, active_color=None):
        self.rect         = pygame.Rect(x, y, w, h)
        self.text         = text
        self.action       = action
        self.active_color = active_color   # vivid bg when is_active=True
        self.font         = pygame.font.SysFont("consolas", 15, bold=True)
        self.is_hovered   = False
        self.is_active    = False

    def draw(self, surface):
        if self.is_active and self.active_color:
            bg         = self.active_color
            text_color = Colors.BLACK          # dark text on vivid bg
        elif self.is_active:
            bg         = Colors.SURFACE_ACTIVE
            text_color = Colors.TEXT_PRIMARY
        elif self.is_hovered:
            bg         = Colors.SURFACE_HOVER
            text_color = Colors.TEXT_PRIMARY
        else:
            bg         = Colors.SEPARATOR
            text_color = Colors.TEXT_PRIMARY

        draw_rounded_rect(surface, bg, self.rect, radius=5)
        surf = self.font.render(self.text, True, text_color)
        bx   = self.rect.centerx - surf.get_width()  // 2
        by   = self.rect.centery - surf.get_height() // 2
        surface.blit(surf, (bx, by))

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                return True
        return False




class App:

    PANEL_WIDTH = 240
    __mode      = "addVertex"

    MODE_META = {
        "addVertex": ("Vertex Mode", Colors.ACCENT_VERTEX),
        "addEdge":   ("Edge Mode",   Colors.ACCENT_EDGE),
        "animate":   ("Animate",     Colors.ACCENT_ANIMATE),
    }

    STATUS_HINTS = {
        "addVertex": "Click canvas to add a node",
        "addEdge":   "Select first node",
        "animate":   "Click a node to start",
    }

    def __init__(self):

        self.graph  = Graph(20)
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        pygame.display.set_caption("Graph Visualizer")
        self.clock      = pygame.time.Clock()
        self.running    = True
        self.render     = Render(self.graph, self.screen)
        self.prevVertex = None

        # Fonts
        self.font_title   = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_section = pygame.font.SysFont("consolas", 12)
        self.font_stat    = pygame.font.SysFont("consolas", 16)
        self.font_status  = pygame.font.SysFont("consolas", 13)
        self.font_badge   = pygame.font.SysFont("consolas", 14, bold=True)

        self._status_override = None
        self._anim_mode  = "DFS"
        self._anim_speed = 500
        self._speed_min  = 100  
        self._speed_max  = 1000
        self._speed_step = 100

        self.mode_buttons  = []
        self.anim_controls = []
        self.danger_button = None

        self.__addButtons()

   

    def __addButtons(self):
        px = 16
        bw = self.PANEL_WIDTH - px * 2

        self.mode_buttons = [
            Button(px, 130, bw, 40, "Add Vertex",
                   accent_color=Colors.ACCENT_VERTEX, shortcut="V",
                   action=lambda: self._switch_mode("addVertex")),
            Button(px, 178, bw, 40, "Add Edge",
                   accent_color=Colors.ACCENT_EDGE,   shortcut="E",
                   action=lambda: self._switch_mode("addEdge")),
            Button(px, 226, bw, 40, "Animate",
                   accent_color=Colors.ACCENT_ANIMATE, shortcut="A",
                   action=lambda: self._switch_mode("animate")),
        ]

        # anim_controls y is updated dynamically in draw_buttons each frame
        sw = 38
        self.anim_controls = [
            SmallButton(px,             430, sw, 28, "-",
                        action=lambda: self._adjust_speed(-self._speed_step)),
            SmallButton(px + sw + 4,   430, sw, 28, "+",
                        action=lambda: self._adjust_speed(+self._speed_step)),
            SmallButton(px + sw*2 + 12, 430, 60, 28, "DFS",
                        action=lambda: self._toggle_anim_mode("DFS"),
                        active_color=Colors.ACCENT_ANIMATE),
            SmallButton(px + sw*2 + 76, 430, 60, 28, "BFS",
                        action=lambda: self._toggle_anim_mode("BFS"),
                        active_color=Colors.ACCENT_ANIMATE),
        ]

        screen_h = self.screen.get_height()
        self.danger_button = SmallButton(
            px, screen_h - 50, bw, 38, "Clear Graph",
            action=self._clear_graph
        )

        self._sync_active_states()

    def _switch_mode(self, mode):
        App.setAppMode(mode)
        self.prevVertex       = None
        self._status_override = None
        self._sync_active_states()

    def _adjust_speed(self, delta):
        self._anim_speed = max(self._speed_min,
                               min(self._speed_max, self._anim_speed + delta))
        self.render.animationSpeed = self._anim_speed

    def _toggle_anim_mode(self, mode):
        self._anim_mode = mode
        self._sync_active_states()

    def _clear_graph(self):
        self.graph.vertices.clear()
        self.graph.edges.clear()
        self.graph.adjList.clear()
        self.render.orderList = None
        self.prevVertex       = None

    def _sync_active_states(self):
        mode_map = ["addVertex", "addEdge", "animate"]
        for i, btn in enumerate(self.mode_buttons):
            btn.is_active = (App.getAppMode() == mode_map[i])
        for ctrl in self.anim_controls:
            if ctrl.text in ("DFS", "BFS"):
                ctrl.is_active = (ctrl.text == self._anim_mode)

  

    def detectNodeClick(self, pos):
        x, y = pos
        if x < self.PANEL_WIDTH:
            return None
        for vertex_id, vertex in self.graph.vertices.items():
            dx = x - vertex.cords.x
            dy = y - vertex.cords.y
            if (dx**2 + dy**2) < vertex.radius**2:
                return vertex_id
        return None

    def handleUserInput(self):
        all_buttons = self.mode_buttons + self.anim_controls + [self.danger_button]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.MOUSEMOTION:
                for btn in all_buttons:
                    btn.check_hover(event.pos)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self._switch_mode("addEdge")
                elif event.key == pygame.K_v:
                    self._switch_mode("addVertex")
                elif event.key == pygame.K_a:
                    self._switch_mode("animate")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                consumed = False
                for btn in all_buttons:
                    if btn.handle_event(event):
                        consumed = True
                        break
                if consumed:
                    continue

                if event.button == 1:
                    clicked_vertex = self.detectNodeClick(event.pos)
                    mode = App.getAppMode()

                    if mode == "addVertex":
                        if clicked_vertex is None:
                            x, y = event.pos
                            if x >= self.PANEL_WIDTH:
                                self.graph.addNode(x, y)

                    elif mode == "addEdge":
                        if clicked_vertex is not None:
                            if self.prevVertex is None:
                                self.prevVertex = clicked_vertex
                                self.graph.vertices[clicked_vertex].highlight()
                                self._status_override = "Now select second node"
                            else:
                                self.graph.addEdge(self.prevVertex, clicked_vertex)
                                self.graph.vertices[self.prevVertex].unHighlight()
                                self.graph.vertices[clicked_vertex].unHighlight()
                                self.prevVertex       = None
                                self._status_override = None

                    elif mode == "animate":
                        if clicked_vertex is not None:
                            self.render.startAnimation(clicked_vertex,
                                                       mode=self._anim_mode)

   
    def _draw_separator(self, y):
        pygame.draw.line(self.screen, Colors.SEPARATOR,
                         (10, y), (self.PANEL_WIDTH - 10, y), 1)

    def _draw_section_label(self, text, y):
        surf = self.font_section.render(text, True, Colors.TEXT_MUTED)
        self.screen.blit(surf, (16, y))

    def drawPanel(self):
        screen_h = self.screen.get_height()

      
        self.danger_button.rect.y = screen_h - 50

      
        pygame.draw.rect(self.screen, Colors.BG_PANEL,
                         pygame.Rect(0, 0, self.PANEL_WIDTH, screen_h))

        # Elevated title block
        pygame.draw.rect(self.screen, Colors.BG_SIDEBAR,
                         pygame.Rect(0, 0, self.PANEL_WIDTH, 60))

        # Right border
        pygame.draw.line(self.screen, Colors.SEPARATOR,
                         (self.PANEL_WIDTH, 0), (self.PANEL_WIDTH, screen_h), 2)

        # Title
        title = self.font_title.render("GRAPH VISUALIZER", True, Colors.TEXT_PRIMARY)
        self.screen.blit(title, (16, 20))

      
        mode_name, mode_color = self.MODE_META.get(
            App.getAppMode(), ("Unknown", Colors.GRAY)
        )
        badge_text = self.font_badge.render(mode_name, True, mode_color)
        badge_w    = badge_text.get_width() + 24
        badge_rect = pygame.Rect(16, 68, badge_w, 26)
        draw_rounded_rect(self.screen, Colors.SURFACE_ACTIVE, badge_rect, radius=13)
        pygame.draw.circle(self.screen, mode_color,
                           (badge_rect.x + 12, badge_rect.centery), 4)
        self.screen.blit(badge_text,
                         (badge_rect.x + 20,
                          badge_rect.centery - badge_text.get_height() // 2))

        
        self._draw_separator(104)
        self._draw_section_label("MODES", 108)

     
        stats_sep_y   = 274
        stats_label_y = 278
        stats_start_y = 296

        self._draw_separator(stats_sep_y)
        self._draw_section_label("STATS", stats_label_y)

        stat_lines = [
            ("Nodes", str(len(self.graph.vertices))),
            ("Edges", str(len(self.graph.edges))),
        ]
        if App.getAppMode() == "animate" and self.render.orderList:
            done  = min(self.render.animationIndex, len(self.render.orderList))
            total = len(self.render.orderList)
            stat_lines.append((f"{self._anim_mode} step", f"{done} / {total}"))
            stat_lines.append(("Speed", f"{self._anim_speed}ms"))

        sy = stats_start_y
        for label, value in stat_lines:
            lsurf = self.font_stat.render(label + ":", True, Colors.TEXT_MUTED)
            vsurf = self.font_stat.render(value,        True, Colors.TEXT_PRIMARY)
            self.screen.blit(lsurf, (16, sy))
            self.screen.blit(vsurf, (self.PANEL_WIDTH - vsurf.get_width() - 16, sy))
            sy += 24

       
        if App.getAppMode() == "animate":
            anim_sep_y   = sy + 8          
            anim_label_y = anim_sep_y + 4
            anim_ctrl_y  = anim_label_y + 18   

            self._draw_separator(anim_sep_y)
            self._draw_section_label("ANIMATION SPEED / ALGO", anim_label_y)

            
            px = 16
            sw = 38
            xs = [px, px + sw + 4, px + sw*2 + 12, px + sw*2 + 76]
            for ctrl, x in zip(self.anim_controls, xs):
                ctrl.rect.y = anim_ctrl_y

       
        status_sep_y = screen_h - 100
        status_y     = status_sep_y + 6

        self._draw_separator(status_sep_y)
        msg = self._status_override or self.STATUS_HINTS.get(App.getAppMode(), "")
        status_surf = self.font_status.render(msg, True, Colors.TEXT_STATUS)
        self.screen.blit(status_surf, (16, status_y))

       
        self._draw_separator(screen_h - 58)

    def _draw_canvas_grid(self):
        """Faint dot grid drawn only on the canvas area."""
        gap = 40
        screen_w, screen_h = self.screen.get_size()
        for gx in range(self.PANEL_WIDTH + gap, screen_w, gap):
            for gy in range(gap, screen_h, gap):
                pygame.draw.circle(self.screen, Colors.DOT_GRID, (gx, gy), 1)

    def draw_buttons(self):
        for btn in self.mode_buttons:
            btn.draw(self.screen)
        if App.getAppMode() == "animate":
            for ctrl in self.anim_controls:
                ctrl.draw(self.screen)
        self.danger_button.draw(self.screen)

  

    @classmethod
    def setAppMode(cls, mode=None):
        cls.__mode = mode

    @classmethod
    def getAppMode(cls):
        return cls.__mode

  

    def run(self):
        while self.running:
            self.screen.fill(Colors.BG_CANVAS)
            self.handleUserInput()
            self._draw_canvas_grid()
            self.render.draw_graph()
            self.render.updateAnimation(self.clock)
            self.drawPanel()
            self.draw_buttons()
            pygame.display.flip()
            self.clock.tick(60)