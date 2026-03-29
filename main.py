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


selected = None
font = pygame.font.SysFont("Segoe UI Symbol", 48)


WIDTH, HEIGHT = 480, 480
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
screen = pygame.display.set_mode((WIDTH, HEIGHT))

WHITE = (240, 240, 240)
BLACK = (100, 100, 100)

piece_map = {
    "P": "♙", "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔",
    "p": "♟", "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚"
}

def draw_board():
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if(row + col) % 2 == 0 else BLACK
            pygame.draw.rect(
                screen, 
                color, 
                (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            )

            piece = board[row][col]
            if selected == (row, col):
                pygame.draw.rect(
                    screen, 
                    (0, 255, 255),
                    (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                    3
                )
            if piece != ".":
                symbol = piece_map[piece]
                text = font.render(symbol, True, (0, 0, 0))
                text_rect = text.get_rect(center = (
                    col * SQUARE_SIZE + SQUARE_SIZE // 2,
                    row * SQUARE_SIZE + SQUARE_SIZE // 2
                ))
                screen.blit(text, text_rect)

pygame.display.set_caption("Chess")

def get_square(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

running = True
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            row, col = get_square(pygame.mouse.get_pos())
        
            if selected is None:
                if board[row][col] != ".":
                    selected = (row, col)
                    print("Selected: ", selected)
            else:
                sr, sc = selected

                board[row][col] = board[sr][sc]
                board[sr][sc] = "."

                print("Moved: ", (sr, sc), "->", (row, col))
                selected = None
    draw_board()
    pygame.display.update()

pygame.quit()