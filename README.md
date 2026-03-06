# Tile Matching Puzzle Solver
Automatic solver for a tile-matching puzzle using **Breadth-First Search (BFS)** and **Uniform Cost Search (UCS)**.

This project was developed as part of an Artificial Intelligence course project.

The program generates a puzzle board and automatically computes the optimal sequence of moves needed to eliminate all tile pairs while minimizing total cost.

---

## Project Overview

The puzzle board is represented as a **2D grid** where each colored tile appears exactly twice.

Tiles can slide across empty spaces in four directions:

- Up
- Down
- Left
- Right

When two identical tiles align horizontally or vertically with **no obstacles between them**, they are removed from the board.

The goal is to find a sequence of moves that removes all tiles with **minimum total cost**.

---

## Algorithms Used

### Breadth-First Search (BFS)

BFS is used to compute the **shortest sliding path** between two matching tiles.

The algorithm:

1. Starts from a tile position
2. Expands reachable empty cells in four directions
3. Tracks visited positions to avoid redundant exploration
4. Stops when the matching tile can be connected

Because BFS explores nodes level-by-level, the first valid path found is guaranteed to be the **shortest path**.

---

### Uniform Cost Search (UCS)

After computing shortest paths for each tile pair, the solver must determine the **optimal elimination order**.

Each color is assigned a **random weight (1–5)**.

The cost of eliminating a pair is defined as: cost = sliding_steps × weight


Uniform Cost Search explores board states in order of **lowest cumulative cost**, ensuring the final solution has the **minimum total cost**.

---

## Features

- Automatic puzzle solver
- BFS-based shortest path detection
- UCS-based optimal elimination ordering
- Visualization of tile movements
- Displays sliding steps and total cost
- Detects unsolvable board configurations

---

## Example Workflow

1. User inputs board size and number of tile pairs
2. Program generates a random puzzle board
3. Solver computes optimal elimination sequence
4. Visualization displays step-by-step solution

Example configuration:
<img width="501" height="121" alt="image" src="https://github.com/user-attachments/assets/1764cf15-82ce-4cad-b46d-1b4ff91e3244" />
Board size: 8 × 8
<img width="493" height="128" alt="image" src="https://github.com/user-attachments/assets/67be389e-4c8a-423a-a7c1-b9e44768bfdd" />
Tile pairs: 10


Output includes:

- total sliding steps
- total weighted cost
- elimination order for tile colors

---

## Project Structure
tile-matching-puzzle-solver
│
├── main.py # main solver logic
├── graphs.py # visualization utilities
├── run.py # program entry point
├── README.md
└── .gitignore

---

## How to Run

Make sure Python is installed.

Run the program:

```bash
python run.py


**## Limitations**

The main limitation is search complexity.

The number of possible board states grows rapidly as:

board size increases

number of tile pairs increases

For large boards (e.g., 10×10 with many tiles), the search space becomes very large and computation time increases significantly.

Future improvements could include:

heuristic search (A*)

pruning strategies

improved state representation

**Author**

Hu Xin
Tsinghua University
Artificial Intelligence Course Project

## Demo
Below is an example of the solver running on an **8×8 board with 10 tile pairs**.
<img width="1582" height="918" alt="image" src="https://github.com/user-attachments/assets/7f6c06c6-9c43-4398-a1ef-0e7823544748" />
The solver automatically finds the optimal sequence of moves required to clear the board.

The visualization shows:

- **Initial board state** (top left)
- **Step-by-step elimination of tile pairs**
- **Shortest sliding paths** computed using Breadth-First Search (BFS)
- **Tile weights and costs** used by the Uniform Cost Search (UCS)
- **Total solution cost and number of slides**

Each numbered step corresponds to removing one pair of tiles.  
The colored line indicates the shortest path discovered by BFS, while the order of elimination is determined by UCS to minimize the overall weighted cost.

In this example:

- Board size: **8 × 8**
- Tile pairs: **10**
- Total slides: **9**
- Total weighted cost: **23**

The solver successfully finds a globally optimal solution and visualizes the entire process.


