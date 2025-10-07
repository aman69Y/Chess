Python 3.11.9 (tags/v3.11.9:de54cf5, Apr  2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
import pygame
import chess
import chess.engine
import sys
import os

# ----------------- Pygame Initialization -----------------
pygame.init()
WIDTH, HEIGHT = 640, 640
SQUARE_SIZE = WIDTH // 8
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Professional Python Chess")
CLOCK = pygame.time.Clock()
FPS = 60

# ----------------- Colors -----------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 68)

# ----------------- Load Piece Images -----------------
IMAGES = {}
PIECE_TYPES = ["P", "N", "B", "R", "Q", "K"]
for piece in ["w"+p for p in PIECE_TYPES] + ["b"+p for p in PIECE_TYPES]:
    IMAGES[piece] = pygame.transform.scale(
        pygame.image.load(os.path.join("assets", piece + ".png")),
        (SQUARE_SIZE, SQUARE_SIZE)
    )

# ----------------- Chess Variables -----------------
board = chess.Board()
selected_square = None
dragging_piece = None
dragging_offset = (0,0)
move_log = []
redo_stack = []

# AI Settings
ai_enabled = True
player_color = chess.WHITE
STOCKFISH_PATH = "stockfish_15_win_x64_avx2.exe"  # Change to your path
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
AI_TIME = 0.1  # Adjust for difficulty

# Two-player toggle
two_player_mode = False

# ----------------- Functions -----------------
def draw_board():
    for r in range(8):
        for c in range(8):
            color = LIGHT_BROWN if (r+c) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(SCREEN, color, pygame.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def highlight_squares():
    if selected_square is not None:
        r = 7 - chess.square_rank(selected_square)
        c = chess.square_file(selected_square)
        pygame.draw.rect(SCREEN, HIGHLIGHT_COLOR, pygame.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        for move in board.legal_moves:
            if move.from_square == selected_square:
                r2 = 7 - chess.square_rank(move.to_square)
                c2 = chess.square_file(move.to_square)
                pygame.draw.circle(SCREEN, (0,0,255), (c2*SQUARE_SIZE+SQUARE_SIZE//2, r2*SQUARE_SIZE+SQUARE_SIZE//2), 10)

def draw_pieces():
    for r in range(8):
        for c in range(8):
            sq = chess.square(c, 7-r)
            piece = board.piece_at(sq)
            if piece:
                key = ('w' if piece.color == chess.WHITE else 'b') + piece.symbol().upper()
                if dragging_piece and dragging_piece[1] == sq:
                    continue  # skip drawing dragged piece
                SCREEN.blit(IMAGES[key], (c*SQUARE_SIZE, r*SQUARE_SIZE))
    # Draw dragged piece on top
    if dragging_piece:
        key = ('w' if dragging_piece[0].color == chess.WHITE else 'b') + dragging_piece[0].symbol().upper()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        SCREEN.blit(IMAGES[key], (mouse_x + dragging_offset[0], mouse_y + dragging_offset[1]))

def get_square_under_mouse():
    mouse_pos = pygame.mouse.get_pos()
    col = mouse_pos[0] // SQUARE_SIZE
    row = mouse_pos[1] // SQUARE_SIZE
    return chess.square(col, 7-row)

def ai_move():
    result = engine.play(board, chess.engine.Limit(time=AI_TIME))
    board.push(result.move)
    move_log.append(result.move)
    redo_stack.clear()

def undo_move():
    if board.move_stack:
        move = board.pop()
        move_log.pop()
        redo_stack.append(move)

def redo_move():
    if redo_stack:
        move = redo_stack.pop()
        board.push(move)
        move_log.append(move)

# ----------------- Main Loop -----------------
def main():
    global selected_square, dragging_piece, dragging_offset, two_player_mode

    running = True
    while running:
        CLOCK.tick(FPS)
        draw_board()
        highlight_squares()
        draw_pieces()
        pygame.display.flip()

        # AI Move
        if ai_enabled and not two_player_mode and board.turn != player_color:
            ai_move()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.quit()
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    undo_move()
                elif event.key == pygame.K_r:
                    redo_move()
                elif event.key == pygame.K_t:
                    two_player_mode = not two_player_mode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                square = get_square_under_mouse()
                piece = board.piece_at(square)
...                 if piece and piece.color == board.turn:
...                     selected_square = square
...                     dragging_piece = (piece, square)
...                     mouse_x, mouse_y = pygame.mouse.get_pos()
...                     r = 7 - chess.square_rank(square)
...                     c = chess.square_file(square)
...                     dragging_offset = (c*SQUARE_SIZE - mouse_x, r*SQUARE_SIZE - mouse_y)
... 
...             elif event.type == pygame.MOUSEBUTTONUP:
...                 if dragging_piece:
...                     target_square = get_square_under_mouse()
...                     move = chess.Move(dragging_piece[1], target_square)
...                     if move in board.legal_moves:
...                         board.push(move)
...                         move_log.append(move)
...                         redo_stack.clear()
...                     dragging_piece = None
...                     selected_square = None
... 
... if __name__ == "__main__":
...     main()
