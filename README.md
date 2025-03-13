# Sudoku Puzzle Game

A fully functional Sudoku game built with Python and Pygame. Enjoy a classic 9×9 Sudoku grid with multiple difficulty levels, night mode, a pause menu, and a clean user interface that supports window resizing.

---

## Features

1. **Start Menu**  
   - Options to **Play** or **View Instructions**.  
   - Press **N** to toggle Night Mode at any time.

2. **Instructions Menu**  
   - Explains Sudoku rules and controls.  
   - Press **Back** to return to the main menu.

3. **Gameplay**  
   - **9×9 Sudoku** with support for **Easy**, **Medium**, and **Hard** difficulties.  
   - Insert numbers **(1-9)** into cells or **clear** a cell with **Backspace/Delete**.  
   - **Mistakes** are tracked (up to 3).  
   - **Hints** (H key) fill one empty cell.  
   - **Auto-solve** (A key) completes the puzzle.  
   - **Change difficulty** at any time (E, M, or D keys).  
   - **Night Mode** (N key) inverts the color scheme to a dark theme.  
   - **Pause Menu** (P key) freezes the timer and disables all puzzle actions until you resume.  
   - **Timer** showing play duration (ignoring paused time).  

4. **Resizing**  
   - The window can be resized; puzzle and UI will adapt accordingly.

5. **Game Over & Restart**  
   - Make three mistakes and you see “Game Over” with a **Restart** button.

---

## Installation

1. **Python 3.7+** is recommended.  
2. Install **Pygame**:
   ```bash
   pip install pygame
   ```
3. Download or clone this repository to get all the game files.

---

## Running the Game

1. Open a terminal or command prompt in the project directory.  
2. Run the main Python file:
   ```bash
   python sudoku.py
   ```
3. A **resizable window** will open.  

---

## Controls

- **Mouse**:
  - Click **Play** / **Instructions** buttons in the menus.
  - Click cells on the Sudoku board to select them.
  - Click **Restart** when Game Over, or **Resume** / **Main Menu** from the Pause screen.

- **Keyboard**:
  - **Arrow Keys**: Move selection up/down/left/right.  
  - **1-9**: Place that digit in the selected cell.  
  - **Backspace/Delete**: Clear the selected cell.  
  - **H**: Fill a single random empty cell with the correct digit (hint).  
  - **A**: Automatically solve the puzzle.  
  - **E, M, D**: Switch puzzle difficulty to **Easy**, **Medium**, or **Hard**.  
  - **P**: Pause/Unpause the game.  
  - **N**: Toggle Night Mode (dark background, lighter text).

---

## How to Play

1. **Start the Game**:  
   - From the **Start Menu**, click **Play** or press any key to begin.  
   - The puzzle is automatically generated based on your chosen difficulty (default: Medium).

2. **Fill the Grid**:  
   - Click or use arrow keys to select a cell.  
   - Press a **1-9** key to insert that number.  
   - If it’s correct (matching the solution), it becomes permanent; if it’s wrong, it turns red and increments your mistakes.

3. **Mistakes**:  
   - You can only make **3 mistakes**. On the third mistake, the game ends.

4. **Pause**:  
   - Press **P** to pause. The timer will stop, and a menu offers **Resume** or **Main Menu**.  

5. **Restart**:  
   - If you reach 3 mistakes (Game Over), click **Restart** to generate a new puzzle with the current difficulty.

---

## Project Structure

- **sudoku.py**: Main game logic and Pygame loop.
- **README.md**: Documentation (this file).

---

## Contributing

Feel free to open issues or pull requests if you want to improve the game or fix bugs. All contributions are welcome.

---

## License

This project can be distributed and modified under open license terms
---

Enjoy puzzling! If you have any questions or suggestions, please let me know.
