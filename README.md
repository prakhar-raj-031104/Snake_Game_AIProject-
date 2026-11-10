# Snake Game AI – Breadth-First Search

## Team: DietCoke

| Name                         | Roll Number |
|------------------------------|-------------|
| Nomula Naga Eswara Akshay    | B24ME032    |
| Nirbhay Pratap Singh Tomar   | B24EC511    |
| Soham Jayesh Mahale          | B24ME028    |
| Prakhar Raj Singhal          | B24EC512    |
| Gajera Rudra Pravinkumar     | B24MT006    |

---

An autonomous agent that plays the classic Snake game.

The AI uses the **Breadth-First Search (BFS)** algorithm to find the shortest
possible path from the snake's head to the food. The game board is treated as
a grid, with the snake's body acting as obstacles. This pathfinding approach
lets the AI move around the board efficiently and avoid hitting itself and
the walls.

The core logic is written in **Python** and the visual interface uses
**Pygame**. The agent shows a classic AI technique for solving problems in a
deterministic environment.

---

## Features

- Fully autonomous snake controlled by a BFS agent
- The planned path is drawn live on the board
- Safety check so the snake does not trap itself
- Clean, object-oriented and modular code
- Game logic is separate from graphics, so it can be tested without a window
- Headless mode to benchmark the AI from the terminal
- Unit tests with `pytest`

---

## Project structure

```
Snake_Game_AIProject-/
├── main.py               # Entry point (command-line options)
├── snake_ai/
│   ├── config.py         # GameConfig: board size, speed, colours
│   ├── geometry.py       # Point and Direction
│   ├── board.py          # Board: grid size and neighbouring cells
│   ├── snake.py          # Snake: body, movement, growth, self-collision
│   ├── food.py           # Food: spawns on a random empty cell
│   ├── game.py           # SnakeGame: game rules, score, game over / win
│   ├── pathfinder.py     # BFSPathfinder: shortest path + flood fill
│   ├── agent.py          # BFSAgent: decides the next move
│   ├── renderer.py       # Renderer: draws everything with Pygame
│   └── app.py            # SnakeApp: main loop (input -> AI -> update -> draw)
├── tests/
│   └── test_snake_ai.py  # Unit tests
├── requirements.txt
└── requirements-dev.txt
```

---

## How to run it on your laptop

**Requirements:** Python 3.10 or newer.

1. Clone the repository and enter the folder:

   ```bash
   git clone https://github.com/prakhar-raj-031104/Snake_Game_AIProject-.git
   ```

   ```bash
   cd Snake_Game_AIProject-
   ```

2. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv venv
   ```

   Windows:

   ```bash
   venv\Scripts\activate
   ```

   macOS / Linux:

   ```bash
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the game:

   ```bash
   python main.py
   ```

### Keyboard controls

| Key              | Action                     |
|------------------|----------------------------|
| `Space`          | Pause / resume             |
| `R`              | Restart the game           |
| `P`              | Show / hide the BFS path   |
| `↑` or `+`       | Speed up                   |
| `↓` or `-`       | Slow down                  |
| `Esc` or `Q`     | Quit                       |

### Command-line options

```bash
python main.py --width 15 --height 15 --fps 25 --cell-size 35
```

| Option         | Default | Meaning                               |
|----------------|---------|---------------------------------------|
| `--width`      | 20      | Number of columns                     |
| `--height`     | 20      | Number of rows                        |
| `--cell-size`  | 30      | Size of one cell in pixels            |
| `--fps`        | 15      | Moves per second                      |
| `--seed`       | random  | Seed for a repeatable game            |
| `--headless`   | off     | Play without a window, print results  |
| `--games`      | 5       | Number of games in headless mode      |

Benchmark the AI without opening a window:

```bash
python main.py --headless --games 10
```

---

## How the AI works

### 1. Breadth-First Search (BFS)

BFS starts at the snake's head and explores the grid **level by level**:
first all cells 1 step away, then all cells 2 steps away, and so on. It uses a
**queue** (first in, first out) and remembers where it came from for each
cell. The first time it reaches the food, it has found the **shortest path**.
Walking back through the "came from" links rebuilds that path.

- Walls: cells outside the grid are never explored.
- Obstacles: the snake's body cells are skipped. The tail is not treated as an
  obstacle, because it moves away on the next step.
- Time complexity: `O(W × H)`, every cell is visited at most once.

### 2. The decision process (`BFSAgent`)

Every move, the agent tries these plans in order:

1. **Go for the food.** Use BFS to find the shortest path to the food. Before
   taking it, simulate the snake after eating and check, again with BFS,
   that the head can still reach the tail. If it can, the snake cannot be
   trapped, so the path is safe.
2. **Follow the tail.** If the food path is missing or unsafe, chase the tail.
   This keeps the snake alive while the body moves and the food opens up.
3. **Find open space.** As a last resort, take the move that leads to the
   largest open area (counted with a BFS flood fill).

To avoid circling forever, the agent has a **patience** limit. If it goes too
long without eating, it takes the food path even when it is risky.

### 3. Design (OOP principles)

- **Single responsibility:** each class does one job (`Snake` moves,
  `Food` spawns, `BFSPathfinder` searches, `Renderer` draws, …).
- **Encapsulation:** the snake keeps its body private and offers methods
  like `move()`, `turn()` and `occupies()`.
- **Separation of concerns:** `SnakeGame` holds the rules and knows nothing
  about Pygame. That makes it easy to test and to run headless.
- **Composition:** `SnakeApp` is built from a `SnakeGame`, a `BFSAgent`
  and a `Renderer`. Any of them could be swapped out, for example for a
  different AI agent.

---

## Running the tests

```bash
pip install -r requirements-dev.txt
```

```bash
pytest
```

---

## Tech stack

- Python 3.10+
- Pygame
- pytest (tests)
