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

An autonomous agent that plays **Snake in 3D**.

The snake lives inside a cube and can move left/right, forward/back **and
up/down**. The AI uses the **Breadth-First Search (BFS)** algorithm to find
the shortest path from the snake's head to the food. The world is treated as
a 3D grid of cells, with the snake's body and rocks acting as obstacles.

The core logic is written in **Python**. The 3D graphics are drawn with
**Pygame** (pygame-ce) using our own small 3D engine, so no extra libraries
are needed.

---

## What is new in our version

| Idea | What it adds |
|------|--------------|
| **3D world** | The snake moves in a 10 × 10 × 10 cube with 6 directions instead of 4. BFS works unchanged: only the number of neighbours changes. |
| **Rocks** | Random rocks float inside the cube. They are placed so that no part of the world is ever sealed off (checked with BFS). |
| **Golden apples** | Worth **5 points** instead of 1, but they **vanish after 40 moves**. |
| **Smart targeting** | One BFS from the head reaches every cell at once. The AI scores every food by *points per move* and skips golden apples it cannot reach in time. |
| **Look-ahead safety** | Before eating, the AI imagines the snake after the meal and checks it can still reach its own tail, so it never traps itself. |
| **Interactive 3D camera** | Drag to rotate, scroll to zoom, auto-rotation, floor shadows and food markers that stay visible behind the snake. |
| **Classic mode** | `--height 1` turns the cube into a flat board: the same code plays normal 2D Snake. |

---

## Features

- Fully autonomous snake controlled by a BFS agent, in 3D or 2D
- The planned path is drawn live in the world
- Rocks, apples and time-limited golden apples
- A small 3D engine: perspective projection, back-face culling, shading and
  the painter's algorithm, built on plain Pygame
- Clean, object-oriented and modular code
- Game logic is separate from graphics, so it can be tested without a window
- Headless mode to benchmark the AI from the terminal
- 20 unit tests with `pytest`

---

## Project structure

```
Snake_Game_AIProject-/
├── main.py               # Entry point (command-line options)
├── snake_ai/
│   ├── config.py         # GameConfig: world size, speed, window, colours
│   ├── geometry.py       # Point (x, y, z) and the 6 Directions
│   ├── board.py          # Board: 3D world size, rocks, neighbouring cells
│   ├── snake.py          # Snake: body, movement, growth, self-collision
│   ├── food.py           # Food: apples and golden apples with a timer
│   ├── game.py           # SnakeGame: game rules, score, rocks, game over / win
│   ├── pathfinder.py     # BFSPathfinder: shortest path, explore-all, flood fill
│   ├── agent.py          # BFSAgent: decides the next move
│   ├── camera.py         # Camera: orbiting 3D camera and perspective projection
│   ├── renderer.py       # Renderer: draws the 3D world with Pygame
│   └── app.py            # SnakeApp: main loop (input -> AI -> update -> draw)
├── tests/
│   └── test_snake_ai.py  # Unit tests
├── requirements.txt
└── requirements-dev.txt
```

---

## How to run it on your laptop

**Requirements:** Python 3.10 or newer (tested on Python 3.10 through 3.14).

> **Note:** The project uses `pygame-ce` (Pygame Community Edition) in `requirements.txt`, which provides out-of-the-box precompiled support across all modern Python releases (including Python 3.12+ and 3.14).

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

   Or play classic flat Snake:

   ```bash
   python main.py --height 1 --width 20 --depth 20
   ```

### Controls

| Input                 | Action                         |
|-----------------------|--------------------------------|
| Drag with left mouse  | Rotate the camera              |
| Mouse wheel           | Zoom in / out                  |
| `←` `→` `↑` `↓`       | Rotate the camera              |
| `A`                   | Auto-rotation on / off         |
| `Space`               | Pause / resume                 |
| `R`                   | Restart with a new world       |
| `P`                   | Show / hide the BFS path       |
| `+` / `-`             | Speed up / slow down           |
| `Esc` or `Q`          | Quit                           |

### Command-line options

```bash
python main.py --width 12 --depth 12 --height 8 --rocks 0.05 --speed 12
```

| Option       | Default | Meaning                                          |
|--------------|---------|--------------------------------------------------|
| `--width`    | 10      | Cells left-right                                 |
| `--depth`    | 10      | Cells front-back                                 |
| `--height`   | 10      | Cells up-down (`1` = classic 2D Snake)           |
| `--rocks`    | 0.03    | Share of cells filled with rocks (0 to 0.2)      |
| `--golden`   | 0.3     | Chance of a golden apple after each apple        |
| `--speed`    | 8       | Snake moves per second                           |
| `--seed`     | random  | Seed for a repeatable game                       |
| `--headless` | off     | Play without a window, print results             |
| `--games`    | 5       | Number of games in headless mode                 |

Benchmark the AI without opening a window:

```bash
python main.py --headless --games 3 --width 8 --depth 8 --height 8
```

---

## How the AI works

### 1. Breadth-First Search (BFS) in 3D

BFS starts at the snake's head and explores the world **level by level**:
first all cells 1 step away, then all cells 2 steps away, and so on. It uses a
**queue** (first in, first out) and remembers where it came from for each
cell. The first time it reaches a cell, it has found the **shortest path**.
Walking back through the "came from" links rebuilds that path.

- In 3D every cell has up to **6 neighbours** (in 2D: 4). The BFS code is
  exactly the same: only `Board.neighbors()` knows about dimensions.
- Walls and rocks: `Board.neighbors()` never returns them.
- Obstacles: the snake's body cells are skipped. The tail is not treated as an
  obstacle, because it moves away on the next step.
- Time complexity: `O(W × D × H)`, every cell is visited at most once.

### 2. The decision process (`BFSAgent`)

Every move, the agent tries these plans in order:

1. **Pick the best food.** One BFS from the head explores every reachable
   cell. Each piece of food gets a score of *points ÷ moves needed*. A golden
   apple that would vanish before the snake arrives is skipped. The best
   target is taken only if it is safe: the AI simulates the snake after
   eating and checks, again with BFS, that the head can still reach the tail.
2. **Follow the tail.** If no food is safely reachable, chase the tail. This
   keeps the snake alive while the body moves and the food opens up.
3. **Find open space.** As a last resort, take the move that leads to the
   largest open area (counted with a BFS flood fill).

To avoid circling forever, the agent has a **patience** limit. If it goes too
long without eating, it takes a food path even when it is risky.

### 3. The 3D graphics (`Camera` + `Renderer`)

Pygame can only draw flat shapes, so we built a tiny 3D engine:

1. **Camera:** the world is turned around the vertical axis (yaw) and tilted
   (pitch), then divided by depth (perspective), so far things look smaller.
2. **Back-face culling:** for each cube, only the faces pointing towards the
   camera are drawn.
3. **Painter's algorithm:** all objects are sorted by depth and drawn from far
   to near, so near cubes cover far ones.
4. **Shading:** each face is darker or lighter depending on how much it faces
   the light, which makes the cubes look solid.
5. **Depth cues:** shadows on the floor and drop lines show where the head and
   the food are inside the cube.

### 4. Design (OOP principles)

- **Single responsibility:** each class does one job (`Snake` moves,
  `Food` counts down, `BFSPathfinder` searches, `Camera` projects,
  `Renderer` draws, …).
- **Encapsulation:** the snake keeps its body private and offers methods
  like `move()`, `turn()` and `occupies()`.
- **Separation of concerns:** `SnakeGame` holds the rules and knows nothing
  about Pygame. That makes it easy to test and to run headless.
- **Composition:** `SnakeApp` is built from a `SnakeGame`, a `BFSAgent`
  and a `Renderer`. Any of them could be swapped out, for example for a
  different AI agent.
- **Abstraction:** the pathfinder does not know whether the world is 2D or
  3D; it only asks the board for neighbours.

---

## Results

Measured with headless mode (3 games each, `--seed 1`):

| World | Rocks | Average score | Best score | Golden apples eaten (best game) |
|-------|-------|---------------|------------|---------------------------------|
| 3D cube 8 × 8 × 8 | 3% | 603.3 | 692 | 77 |
| Flat 20 × 20 (`--height 1`) | none | 383.3 | 504 | 49 |

```bash
python main.py --headless --games 3 --seed 1 --width 8 --depth 8 --height 8
```

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
- Pygame (pygame-ce), with our own small 3D renderer
- pytest (tests)
