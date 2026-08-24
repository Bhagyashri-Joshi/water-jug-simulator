# Water Jug Simulator

A Python-based **Water Jug Problem Simulator** that demonstrates and compares different search algorithms for solving the classic water jug problem.

The simulator provides a graphical interface where users can configure jug capacities, select a target amount, run different algorithms, and visualize the solution steps and search tree.

## Features

* Solve the Water Jug Problem using multiple search algorithms.
* Compare algorithm performance.
* Visualize the generated solution path.
* Display the search tree.
* Interactive graphical user interface.
* Track solution steps and execution details.

## Algorithms Implemented

The project currently includes:

* **Breadth-First Search (BFS)**
* **Depth-First Search (DFS)**
* **A* Search**
* **Iterative Deepening Depth-First Search (IDDFS)**

## Project Structure

```text
water-jug-simulator/
│
├── algorithms/
│   ├── __init__.py
│   ├── astar.py
│   ├── bfs.py
│   ├── dfs.py
│   ├── iddfs.py
│   └── state.py
│
├── gui/
│   ├── __init__.py
│   ├── app.py
│   ├── compare_window.py
│   ├── control_panel.py
│   ├── jug_panel.py
│   ├── log_panel.py
│   └── tree_panel.py
│
├── simulation/
│   ├── __init__.py
│   ├── controller.py
│   └── tree_builder.py
│
├── main.py
├── requirements.txt
└── .gitignore
```

## Requirements

* Python 3.10 or higher
* pip
* Required Python packages listed in `requirements.txt`

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/water-jug-simulator.git
cd water-jug-simulator
```

### 2. Create a virtual environment

**Windows:**

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Simulator

Run the main application:

```bash
python main.py
```

The graphical interface will open, allowing you to configure the water jugs and select a search algorithm.

## How It Works

The Water Jug Problem represents the state of the system using the amount of water currently present in each jug.

For example, with two jugs of capacities **4L and 3L**, the initial state can be represented as:

```text
(0, 0)
```

Possible operations include:

* Fill a jug completely.
* Empty a jug.
* Pour water from one jug into the other.
* Continue until the target amount is reached.

The algorithms explore these possible states to find a solution.

## Algorithm Comparison

| Algorithm | Approach          | Main Characteristic                                 |
| --------- | ----------------- | --------------------------------------------------- |
| BFS       | Uninformed Search | Finds the shortest solution path                    |
| DFS       | Uninformed Search | Explores deeply before backtracking                 |
| IDDFS     | Iterative Search  | Combines depth-limited search with increasing depth |
| A*        | Informed Search   | Uses a heuristic to guide the search                |

## Example

Suppose the jugs have capacities:

```text
Jug A = 4 Litres
Jug B = 3 Litres
Target = 2 Litres
```

The simulator searches through possible states until it finds a state containing the required target amount.

A solution can then be displayed as a sequence of states, for example:

```text
(0, 0)
   ↓
(4, 0)
   ↓
(1, 3)
   ↓
(1, 0)
   ↓
(0, 1)
   ...
```

## Technologies Used

* **Python**
* **Object-Oriented Programming**
* **Search Algorithms**
* **Graph/State-Space Search**
* **GUI-based simulation**

## Learning Objectives

This project demonstrates:

* State-space representation
* Problem-solving using search algorithms
* BFS, DFS, IDDFS and A* algorithms
* Algorithm comparison
* Search-tree construction
* Python modular programming
* GUI development

## Future Improvements

* Add more search algorithms.
* Add performance graphs and statistics.
* Support more than two jugs.
* Add customizable heuristics for A*.
* Export solution paths and comparison results.
* Add step-by-step animation of the solution.

## Author

**Bhagyashri**

## License

This project is intended for educational and academic purposes.
