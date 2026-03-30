import pygame
pygame.init()

board = [
    ["r","n","b","q","k","b","n","r"],
    ["p","p","p","p","p","p","p","p"],
    [".",".",".",".",".",".",".","."],
    [".",".",".",".",".",".",".","."],
    [".",".",".",".",".",".",".","."],
    [".",".",".",".",".",".",".","."],
    ["P","P","P","P","P","P","P","P"],
    ["R","N","B","Q","K","B","N","R"]
]

selected=None
turn="white"
valid=[]
game_over=False
stalemate=False
promotion_pending=None
font=pygame.font.SysFont("Segoe UI Symbol",48)

castling_rights={
    "white_king":True,"white_rook_left":True,"white_rook_right":True,
    "black_king":True,"black_rook_left":True,"black_rook_right":True
}

last_move=None

def valid_pawn_moves(r,c,b):
    moves=[]
    p=b[r][c]
    if p=="P":
        if r>0 and b[r-1][c]==".":
            moves.append((r-1,c))
            if r==6 and b[r-2][c]==".":
                moves.append((r-2,c))
        if r>0 and c>0 and b[r-1][c-1].islower():
            moves.append((r-1,c-1))
        if r>0 and c<7 and b[r-1][c+1].islower():
            moves.append((r-1,c+1))
        if last_move:
            (fr,fc),(tr,tc)=last_move
            if fr==1 and tr==3 and abs(tc-c)==1 and r==3:
                moves.append((2,tc))
    else:
        if r<7 and b[r+1][c]==".":
            moves.append((r+1,c))
            if r==1 and b[r+2][c]==".":
                moves.append((r+2,c))
        if r<7 and c>0 and b[r+1][c-1].isupper():
            moves.append((r+1,c-1))
        if r<7 and c<7 and b[r+1][c+1].isupper():
            moves.append((r+1,c+1))
        if last_move:
            (fr,fc),(tr,tc)=last_move
            if fr==6 and tr==4 and abs(tc-c)==1 and r==4:
                moves.append((5,tc))
    return moves

def slide(r,c,b,dirs):
    moves=[]
    w=b[r][c].isupper()
    for dr,dc in dirs:
        nr,nc=r+dr,c+dc
        while 0<=nr<8 and 0<=nc<8:
            t=b[nr][nc]
            if t==".":
                moves.append((nr,nc))
            elif t.isupper()!=w:
                moves.append((nr,nc));break
            else: break
            nr+=dr;nc+=dc
    return moves

def valid_rook_moves(r,c,b): return slide(r,c,b,[(-1,0),(1,0),(0,-1),(0,1)])
def valid_bishop_moves(r,c,b): return slide(r,c,b,[(-1,-1),(1,1),(1,-1),(-1,1)])
def valid_queen_moves(r,c,b): return valid_rook_moves(r,c,b)+valid_bishop_moves(r,c,b)

def valid_knight_moves(r,c,b):
    moves=[];w=b[r][c].isupper()
    for dr,dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
        nr,nc=r+dr,c+dc
        if 0<=nr<8 and 0<=nc<8:
            t=b[nr][nc]
            if t=="." or t.isupper()!=w:
                moves.append((nr,nc))
    return moves

def valid_king_moves(r,c,b):
    moves=[];w=b[r][c].isupper()
    for dr,dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
        nr,nc=r+dr,c+dc
        if 0<=nr<8 and 0<=nc<8:
            t=b[nr][nc]
            if t=="." or t.isupper()!=w:
                moves.append((nr,nc))
    if w and castling_rights["white_king"]:
        if castling_rights["white_rook_right"] and b[7][5]=="." and b[7][6]==".":
            moves.append((7,6))
        if castling_rights["white_rook_left"] and b[7][1]=="." and b[7][2]=="." and b[7][3]==".":
            moves.append((7,2))
    if not w and castling_rights["black_king"]:
        if castling_rights["black_rook_right"] and b[0][5]=="." and b[0][6]==".":
            moves.append((0,6))
        if castling_rights["black_rook_left"] and b[0][1]=="." and b[0][2]=="." and b[0][3]==".":
            moves.append((0,2))
    return moves

def get_attacks(r,c,b):
    p=b[r][c]
    if p in ("P","p"):
        d=-1 if p=="P" else 1
        return [(r+d,c-1),(r+d,c+1)]
    if p in ("R","r"): return valid_rook_moves(r,c,b)
    if p in ("N","n"): return valid_knight_moves(r,c,b)
    if p in ("B","b"): return valid_bishop_moves(r,c,b)
    if p in ("Q","q"): return valid_queen_moves(r,c,b)
    if p in ("K","k"):
        return [(r+dr,c+dc) for dr,dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)] if 0<=r+dr<8 and 0<=c+dc<8]
    return []

def is_attacked(r,c,by_white,b):
    for i in range(8):
        for j in range(8):
            if b[i][j]!="." and b[i][j].isupper()==by_white:
                if (r,c) in get_attacks(i,j,b):
                    return True
    return False

def find_king(b,w):
    k="K" if w else "k"
    for i in range(8):
        for j in range(8):
            if b[i][j]==k: return i,j

def in_check(b,w):
    r,c=find_king(b,w)
    return is_attacked(r,c,not w,b)

def leaves_check(fr,fc,tr,tc,b,w):
    t=[row[:] for row in b]
    piece=t[fr][fc]
    if piece in ("P","p") and fc!=tc and t[tr][tc]==".":
        t[fr][tc]="."
    t[tr][tc]=piece
    t[fr][fc]="."
    return in_check(t,w)

def valid_castle(fr,fc,tr,tc,b,w):
    if b[fr][fc] not in ("K","k") or abs(tc-fc)!=2: return True
    if in_check(b,w): return False
    d=1 if tc>fc else -1
    if is_attacked(fr,fc+d,not w,b): return False
    if is_attacked(tr,tc,not w,b): return False
    return True

def raw_moves(r,c,b):
    p=b[r][c]
    if p in ("P","p"): return valid_pawn_moves(r,c,b)
    if p in ("R","r"): return valid_rook_moves(r,c,b)
    if p in ("N","n"): return valid_knight_moves(r,c,b)
    if p in ("B","b"): return valid_bishop_moves(r,c,b)
    if p in ("Q","q"): return valid_queen_moves(r,c,b)
    if p in ("K","k"): return valid_king_moves(r,c,b)
    return []

def moves(r,c,b):
    w=b[r][c].isupper()
    return [(tr,tc) for tr,tc in raw_moves(r,c,b) if not leaves_check(r,c,tr,tc,b,w) and valid_castle(r,c,tr,tc,b,w)]

def checkmate(b,w):
    if not in_check(b,w): return False
    for i in range(8):
        for j in range(8):
            if b[i][j]!="." and b[i][j].isupper()==w:
                if moves(i,j,b): return False
    return True

def stalemate_fn(b,w):
    if in_check(b,w): return False
    for i in range(8):
        for j in range(8):
            if b[i][j]!="." and b[i][j].isupper()==w:
                if moves(i,j,b): return False
    return True

def update_rights(fr,fc,p):
    if p=="K": castling_rights["white_king"]=False
    elif p=="k": castling_rights["black_king"]=False
    elif p=="R":
        if (fr,fc)==(7,0): castling_rights["white_rook_left"]=False
        if (fr,fc)==(7,7): castling_rights["white_rook_right"]=False
    elif p=="r":
        if (fr,fc)==(0,0): castling_rights["black_rook_left"]=False
        if (fr,fc)==(0,7): castling_rights["black_rook_right"]=False

def capture_rights(r,c):
    if (r,c)==(7,0): castling_rights["white_rook_left"]=False
    if (r,c)==(7,7): castling_rights["white_rook_right"]=False
    if (r,c)==(0,0): castling_rights["black_rook_left"]=False
    if (r,c)==(0,7): castling_rights["black_rook_right"]=False

def castle_move(fr,fc,tr,tc,b):
    if b[tr][tc]=="K" and fc==4 and tc==6:
        b[7][5]="R"; b[7][7]="."
    elif b[tr][tc]=="K" and fc==4 and tc==2:
        b[7][3]="R"; b[7][0]="."
    elif b[tr][tc]=="k" and fc==4 and tc==6:
        b[0][5]="r"; b[0][7]="."
    elif b[tr][tc]=="k" and fc==4 and tc==2:
        b[0][3]="r"; b[0][0]="."

WIDTH=480;S=WIDTH//8
screen=pygame.display.set_mode((WIDTH,WIDTH))
WHITE=(240,240,240);BLACK=(100,100,100)

piece_map={
"P":"♙","R":"♖","N":"♘","B":"♗","Q":"♕","K":"♔",
"p":"♟","r":"♜","n":"♞","b":"♝","q":"♛","k":"♚"
}

def draw(valid_moves=[],chk=None):
    for r in range(8):
        for c in range(8):
            col=WHITE if (r+c)%2==0 else BLACK
            pygame.draw.rect(screen,col,(c*S,r*S,S,S))
            if chk==(r,c): pygame.draw.rect(screen,(255,0,0),(c*S,r*S,S,S))
            if selected==(r,c): pygame.draw.rect(screen,(0,255,255),(c*S,r*S,S,S),3)
            if (r,c) in valid_moves:
                pygame.draw.circle(screen,(0,200,0),(c*S+S//2,r*S+S//2),10)
            p=board[r][c]
            if p!=".":
                t=font.render(piece_map[p],True,(0,0,0))
                screen.blit(t,t.get_rect(center=(c*S+S//2,r*S+S//2)))

def promo_draw(w):
    pieces=["Q","R","B","N"] if w else ["q","r","b","n"]
    x=(WIDTH-4*S)//2; y=WIDTH//2-S//2
    for i,p in enumerate(pieces):
        rect=pygame.Rect(x+i*S,y,S,S)
        pygame.draw.rect(screen,(255,255,200),rect)
        pygame.draw.rect(screen,(0,0,0),rect,2)
        t=font.render(piece_map[p],True,(0,0,0))
        screen.blit(t,t.get_rect(center=rect.center))

def promo_pick(pos,w):
    pieces=["Q","R","B","N"] if w else ["q","r","b","n"]
    x=(WIDTH-4*S)//2; y=WIDTH//2-S//2
    px,py=pos
    if y<=py<=y+S:
        idx=(px-x)//S
        if 0<=idx<4: return pieces[idx]

def sq(pos):
    x,y=pos
    return y//S,x//S

running=True
while running:
    screen.fill((0,0,0))
    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False
        if e.type==pygame.MOUSEBUTTONDOWN and not game_over and not stalemate:
            if promotion_pending:
                w=promotion_pending[0]==0
                choice=promo_pick(pygame.mouse.get_pos(),w)
                if choice:
                    r,c=promotion_pending
                    board[r][c]=choice
                    promotion_pending=None
                    turn="black" if turn=="white" else "white"
            else:
                r,c=sq(pygame.mouse.get_pos())
                if selected is None:
                    if board[r][c]!="." and ((turn=="white" and board[r][c].isupper()) or (turn=="black" and board[r][c].islower())):
                        selected=(r,c); valid=moves(r,c,board)
                else:
                    if (r,c) in valid:
                        sr,sc=selected
                        p=board[sr][sc]
                        capture_rights(r,c)
                        if p in ("P","p") and c!=sc and board[r][c]==".":
                            board[sr][c]="."
                        board[r][c]=p; board[sr][sc]="."
                        castle_move(sr,sc,r,c,board)
                        update_rights(sr,sc,p)
                        last_move=((sr,sc),(r,c))
                        if (p=="P" and r==0) or (p=="p" and r==7):
                            promotion_pending=(r,c)
                        else:
                            turn="black" if turn=="white" else "white"
                    selected=None; valid=[]

    chk=None
    if not promotion_pending:
        if in_check(board,turn=="white"):
            chk=find_king(board,turn=="white")

    draw(valid,chk)

    if promotion_pending:
        promo_draw(promotion_pending[0]==0)

    if not promotion_pending:
        if checkmate(board,turn=="white"):
            game_over=True
        elif stalemate_fn(board,turn=="white"):
            stalemate=True

    pygame.display.update()

pygame.quit()