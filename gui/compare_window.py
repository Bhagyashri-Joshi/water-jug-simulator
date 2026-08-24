"""
gui/compare_window.py
---------------------
Popup window showing a side-by-side comparison of all 4 algorithms.
"""
import tkinter as tk
from tkinter import ttk
import time

from algorithms.bfs   import solve_bfs
from algorithms.dfs   import solve_dfs
from algorithms.iddfs import solve_iddfs
from algorithms.astar import solve_astar

BG   = "#1A2B3C"
FG   = "#E8EFF6"
ACCENT = "#4A9EE0"

SOLVERS = [
    ('BFS',   solve_bfs),
    ('DFS',   solve_dfs),
    ('IDDFS', solve_iddfs),
    ('A*',    solve_astar),
]

class CompareWindow(tk.Toplevel):
    def __init__(self, parent, cap1, cap2, goal):
        super().__init__(parent)
        self.title("Algorithm Comparison")
        self.configure(bg=BG)
        self.resizable(False, False)

        tk.Label(self, text=f"Comparing all algorithms  |  Jug1={cap1}L  Jug2={cap2}L  Target={goal}L",
                 bg=BG, fg=ACCENT, font=("Arial", 11, "bold")).pack(pady=10, padx=16)

        cols = ('Algorithm', 'Solution Steps', 'Nodes Expanded', 'Optimal?', 'Time (ms)')
        tree = ttk.Treeview(self, columns=cols, show='headings', height=5)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=130, anchor='center')

        style = ttk.Style()
        style.configure("Treeview", background="#0F1923", foreground=FG,
                        fieldbackground="#0F1923", rowheight=28,
                        font=("Courier New", 10))
        style.configure("Treeview.Heading", background="#243447", foreground=ACCENT,
                        font=("Arial", 10, "bold"))

        results = []
        for name, solver in SOLVERS:
            t0 = time.perf_counter()
            r  = solver(cap1, cap2, goal)
            elapsed = (time.perf_counter() - t0) * 1000
            sol_len = len(r['solution']) - 1 if r['found'] else 'N/A'
            results.append((name, sol_len, r['steps'], r['found'], elapsed))

        # Find best solution length and fewest nodes (among found solutions)
        found_results = [r for r in results if r[4]]  # r[3]=found
        best_len  = min((r[1] for r in results if r[1] != 'N/A'), default=None)
        best_nodes = min((r[2] for r in results), default=None)

        tree.tag_configure('best',   background='#0D2B1A', foreground='#2ECC71')
        tree.tag_configure('normal', background='#0F1923', foreground=FG)
        tree.tag_configure('nofind', background='#2B0F0F', foreground='#E74C3C')

        for name, sol_len, nodes, found, elapsed in results:
            tag = 'nofind' if not found else ('best' if sol_len == best_len else 'normal')
            optimal = '✅ Yes' if found and sol_len == best_len else ('No' if found else '—')
            tree.insert('', tk.END,
                        values=(name,
                                sol_len if found else '—',
                                nodes,
                                optimal,
                                f"{elapsed:.2f}"),
                        tags=(tag,))

        tree.pack(padx=16, pady=8)

        tk.Label(self, text="★ Green = optimal solution (fewest steps)",
                 bg=BG, fg='#2ECC71', font=("Arial", 8)).pack()
        tk.Button(self, text="Close", command=self.destroy,
                  bg="#C0392B", fg="white", font=("Arial", 10, "bold"),
                  relief=tk.FLAT, padx=20, pady=4).pack(pady=10)

        self.transient(parent)
        self.grab_set()