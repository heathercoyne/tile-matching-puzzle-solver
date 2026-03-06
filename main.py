import sys, random, heapq
from collections import deque 
import pygame


# Sizes and arrangement of overall window and components in the window
MIN_N, MAX_N = 4, 8 
TILE_SIZE = 64 
MARGIN = 20 
HUD_H = 140 # top area
SIDE_W = 720 # side info panel
WIN_MIN_W = 1740 
WIN_MIN_H = 1040

# Colors for different components
BG   = (22, 24, 32) 
GRID = (70, 75, 90)
TXT  = (235, 240, 246)
BTN_BG   = (54, 60, 76)
BTN_BG_H = (76, 86, 110)
BTN_TXT  = (255, 255, 255)
PANEL_BG = (35, 38, 46)
EMPTY = 0

#Keeping track of directions and their arrows
DIRS = [(1,0,"→"),(-1,0,"←"),(0,1,"↓"),(0,-1,"↑")]


# Set each pair of tile to a unique color
def palette_color(i, total=100):
    c = pygame.Color(0)
    c.hsva = ((i * 360 / max(1,total)) % 360, 65, 95, 100)
    return (c.r, c.g, c.b)

# For creating copies of board after each move to keep track
def clone(board):
    return [r[:] for r in board]

# Boards become tuples so it is more efficient to compare them 
def board_key(board):
    return tuple(tuple(r) for r in board)

# finds the position of a colored tile (tid) and returns coordinate
def find_positions(board, tid):
    ps=[]
    for y,row in enumerate(board):
        for x,v in enumerate(row):
            if v==tid: ps.append((x,y))
    return ps

#check if there is obstruction between two coordinates either vertically or horizontally
def line_clear(board, a, b):
    (x1,y1),(x2,y2)=a,b 
    if x1==x2: #check vertically
        ylo,yhi=sorted([y1,y2])
        for yy in range(ylo+1,yhi):
            if board[yy][x1]!=0: return False
        return True
    if y1==y2: # check horizontally
        xlo,xhi=sorted([x1,x2])
        for xx in range(xlo+1,xhi):
            if board[y1][xx]!=0: return False
        return True
    return False

# create a board with randomly located pairs 
def generate_board_random(n, pairs):
    ids=[]
    for t in range(1,pairs+1): ids += [t,t]
    random.shuffle(ids)
    cells=[(x,y) for y in range(n) for x in range(n)]
    random.shuffle(cells)
    board=[[0]*n for _ in range(n)]
    for (x,y),tid in zip(cells,ids):
        board[y][x]=tid
    return board

# find all valid moves from a board
def sliding_neighbors(board, pos):
    n=len(board)
    x0,y0=pos
    for dx,dy,sym in DIRS:
        x,y=x0,y0
        while True:
            nx,ny=x+dx,y+dy
            if not(0<=nx<n and 0<=ny<n): break
            if board[ny][nx]!=0: break
            x,y=nx,ny
            yield (x,y),(sym,(x0,y0),(x,y))

#BFS over slides of the movable tile. 
# Returns either none or a list of slides that leads to elimination 
def local_bfs_move_one(board, tid, p_movable, p_fixed):
    
    q=deque([p_movable]) # the BFS queue
    parent={p_movable:None}
    step_taken={p_movable:None}
    seen={p_movable} # keeping track of visited positions

    while q:
        cur=q.popleft()
        # check if the pairs are in the same row or column after checking there is no obstruction
        if line_clear(board, cur, p_fixed):
            path=[]
            p=cur
            while p is not None:
                st=step_taken[p]
                if st is not None: path.append(st)
                p=parent[p]
            path.reverse()
            return path

        for nxt,(sym,frm,to) in sliding_neighbors(board, cur):
            if nxt in seen: 
                continue
            seen.add(nxt)
            parent[nxt]=cur
            step_taken[nxt]=(sym,frm,to)
            if line_clear(board, nxt, p_fixed):
                path=[]
                p=nxt
                while p is not None:
                    st=step_taken[p]
                    if st is not None: path.append(st)
                    p=parent[p]
                path.reverse()
                return path
            q.append(nxt)
    return None


# For each pair check which tile is better to move
def best_local_for_color(board, tid):
    pos=find_positions(board, tid)
    if len(pos)!=2: return (None,None,None)
    p1,p2=pos[0],pos[1]
    slides1=local_bfs_move_one(board, tid, p1, p2)
    slides2=local_bfs_move_one(board, tid, p2, p1)
    if slides1 is None and slides2 is None: return (None,None,None)
    if slides2 is None or (slides1 is not None and len(slides1)<=len(slides2)):
        return (slides1, p1, p2)
    else:
        return (slides2, p2, p1)


# Slides the chosen tile
# Eliminates pairs in they are in the same column and row with no obstructions
def apply_sliding_path(board, tid, slides, moved_from, fixed_other):

    nb=clone(board) # use a copy to keep original state
    cx,cy=moved_from
    for (sym,frm,to) in slides:
        fx,fy=frm; tx,ty=to
        nb[fy][fx]=0
        nb[ty][tx]=tid
        cx,cy=tx,ty
    if line_clear(nb, (cx,cy), fixed_other):
        nb[cy][cx]=0
        ox,oy=fixed_other
        nb[oy][ox]=0
    return nb

# the main solver (uses Uniform-cost search)
# finds the lowest total weigheted cost to fully clear the board
def ucs_global(board, pairs, weights):
    
    remaining=frozenset(range(1,pairs+1))
    start_key=(board_key(board), remaining)
    pq=[(0,0,start_key)]  # (cost, slides_so_far, key)
    parent={start_key:None}
    action={start_key:None}
    state_obj={start_key:(clone(board), remaining)}
    best_cost={start_key:0}
    best_slides={start_key:0}

    while pq:
        cost, slides_so_far, key = heapq.heappop(pq)
        if best_cost.get(key,1e18) < cost: # check that this current one is the cheapest, otherwise skip
            continue
        cur_board, cur_rem = state_obj[key]

        # if goal reached
        if not cur_rem:
            seq=[]
            k=key
            while k is not None:
                a=action[k]
                if a is not None: seq.append(a)
                k=parent[k]
            seq.reverse()
            return cost, slides_so_far, seq, clone(cur_board)

        # go through remaining colors and find the best path 
        for tid in sorted(cur_rem):
            slides, moved_from, fixed_other = best_local_for_color(cur_board, tid)
            if slides is None:
                continue
            nb = apply_sliding_path(cur_board, tid, slides, moved_from, fixed_other)
            nrem = frozenset(x for x in cur_rem if x!=tid)
            nkey = (board_key(nb), nrem)

            slid_ct = len(slides)
            step_cost = slid_ct * weights.get(tid,1)
            ncost  = cost + step_cost
            nslides= slides_so_far + slid_ct

            if (nkey not in best_cost) or (ncost < best_cost[nkey]) or (ncost==best_cost[nkey] and nslides<best_slides[nkey]):
                best_cost[nkey]=ncost
                best_slides[nkey]=nslides
                parent[nkey]=key
                action[nkey]={
                    'tid': tid,
                    'positions': find_positions(cur_board, tid),
                    'slides': slides,
                    'moved_from': moved_from,
                    'fixed_other': fixed_other,
                    'slide_count': slid_ct,
                    'cost': step_cost
                }
                state_obj[nkey]=(nb, nrem)
                heapq.heappush(pq,(ncost,nslides,nkey))
    return None  # unsolvable

# Make a minature board with an arrow showing each move 
def render_miniature(board_for_step, n, tid, slides, pairs, tile_size=18, margin=6):
    w = margin*2 + n*tile_size
    h = margin*2 + n*tile_size
    surf = pygame.Surface((w,h))
    surf.fill((32,35,42))

    # Mini grid + tiles
    for y in range(n):
        for x in range(n):
            pygame.draw.rect(surf, GRID, pygame.Rect(margin+x*tile_size, margin+y*tile_size, tile_size, tile_size), 1)
            t = board_for_step[y][x]
            if t != 0:
                color = palette_color(t, pairs)
                pygame.draw.rect(surf, color,
                                 pygame.Rect(margin+x*tile_size, margin+y*tile_size, tile_size, tile_size).inflate(-4,-4),
                                 border_radius=5)

 
    pts=[]
    # Show move and add lines for each slide in the best path found above.
    if slides:
        pts.append(slides[0][1])  
        for (_sym, frm, to) in slides:
            pts.append(to)
    if len(pts)>=2:
        scaled=[]
        for (x,y) in pts:
            cx = margin + x*tile_size + tile_size//2
            cy = margin + y*tile_size + tile_size//2
            scaled.append((cx,cy))
        pygame.draw.lines(surf, palette_color(tid, pairs), False, scaled, 3)

    return surf

# Buttons and Text for the UI
class Button:
    def __init__(self, rect, text, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.txt  = font.render(text, True, BTN_TXT)
        self.hover=False
    def draw(self,screen):
        pygame.draw.rect(screen, BTN_BG_H if self.hover else BTN_BG, self.rect, border_radius=8)
        screen.blit(self.txt, self.txt.get_rect(center=self.rect.center))
    def handle(self,e):
        if e.type==pygame.MOUSEMOTION: self.hover=self.rect.collidepoint(e.pos)
        if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
            if self.rect.collidepoint(e.pos): return True
        return False

def popup_text(screen, font, message):
    w,h=screen.get_size()
    overlay=pygame.Surface((w,h),pygame.SRCALPHA)
    overlay.fill((0,0,0,140))
    box=pygame.Rect(0,0,700,200); box.center=(w//2, h//2)
    ok=Button(pygame.Rect(box.centerx-50, box.bottom-60, 100, 44), "OK", font)
    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit(0)
            if ok.handle(e): return
        screen.blit(overlay,(0,0))
        pygame.draw.rect(screen, BTN_BG, box, border_radius=10)
        pygame.draw.rect(screen, GRID, box, width=2, border_radius=10)
        t1=font.render(message, True, BTN_TXT)
        screen.blit(t1, t1.get_rect(center=(box.centerx, box.centery-18)))
        ok.draw(screen); pygame.display.flip()

def input_integer(screen, font, prompt, lo, hi):
    text=""; clock=pygame.time.Clock()
    while True:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit(0)
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_RETURN and text.isdigit():
                    v=int(text)
                    if lo<=v<=hi: return v
                elif e.key==pygame.K_BACKSPACE:
                    text=text[:-1]
                else:
                    if e.unicode.isdigit(): text+=e.unicode
        screen.fill(BG)
        title=font.render("Input", True, TXT); screen.blit(title,(40,30))
        msg=font.render(f"{prompt} [{lo}-{hi}]: {text}", True, TXT); screen.blit(msg,(40,70))
        tip=font.render("Enter to confirm, Backspace to edit, close window to quit", True, TXT)
        screen.blit(tip,(40,110)); pygame.display.flip()

def input_yesno(screen, font, prompt):
    clock=pygame.time.Clock()
    while True:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit(0)
            if e.type==pygame.KEYDOWN and e.unicode.lower() in ('y','n'):
                return e.unicode.lower()=='y'
        screen.fill(BG)
        screen.blit(font.render("Input", True, TXT),(40,30))
        screen.blit(font.render(f"{prompt} [Y/N]", True, TXT),(40,70))
        pygame.display.flip()

# Making the information panel on the right sile scrollable
class ScrollPanel:
    def __init__(self, rect, font):
        self.rect=pygame.Rect(rect)
        self.font=font
        self.items=[]
        self.offset=0
        self.scroll_speed=24
    def set_items(self, items):
        self.items=items; self.offset=0
    def handle(self,e):
        if e.type==pygame.MOUSEWHEEL:
            self.offset -= e.y*self.scroll_speed
            maxoff=max(0, self.content_height()-self.rect.height)
            self.offset=max(0, min(self.offset, maxoff))
    def content_height(self):
        h=0
        for it in self.items:
            if it["type"]=="text": h+=22
            else: h+=it["surf"].get_height()+it.get("pad",8)
        return h
    def draw(self,screen):
        surf=pygame.Surface(self.rect.size)
        surf.fill(PANEL_BG)
        y=-self.offset
        for it in self.items:
            if it["type"]=="text":
                if -22<=y<=self.rect.height:
                    surf.blit(self.font.render(it["text"], True, it["color"]),(8,y))
                y+=22
            else:
                img=it["surf"]; ih=img.get_height()
                if -ih<=y<=self.rect.height:
                    surf.blit(img,(8,y))
                y+=ih+it.get("pad",8)
        pygame.draw.rect(screen, GRID, self.rect, 1)
        screen.blit(surf, self.rect.topleft)

 # main function
def main():
    pygame.init()
    font = pygame.font.SysFont("consolas", 20)
    big  = pygame.font.SysFont("consolas", 26)

    # Window
    screen = pygame.display.set_mode((WIN_MIN_W, WIN_MIN_H))
    pygame.display.set_caption("Brick Solver — Sliding BFS + UCS (No Start/Goal)")

    # Inputs from user
    n     = input_integer(screen, font, "Board size (side length)", MIN_N, MAX_N)
    pairs = input_integer(screen, font, "Number of pairs", 1, (n*n)//2)

    # Layout based on board size
    board_px_w = n*TILE_SIZE
    board_px_h = n*TILE_SIZE
    left_area_w = max(MARGIN*2 + board_px_w, WIN_MIN_W - SIDE_W - MARGIN)
    left_area_h = max(MARGIN*2 + board_px_h, WIN_MIN_H - HUD_H - MARGIN)
    W = max(WIN_MIN_W, left_area_w + SIDE_W + MARGIN)
    H = max(WIN_MIN_H, HUD_H + left_area_h)
    screen = pygame.display.set_mode((W, H))

    def compute_board_origin():
        left_w = W - SIDE_W - MARGIN*2
        left_h = H - HUD_H - MARGIN*2
        ox = MARGIN + (left_w - board_px_w)//2
        oy = HUD_H + MARGIN + (left_h - board_px_h)//2
        return ox, oy

    def rect_cell(x, y):
        ox, oy = compute_board_origin()
        return pygame.Rect(ox + x*TILE_SIZE, oy + y*TILE_SIZE, TILE_SIZE, TILE_SIZE)

    # Generate random board
    board = generate_board_random(n, pairs)
    board_init = clone(board)

    # Random weight
    weights = {tid: random.randint(1,5) for tid in range(1, pairs+1)}

    # UI
    btn_solve   = Button(pygame.Rect(MARGIN, 20, 320, 44), "Solve", font)
    btn_restart = Button(pygame.Rect(MARGIN+340, 20, 160, 44), "Restart", font)
    btn_quit    = Button(pygame.Rect(MARGIN+510, 20, 120, 44), "Quit", font)
    panel       = ScrollPanel(pygame.Rect(W-SIDE_W+8, MARGIN, SIDE_W-16, H-2*MARGIN), font)

    info="Ready."
    clock=pygame.time.Clock()
    running=True

    while running:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
            if btn_quit.handle(e): running=False
            panel.handle(e)

            if btn_restart.handle(e):
                # Rerun again
                n     = input_integer(screen, font, "Board size (side length)", MIN_N, MAX_N)
                pairs = input_integer(screen, font, "Number of pairs", 1, (n*n)//2)

                # Recompute layout
                board_px_w = n*TILE_SIZE
                board_px_h = n*TILE_SIZE
                left_area_w = max(MARGIN*2 + board_px_w, WIN_MIN_W - SIDE_W - MARGIN)
                left_area_h = max(MARGIN*2 + board_px_h, WIN_MIN_H - HUD_H - MARGIN)
                W = max(WIN_MIN_W, left_area_w + SIDE_W + MARGIN)
                H = max(WIN_MIN_H, HUD_H + left_area_h)
                screen = pygame.display.set_mode((W, H))
                panel  = ScrollPanel(pygame.Rect(W-SIDE_W+8, MARGIN, SIDE_W-16, H-2*MARGIN), font)

                # New board + weights
                board = generate_board_random(n, pairs)
                board_init = clone(board)
                weights = {tid: random.randint(1,5) for tid in range(1, pairs+1)}

                # Recreate buttons (positions stay same)
                btn_solve   = Button(pygame.Rect(MARGIN, 20, 320, 44), "Solve", font)
                btn_restart = Button(pygame.Rect(MARGIN+340, 20, 160, 44), "Restart", font)
                btn_quit    = Button(pygame.Rect(MARGIN+510, 20, 120, 44), "Quit", font)
                info="Ready"

            if btn_solve.handle(e):
                info="Solving ..."
                pygame.display.flip()

                result = ucs_global(board, pairs, weights)
                if result is None:
                    popup_text(screen, font, "Unsolvable")
                    info="No solution"
                    panel.set_items([])
                else:
                    total_cost, total_slides, order_moves, final_board = result
                    board = final_board
                    info=f"Solved. Total weighted cost={total_cost}  Total slides={total_slides}"

                    # Build side panel content
                    items=[]
                    items.append({"type":"text","text":" Full Solution ","color":(220,220,235)})
                    items.append({"type":"text","text":f"Total cost: {total_cost}   Total slides: {total_slides}","color":(230,230,240)})
                    items.append({"type":"text","text":"Color weights (cost per slide):","color":(220,220,235)})

                    # compact weight listing
                    line=""
                    for tid in range(1, pairs+1):
                        part=f"{tid}:{weights[tid]}"
                        if len(line)+len(part)+2>46:
                            items.append({"type":"text","text":"   "+line,"color":(205,205,220)})
                            line=part
                        else:
                            line = part if not line else f"{line}, {part}"
                    if line:
                        items.append({"type":"text","text":"   "+line,"color":(205,205,220)})
                    items.append({"type":"text","text":"", "color":TXT})

                    # minature boards for the information panel
                    board_for_mini = clone(board_init)
                    for idx, entry in enumerate(order_moves, start=1):
                        tid = entry['tid']
                        slides = entry['slides']
                        step_cost = entry['cost']
                        color = palette_color(tid, pairs)

                        items.append({"type":"text","text":f"{idx}. Color {tid} (w={weights[tid]})  slides={len(slides)}  cost={step_cost}","color":color})
                        for (sym,frm,to) in slides:
                            items.append({"type":"text","text":f"   {sym}: {frm} -> {to}","color":color})

                        mini = render_miniature(board_for_mini, n, tid, slides, pairs, tile_size=18, margin=6)
                        items.append({"type":"surf","surf":mini,"pad":12})
                        items.append({"type":"text","text":"", "color":TXT})

                        # advance mini state
                        board_for_mini = apply_sliding_path(board_for_mini, tid, slides, entry['moved_from'], entry['fixed_other'])

                    panel.set_items(items)

        # DRAW
        screen.fill(BG)
        pygame.draw.rect(screen, (30,33,42), (0,0,W,HUD_H))
        btn_solve.draw(screen); btn_restart.draw(screen); btn_quit.draw(screen)
        screen.blit(big.render(info, True, TXT), (MARGIN+640, 26))

        # centered main board
        for y in range(n):
            for x in range(n):
                r = rect_cell(x,y)
                pygame.draw.rect(screen, GRID, r, 1)
                t = board[y][x]
                if t != 0:
                    pygame.draw.rect(screen, palette_color(t, pairs), r.inflate(-8,-8), border_radius=10)

        panel.draw(screen)
        pygame.display.flip()

    pygame.quit(); sys.exit(0)

if __name__=="__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e)
        pygame.quit(); sys.exit(1)
