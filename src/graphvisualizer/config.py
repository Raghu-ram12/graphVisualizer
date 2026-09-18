class Colors:

    # ── Base palette ──────────────────────────────────────────────────────────
    WHITE   = (255, 255, 255)
    BLACK   = (  0,   0,   0)
    GRAY    = (128, 128, 128)

    RED     = (255,  59,  48)
    GREEN   = ( 52, 199,  89)
    BLUE    = (  0, 122, 255)
    YELLOW  = (255, 204,   0)
    PURPLE  = (175,  82, 222)
    ORANGE  = (255, 149,   0)

    PASTEL_BLUE   = (173, 216, 230)
    PASTEL_GREEN  = (144, 238, 144)
    PASTEL_PINK   = (255, 182, 193)
    PASTEL_YELLOW = (255, 255, 224)

    # ── Backgrounds ───────────────────────────────────────────────────────────
    BG_DARK       = ( 18,  18,  18)   # window fallback
    BG_CANVAS     = ( 12,  12,  18)   # main canvas (replaces pure black)
    BG_PANEL      = ( 30,  30,  30)   # sidebar base
    BG_SIDEBAR    = ( 35,  35,  40)   # sidebar title block (slightly lifted)
    DOT_GRID      = ( 25,  25,  35)   # optional canvas dot grid

    # ── Surfaces (buttons, cards) ─────────────────────────────────────────────
    SURFACE_LIGHT  = ( 45,  45,  45)  # general light surface
    SURFACE_HOVER  = ( 45,  45,  50)  # button hover — subtle, not jarring
    SURFACE_ACTIVE = ( 55,  55,  62)  # active/pressed button background
    SEPARATOR      = ( 50,  50,  55)  # horizontal divider lines
    SHORTCUT_BADGE = ( 60,  60,  70)  # keyboard shortcut pill background

    # ── Node states ───────────────────────────────────────────────────────────
    NODE_DEFAULT  = (  0,  90, 210)   # idle node fill
    NODE_HOVERED  = ( 30, 120, 240)   # cursor over node
    NODE_SELECTED = (255,  64, 129)   # first node picked in edge mode (pink)
    NODE_VISITED  = (106,  90, 205)   # already traversed by BFS/DFS
    NODE_CURRENT  = (255, 204,   0)   # current step in animation (yellow)

    # ── Edge states ───────────────────────────────────────────────────────────
    EDGE_DEFAULT  = ( 80,  80, 100)   # idle edge (muted; not competing with nodes)
    EDGE_VISITED  = (106,  90, 205)   # edge on traversal path (matches NODE_VISITED)
    EDGE_ACTIVE   = (255, 149,   0)   # edge being drawn / highlighted (orange)

    # ── Mode accent strips (left border on buttons) ───────────────────────────
    ACCENT_VERTEX  = (  0, 122, 255)  # vertex mode — blue
    ACCENT_EDGE    = (255, 149,   0)  # edge mode   — orange
    ACCENT_ANIMATE = ( 52, 199,  89)  # animate mode — green

    # ── Text ──────────────────────────────────────────────────────────────────
    TEXT_PRIMARY   = (230, 230, 230)  # main panel labels
    TEXT_MUTED     = (100, 100, 110)  # section headers (MODES / STATS)
    TEXT_STATUS    = (255, 200,   0)  # status bar hints (amber)
    TEXT_NODE      = (255, 255, 255)  # label inside a node (white on blue)

    # ── Danger (Clear Graph button) ───────────────────────────────────────────
    DANGER        = (100,  20,  20)   # button base
    DANGER_BORDER = (200,  50,  50)   # button border / outline
    DANGER_HOVER  = (180,  40,  40)   # button hovered

    # ── Legacy aliases (kept for backward compatibility) ──────────────────────
    HOVERED  = (  0, 255, 255)        # old cyan hover (still used in renderer)
    SELECTED = (255,  64, 129)        # alias → same as NODE_SELECTED
    VISITED  = (106,  90, 205)        # alias → same as NODE_VISITED
