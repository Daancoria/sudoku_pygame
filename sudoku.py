import pygame
import random
import time
import itertools

pygame.init()

################################################################################
# Constants & Globals
################################################################################
# Default starting size
WIDTH, HEIGHT = 600, 750
GRID_SIZE = 9

# We'll compute CELL_SIZE dynamically in set_screen_size()
CELL_SIZE = 0

# Global game states / variables
puzzle = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
solution = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
selected_cell = None
mistakes = 0
start_time = 0
running = True

# Control flow flags
in_start_menu = True
in_instructions_menu = False
current_difficulty = "medium"

# Night mode global toggle
night_mode = False

# Pause menu state
paused = False
pause_start_time = 0.0  # Time when we entered pause, used to freeze the timer

# Fonts (we'll keep them static in size for simplicity)
pygame.font.init()
FONT = pygame.font.Font(pygame.font.match_font('arial'), 30)
TITLE_FONT = pygame.font.Font(pygame.font.match_font('arial'), 48)
SMALL_FONT = pygame.font.Font(pygame.font.match_font('arial'), 20)  # smaller to fit instructions better

# Create window (done in set_screen_size)
screen = None


################################################################################
# Color Management for Day & Night
################################################################################
def get_colors(night):
    """Return a dictionary of color values depending on whether night mode is on."""
    if night:
        return {
            # General backgrounds
            "main_bg": (45, 45, 45),
            "menu_bg": (70, 70, 70),
            # Lines, text, etc.
            "line": (220, 220, 220),
            "text": (230, 230, 230),
            "negative_text": (255, 100, 100),  # for mistakes
            "highlight": (130, 130, 255),
            # Buttons
            "button_bg": (90, 90, 120),
            "button_text": (240, 240, 240),
            # Overlays / special
            "title_text": (220, 220, 220),
            "game_over_overlay": (0, 0, 0, 150),  # black w/ alpha
        }
    else:
        return {
            # General backgrounds
            "main_bg": (255, 255, 255),
            "menu_bg": (230, 230, 230),
            # Lines, text, etc.
            "line": (0, 0, 0),
            "text": (0, 0, 0),
            "negative_text": (255, 0, 0),
            "highlight": (0, 0, 255),
            # Buttons
            "button_bg": (30, 144, 255),
            "button_text": (255, 255, 255),
            # Overlays / special
            "title_text": (25, 25, 112),
            "game_over_overlay": (0, 0, 0, 150),
        }

def toggle_night_mode():
    """Switch between day mode and night mode."""
    global night_mode
    night_mode = not night_mode


################################################################################
# Screen Size Adjustment
################################################################################
def set_screen_size(new_width, new_height):
    """
    Updates the global WIDTH, HEIGHT, and CELL_SIZE.
    Re-initializes the display mode in RESIZABLE mode.
    """
    global WIDTH, HEIGHT, CELL_SIZE, screen

    # Update global dimensions
    WIDTH, HEIGHT = new_width, new_height

    # Re-initialize the screen as resizable
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    # We'll size each Sudoku cell so that 9 columns fit in the available space.
    # Also consider that ~150 px are needed at the bottom for UI text.
    puzzle_area_height = HEIGHT - 150
    cell_size_w = WIDTH // GRID_SIZE
    cell_size_h = puzzle_area_height // GRID_SIZE
    CELL_SIZE = min(cell_size_w, cell_size_h)


################################################################################
# Sudoku Logic
################################################################################
def is_valid_move(board, row, col, num):
    """Checks whether placing `num` into board[row][col] is valid under Sudoku rules."""
    # Check row
    if num in board[row]:
        return False

    # Check column
    for r in range(GRID_SIZE):
        if board[r][col] == num:
            return False

    # Check 3x3 box
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for rr in range(start_row, start_row + 3):
        for cc in range(start_col, start_col + 3):
            if board[rr][cc] == num:
                return False

    return True

def solve_puzzle(board):
    """Backtracking solver that fills `board` in-place with a valid solution."""
    for row, col in itertools.product(range(GRID_SIZE), range(GRID_SIZE)):
        if board[row][col] == 0:
            for num in range(1, 10):
                if is_valid_move(board, row, col, num):
                    board[row][col] = num
                    if solve_puzzle(board):
                        return True
                    board[row][col] = 0
            return False
    return True

def generate_puzzle(difficulty="medium"):
    """
    Generates a Sudoku puzzle of a given difficulty along with its solution.
    Returns: (puzzle, solution)
    """
    # 1) Create an empty board
    board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    # 2) Solve it fully
    solve_puzzle(board)
    # Make a copy of the solved board
    board_solution = [row[:] for row in board]

    # 3) Remove cells based on difficulty
    removal_rate = {"easy": 0.4, "medium": 0.5, "hard": 0.6}
    cells_to_remove = int(GRID_SIZE * GRID_SIZE * removal_rate.get(difficulty, 0.5))

    while cells_to_remove > 0:
        row = random.randint(0, GRID_SIZE - 1)
        col = random.randint(0, GRID_SIZE - 1)
        if board[row][col] != 0:
            board[row][col] = 0
            cells_to_remove -= 1

    return board, board_solution


################################################################################
# Drawing / UI Functions
################################################################################
def draw_board():
    """
    Draws the Sudoku grid lines and any numbers in the puzzle.
    Negative values in puzzle indicate incorrectly filled numbers.
    """
    colors = get_colors(night_mode)
    screen.fill(colors["main_bg"])

    puzzle_draw_height = CELL_SIZE * GRID_SIZE

    # Draw sudoku grid lines
    for i in range(GRID_SIZE + 1):
        line_width = 4 if i % 3 == 0 else 1
        pygame.draw.line(
            screen, colors["line"],
            (i * CELL_SIZE, 0),
            (i * CELL_SIZE, puzzle_draw_height),
            line_width
        )
        pygame.draw.line(
            screen, colors["line"],
            (0, i * CELL_SIZE),
            (CELL_SIZE * GRID_SIZE, i * CELL_SIZE),
            line_width
        )

    # Draw numbers in each cell
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            val = puzzle[row][col]
            if val != 0:
                text_col = colors["negative_text"] if val < 0 else colors["text"]
                num = abs(val)
                text_surf = FONT.render(str(num), True, text_col)
                x_pos = col * CELL_SIZE + (CELL_SIZE - text_surf.get_width()) // 2
                y_pos = row * CELL_SIZE + (CELL_SIZE - text_surf.get_height()) // 2
                screen.blit(text_surf, (x_pos, y_pos))

    # Highlight selected cell
    if selected_cell:
        sel_row, sel_col = selected_cell
        pygame.draw.rect(
            screen, colors["highlight"],
            (sel_col * CELL_SIZE, sel_row * CELL_SIZE, CELL_SIZE, CELL_SIZE),
            3
        )

def draw_ui():
    """Draws the timer, mistakes counter, or pause/game-over overlay if needed."""
    global mistakes, paused
    colors = get_colors(night_mode)

    # If the puzzle isn't paused or ended, show the timer
    time_elapsed = 0
    if mistakes < 3 and not paused:
        time_elapsed = int(time.time() - start_time)

    # Timer at lower-left
    timer_text = FONT.render(f"Time: {time_elapsed}s", True, colors["text"])
    screen.blit(timer_text, (10, HEIGHT - 50))

    # Mistakes at lower-right
    mistakes_color = colors["negative_text"] if mistakes >= 3 else colors["text"]
    mistakes_text = FONT.render(f"Mistakes: {mistakes}/3", True, mistakes_color)
    screen.blit(mistakes_text, (WIDTH - 180, HEIGHT - 50))

    # Pause overlay if paused
    if paused:
        draw_pause_overlay()

    # If game over, overlay
    if mistakes >= 3:
        draw_game_over()

    pygame.display.flip()

def draw_pause_overlay():
    """Semi-transparent pause menu with 'Resume' and 'Main Menu' buttons."""
    colors = get_colors(night_mode)

    overlay_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay_surface.fill((0, 0, 0, 150))  # black w/ alpha
    screen.blit(overlay_surface, (0, 0))

    # "Paused" text
    paused_text_surf = TITLE_FONT.render("Paused", True, colors["title_text"])
    px = (WIDTH - paused_text_surf.get_width()) // 2
    py = HEIGHT // 2 - 80
    screen.blit(paused_text_surf, (px, py))

    # Resume button
    resume_rect = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 - 10, 140, 50)
    pygame.draw.rect(screen, colors["button_bg"], resume_rect, border_radius=10)
    resume_text = FONT.render("Resume", True, colors["button_text"])
    rx = resume_rect.x + (resume_rect.width - resume_text.get_width()) // 2
    ry = resume_rect.y + (resume_rect.height - resume_text.get_height()) // 2
    screen.blit(resume_text, (rx, ry))

    # Main Menu button
    menu_rect = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 + 60, 140, 50)
    pygame.draw.rect(screen, colors["button_bg"], menu_rect, border_radius=10)
    menu_text = FONT.render("Main Menu", True, colors["button_text"])
    mx = menu_rect.x + (menu_rect.width - menu_text.get_width()) // 2
    my = menu_rect.y + (menu_rect.height - menu_text.get_height()) // 2
    screen.blit(menu_text, (mx, my))

def draw_game_over():
    """Draws a semi-transparent overlay with 'GAME OVER' and a 'Restart' button."""
    colors = get_colors(night_mode)

    overlay_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay_surface.fill(colors["game_over_overlay"])
    screen.blit(overlay_surface, (0, 0))

    # "Game Over" text
    game_over_text = TITLE_FONT.render("GAME OVER!", True, colors["negative_text"])
    go_x = (WIDTH - game_over_text.get_width()) // 2
    go_y = HEIGHT // 2 - 60
    screen.blit(game_over_text, (go_x, go_y))

    # Restart button
    button_rect = pygame.Rect(WIDTH // 2 - 60, HEIGHT // 2 + 10, 120, 50)
    pygame.draw.rect(screen, colors["button_bg"], button_rect, border_radius=10)
    restart_text = FONT.render("Restart", True, colors["button_text"])
    rt_x = button_rect.x + (button_rect.width - restart_text.get_width()) // 2
    rt_y = button_rect.y + (button_rect.height - restart_text.get_height()) // 2
    screen.blit(restart_text, (rt_x, rt_y))

def draw_start_menu():
    """
    Draws the Start Menu. Two buttons: "Play" and "Instructions."
    """
    colors = get_colors(night_mode)
    screen.fill(colors["menu_bg"])

    # Title
    title_text = TITLE_FONT.render("Sudoku Puzzle Game", True, colors["title_text"])
    title_x = (WIDTH - title_text.get_width()) // 2
    title_y = HEIGHT // 4
    screen.blit(title_text, (title_x, title_y))

    # Play button
    play_button_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2, 150, 50)
    pygame.draw.rect(screen, colors["button_bg"], play_button_rect, border_radius=8)
    play_text = FONT.render("Play", True, colors["button_text"])
    pt_x = play_button_rect.x + (play_button_rect.width - play_text.get_width()) // 2
    pt_y = play_button_rect.y + (play_button_rect.height - play_text.get_height()) // 2
    screen.blit(play_text, (pt_x, pt_y))

    # Instructions button
    instr_button_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 70, 150, 50)
    pygame.draw.rect(screen, colors["button_bg"], instr_button_rect, border_radius=8)
    instr_text = FONT.render("Instructions", True, colors["button_text"])
    it_x = instr_button_rect.x + (instr_button_rect.width - instr_text.get_width()) // 2
    it_y = instr_button_rect.y + (instr_button_rect.height - instr_text.get_height()) // 2
    screen.blit(instr_text, (it_x, it_y))

    # Night mode hint
    nm_hint_text = SMALL_FONT.render("Press 'N' for Night Mode", True, colors["text"])
    nm_hint_x = (WIDTH - nm_hint_text.get_width()) // 2
    nm_hint_y = instr_button_rect.y + instr_button_rect.height + 60
    screen.blit(nm_hint_text, (nm_hint_x, nm_hint_y))

    pygame.display.flip()
    return play_button_rect, instr_button_rect

def draw_instructions_window():
    """
    Draws a separate Instructions screen with a "Back" button,
    placed in a bounding rectangle so it won't go off-screen.
    """
    colors = get_colors(night_mode)
    screen.fill(colors["menu_bg"])

    # Header
    header_text = TITLE_FONT.render("Instructions", True, colors["title_text"])
    hx = (WIDTH - header_text.get_width()) // 2
    hy = 30
    screen.blit(header_text, (hx, hy))

    # We'll draw instructions within a bounding box to avoid going off-screen
    instructions_box_rect = pygame.Rect(50, 100, WIDTH - 100, HEIGHT - 200)
    # Fill background
    instructions_surf = pygame.Surface((instructions_box_rect.width, instructions_box_rect.height))
    instructions_surf.fill(colors["menu_bg"])

    instructions = [
        "Sudoku rules:",
        "1. Fill each row, column, and 3x3 box with digits 1-9 without repetition.",
        "2. You can make up to 3 mistakes before Game Over.",
        "",
        "Controls:",
        " - Arrow keys: Move selection",
        " - 1-9: Fill cell, Backspace: Clear cell",
        " - H: Hint (fills one empty cell)",
        " - A: Auto-solve puzzle",
        " - E, M, D: Change difficulty on the fly",
        " - N: Toggle Night Mode",
        " - P: Pause/Unpause the puzzle",
        " - Resize the window to scale the puzzle/UI",
        "",
        "Good luck, and have fun!"
    ]

    # Render lines into instructions_surf with some vertical spacing.
    y_offset = 0
    line_spacing = 26  # roughly SMALL_FONT size + a bit
    for line in instructions:
        line_surf = SMALL_FONT.render(line, True, colors["text"])
        # If the next line might go off the bottom, we break to avoid overflow
        if y_offset + line_surf.get_height() > instructions_box_rect.height:
            break
        instructions_surf.blit(line_surf, (0, y_offset))
        y_offset += line_spacing

    # Blit instructions_surf onto screen
    screen.blit(instructions_surf, (instructions_box_rect.x, instructions_box_rect.y))

    # Back button
    back_button_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 80, 100, 40)
    pygame.draw.rect(screen, colors["button_bg"], back_button_rect, border_radius=8)
    back_text = FONT.render("Back", True, colors["button_text"])
    bx = back_button_rect.x + (back_button_rect.width - back_text.get_width()) // 2
    by = back_button_rect.y + (back_button_rect.height - back_text.get_height()) // 2
    screen.blit(back_text, (bx, by))

    pygame.display.flip()
    return back_button_rect


################################################################################
# Game Interaction Functions
################################################################################
def handle_input(key):
    """Handles numeric and deletion input for the currently selected cell."""
    global mistakes
    if selected_cell is None:
        return

    row, col = selected_cell

    # Clear cell if backspace or delete
    if key in (pygame.K_DELETE, pygame.K_BACKSPACE):
        if puzzle[row][col] != 0:
            puzzle[row][col] = 0
        return

    # If cell is empty or marked incorrect, allow placing a number
    if puzzle[row][col] == 0 or puzzle[row][col] < 0:
        if pygame.K_1 <= key <= pygame.K_9:
            num = key - pygame.K_0
        elif pygame.K_KP1 <= key <= pygame.K_KP9:
            num = key - pygame.K_KP0
        else:
            return

        # Check correctness vs. solution
        if solution[row][col] == num:
            puzzle[row][col] = num
        else:
            puzzle[row][col] = -num  # Mark as incorrect
            mistakes += 1

def provide_hint():
    """Fills one empty cell with its correct digit."""
    empty_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if puzzle[r][c] == 0]
    if not empty_cells:
        return
    r, c = random.choice(empty_cells)
    puzzle[r][c] = solution[r][c]

def auto_solve():
    """Fills puzzle with the solution immediately."""
    global puzzle
    puzzle = [row[:] for row in solution]

def change_difficulty(level):
    """Generates a new puzzle of given difficulty, resets mistakes, timer, etc."""
    global puzzle, solution, mistakes, start_time, selected_cell, current_difficulty
    current_difficulty = level
    puzzle, solution = generate_puzzle(current_difficulty)
    mistakes = 0
    start_time = time.time()
    selected_cell = None

def restart_game():
    """Restart the game by generating a new puzzle at the current difficulty."""
    global puzzle, solution, mistakes, start_time, selected_cell
    puzzle, solution = generate_puzzle(current_difficulty)
    mistakes = 0
    start_time = time.time()
    selected_cell = None

def move_selection(key):
    """Moves the selection box with arrow keys."""
    global selected_cell
    if selected_cell is None:
        selected_cell = (0, 0)
        return

    row, col = selected_cell
    if key == pygame.K_UP and row > 0:
        row -= 1
    elif key == pygame.K_DOWN and row < GRID_SIZE - 1:
        row += 1
    elif key == pygame.K_LEFT and col > 0:
        col -= 1
    elif key == pygame.K_RIGHT and col < GRID_SIZE - 1:
        col += 1

    selected_cell = (row, col)

def pause_game():
    """
    Enters paused state, storing the time so we can freeze the timer.
    """
    global paused, pause_start_time
    paused = True
    pause_start_time = time.time()

def unpause_game():
    """
    Leaves paused state, adjusting start_time so the timer won't jump.
    """
    global paused, start_time, pause_start_time
    paused = False
    # Adjust start_time so that the puzzle timer doesn't advance during pause
    paused_duration = time.time() - pause_start_time
    start_time += paused_duration

def handle_keydown(key):
    """
    Central handler for key presses in the game loop.
    Press 'N' to toggle night mode at any point.
    Press 'P' to pause/unpause if not in a menu or game over.
    """
    global in_start_menu, in_instructions_menu, mistakes, paused

    # Toggle night mode
    if key == pygame.K_n:
        toggle_night_mode()
        return

    # If on start menu or instructions menu, we ignore puzzle keys unless we want to handle them
    # If game over, we also ignore puzzle input

    # If the puzzle is not over:
    if mistakes < 3:
        # Pause/unpause
        if key == pygame.K_p:
            if paused:
                unpause_game()
            else:
                pause_game()
            return

    if paused:
        # When paused, only 'N' or 'P' do anything. So we ignore other inputs.
        return

    # Normal gameplay controls
    if mistakes >= 3:
        # game over, ignore further puzzle input
        return
    else:
        # In normal play state
        if key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
            move_selection(key)
        elif key == pygame.K_h:
            provide_hint()
        elif key == pygame.K_a:
            auto_solve()
        elif key == pygame.K_e:
            change_difficulty("easy")
        elif key == pygame.K_m:
            change_difficulty("medium")
        elif key == pygame.K_d:
            change_difficulty("hard")
        else:
            handle_input(key)


################################################################################
# Main Loop
################################################################################
def main():
    global running, in_start_menu, in_instructions_menu
    global puzzle, solution, mistakes, start_time, selected_cell, paused

    # Set initial screen size (resizable) and compute initial CELL_SIZE
    set_screen_size(WIDTH, HEIGHT)

    clock = pygame.time.Clock()
    puzzle, solution = generate_puzzle(current_difficulty)
    mistakes = 0
    start_time = time.time()
    selected_cell = None
    paused = False

    while running:
        if in_start_menu:
            play_btn, instr_btn = draw_start_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    set_screen_size(event.w, event.h)
                elif event.type == pygame.KEYDOWN:
                    handle_keydown(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # left click
                        if play_btn.collidepoint(event.pos):
                            puzzle, solution = generate_puzzle(current_difficulty)
                            mistakes = 0
                            start_time = time.time()
                            selected_cell = None
                            paused = False
                            in_start_menu = False
                        elif instr_btn.collidepoint(event.pos):
                            in_instructions_menu = True
                            in_start_menu = False

        elif in_instructions_menu:
            back_button = draw_instructions_window()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    set_screen_size(event.w, event.h)
                elif event.type == pygame.KEYDOWN:
                    handle_keydown(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and back_button.collidepoint(event.pos):
                        in_instructions_menu = False
                        in_start_menu = True

        else:
            # Main Sudoku Game or Game Over
            draw_board()
            draw_ui()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    set_screen_size(event.w, event.h)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # If game over, check if "Restart" was clicked
                    if mistakes >= 3:
                        restart_button_rect = pygame.Rect(WIDTH // 2 - 60, HEIGHT // 2 + 10, 120, 50)
                        if restart_button_rect.collidepoint(event.pos):
                            restart_game()
                            continue

                    # If paused, check if "Resume" or "Main Menu" was clicked
                    if paused:
                        resume_rect = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 - 10, 140, 50)
                        menu_rect = pygame.Rect(WIDTH // 2 - 70, HEIGHT // 2 + 60, 140, 50)
                        if resume_rect.collidepoint(event.pos):
                            unpause_game()
                        elif menu_rect.collidepoint(event.pos):
                            # Return to main menu
                            in_start_menu = True
                            paused = False
                        continue

                    # If not paused or game-over, handle puzzle cell clicks
                    if mistakes < 3:
                        x, y = event.pos
                        # Ensure we clicked inside puzzle area
                        if x < CELL_SIZE * GRID_SIZE and y < CELL_SIZE * GRID_SIZE:
                            selected_cell = (y // CELL_SIZE, x // CELL_SIZE)

                elif event.type == pygame.KEYDOWN:
                    handle_keydown(event.key)

        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
