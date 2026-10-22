import tkinter as tk
from tkinter import ttk
from functools import lru_cache

SIZE = 8

LIGHT = "#F0D9B5"
DARK = "#779556"
RED = "#E87575"
GREEN = "#65B887"
BACKGROUND = "#F4F5F7"
TEXT = "#263445"


def count_arrangements(n):
    """Count all non-attacking arrangements on an 8x8 board."""
    if n < 1 or n > SIZE:
        return 0

    total = 0

    def search(row, placed, columns, diag1, diag2):
        nonlocal total

        if placed == n:
            total += 1
            return

        if row == SIZE or SIZE - row < n - placed:
            return

        # Option 1: leave this row empty.
        search(row + 1, placed, columns, diag1, diag2)

        # Option 2: place a queen in this row.
        for col in range(SIZE):
            c_bit = 1 << col
            d1_bit = 1 << (row - col + SIZE - 1)
            d2_bit = 1 << (row + col)

            if columns & c_bit:
                continue
            if diag1 & d1_bit:
                continue
            if diag2 & d2_bit:
                continue

            search(
                row + 1,
                placed + 1,
                columns | c_bit,
                diag1 | d1_bit,
                diag2 | d2_bit,
            )

    search(0, 0, 0, 0, 0)
    return total


def find_first_solution(n):
    """Find one solution and return the search events for animation."""
    queens = [-1] * SIZE
    events = []

    def search(row, placed):
        if placed == n:
            events.append(("solution", row - 1, -1, queens.copy()))
            return True

        if row >= SIZE or SIZE - row < n - placed:
            return False

        # Try placing a queen in each column.
        for col in range(SIZE):
            events.append(("try", row, col, queens.copy()))

            safe = True

            for r, c in enumerate(queens):
                if c == -1:
                    continue

                if c == col or abs(r - row) == abs(c - col):
                    safe = False
                    break

            if not safe:
                events.append(("conflict", row, col, queens.copy()))
                continue

            queens[row] = col
            events.append(("place", row, col, queens.copy()))

            if search(row + 1, placed + 1):
                return True

            queens[row] = -1
            events.append(("backtrack", row, col, queens.copy()))

        # This row may remain empty when fewer queens are requested.
        events.append(("skip", row, -1, queens.copy()))

        if search(row + 1, placed):
            return True

        return False

    if search(0, 0):
        return events

    return []


class NQueensVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("N-Queens | Animated Visualizer")
        self.root.configure(bg=BACKGROUND)
        self.root.resizable(False, False)

        self.cell = 64
        self.queens = [-1] * SIZE
        self.events = []
        self.event_index = 0
        self.after_id = None
        self.running = False
        self.paused = False

        self.total_arrangements = 0
        self.attempts = 0

        tk.Label(
            root,
            text="N-QUEENS VISUALIZER",
            font=("Segoe UI", 19, "bold"),
            bg=BACKGROUND,
            fg=TEXT,
        ).pack(pady=(12, 3))

        tk.Label(
            root,
            text="Count every arrangement, then animate only one solution",
            font=("Segoe UI", 9),
            bg=BACKGROUND,
            fg="#526170",
        ).pack(pady=(0, 10))

        controls = tk.Frame(root, bg=BACKGROUND)
        controls.pack()

        tk.Label(
            controls,
            text="Queens (1–16):",
            bg=BACKGROUND,
        ).grid(row=0, column=0, padx=4)

        self.number = ttk.Combobox(
            controls,
            values=list(range(1, 17)),
            width=5,
            state="readonly",
            justify="center",
        )
        self.number.set("4")
        self.number.grid(row=0, column=1, padx=4)

        tk.Label(
            controls,
            text="Speed:",
            bg=BACKGROUND,
        ).grid(row=0, column=2, padx=(12, 3))

        self.speed = ttk.Combobox(
            controls,
            values=["Slow", "Normal", "Fast"],
            width=8,
            state="readonly",
        )
        self.speed.set("Fast")
        self.speed.grid(row=0, column=3, padx=4)

        buttons = tk.Frame(root, bg=BACKGROUND)
        buttons.pack(pady=8)

        self.start_button = tk.Button(
            buttons,
            text="▶ Count & Animate",
            command=self.start,
            bg="#286749",
            fg="white",
            relief="flat",
            padx=12,
            pady=6,
        )
        self.start_button.pack(side="left", padx=4)

        self.pause_button = tk.Button(
            buttons,
            text="Ⅱ Pause",
            command=self.pause,
            padx=12,
            pady=6,
        )
        self.pause_button.pack(side="left", padx=4)

        tk.Button(
            buttons,
            text="↻ Reset",
            command=self.reset,
            padx=12,
            pady=6,
        ).pack(side="left", padx=4)

        self.canvas = tk.Canvas(
            root,
            width=SIZE * self.cell,
            height=SIZE * self.cell,
            highlightthickness=3,
            highlightbackground="#344638",
        )
        self.canvas.pack(pady=8)

        self.result = tk.Label(
            root,
            text="Choose the number of queens and click Count & Animate.",
            bg=BACKGROUND,
            fg=TEXT,
            font=("Segoe UI", 10, "bold"),
            wraplength=520,
        )
        self.result.pack(pady=3)

        self.status = tk.Label(
            root,
            text="Ready.",
            bg=BACKGROUND,
            fg="#526170",
            font=("Segoe UI", 9),
        )
        self.status.pack(pady=3)

        self.stats = tk.Label(
            root,
            text="Attempts: 0",
            bg=BACKGROUND,
            fg="#526170",
        )
        self.stats.pack(pady=(0, 4))

        tk.Label(
            root,
            text="♛ Queen     Red: attacked square     Green: active row",
            bg=BACKGROUND,
            fg=TEXT,
        ).pack(pady=(2, 12))

        self.draw_board()

    def delay(self):
        return {
            "Slow": 220,
            "Normal": 65,
            "Fast": 20,
        }.get(self.speed.get(), 20)

    def attacked(self, row, col):
        for r, c in enumerate(self.queens):
            if c == -1:
                continue

            if r == row:
                continue

            if c == col or abs(r - row) == abs(c - col):
                return True

        return False

    def draw_board(self, active_row=-1, checked_col=-1):
        self.canvas.delete("all")

        for row in range(SIZE):
            for col in range(SIZE):
                x1 = col * self.cell
                y1 = row * self.cell
                x2 = x1 + self.cell
                y2 = y1 + self.cell

                color = LIGHT if (row + col) % 2 == 0 else DARK

                if row == active_row:
                    color = GREEN

                if (
                    row == active_row
                    and col == checked_col
                    and self.attacked(row, col)
                ):
                    color = RED

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=color,
                )

                if col == 0:
                    self.canvas.create_text(
                        x1 + 7, y1 + 7,
                        text=str(8 - row),
                        anchor="nw",
                        fill="#243424",
                        font=("Segoe UI", 8, "bold"),
                    )

                if row == 7:
                    self.canvas.create_text(
                        x2 - 7, y2 - 6,
                        text="abcdefgh"[col],
                        anchor="se",
                        fill="#243424",
                        font=("Segoe UI", 8, "bold"),
                    )

                if self.queens[row] == col:
                    self.canvas.create_text(
                        x1 + self.cell // 2,
                        y1 + self.cell // 2,
                        text="♛",
                        font=("Segoe UI Symbol", 43),
                        fill="#202020",
                    )

    def start(self):
        if self.running:
            return

        n = int(self.number.get())

        self.reset(keep_selection=True)

        if n > SIZE:
            self.result.config(
                text="Total valid arrangements: 0"
            )
            self.status.config(
                text="No solution: an 8x8 board holds at most "
                     "8 non-attacking queens."
            )
            return

        self.running = True
        self.number.config(state="disabled")
        self.start_button.config(state="disabled")

        self.result.config(text="Counting all valid arrangements...")
        self.status.config(text="Calculating the total...")

        # Count first, then generate only the first solution's animation.
        self.root.after(10, lambda: self.calculate(n))

    def calculate(self, n):
        if not self.running:
            return

        self.total_arrangements = count_arrangements(n)

        self.result.config(
            text=f"Total valid arrangements: {self.total_arrangements:,}"
        )

        self.events = find_first_solution(n)
        self.event_index = 0
        self.attempts = 0
        self.queens = [-1] * SIZE

        if not self.events:
            self.finish()
            return

        self.status.config(
            text="Now animating the search for one solution..."
        )

        self.animate()

    def animate(self):
        if not self.running or self.paused:
            return

        # Process several events per frame in fast mode.
        batch_size = {
            "Slow": 1,
            "Normal": 3,
            "Fast": 6,
        }.get(self.speed.get(), 6)

        for _ in range(batch_size):
            if self.event_index >= len(self.events):
                self.finish()
                return

            event, row, col, board = self.events[self.event_index]
            self.event_index += 1
            self.queens = board.copy()

            if event == "try":
                self.attempts += 1
                self.status.config(
                    text=f"Testing row {row + 1}, column {col + 1}..."
                )
                self.draw_board(row, col)

            elif event == "conflict":
                self.status.config(
                    text=f"Conflict at row {row + 1}, column {col + 1}."
                )
                self.draw_board(row, col)

            elif event == "place":
                self.status.config(
                    text=f"Queen placed at row {row + 1}, column {col + 1}."
                )
                self.draw_board(row)

            elif event == "backtrack":
                self.status.config(
                    text=f"Backtracking from row {row + 1}..."
                )
                self.draw_board(row)

            elif event == "skip":
                self.status.config(
                    text=f"Trying another row after row {row + 1}."
                )
                self.draw_board(row)

            elif event == "solution":
                self.status.config(
                    text="A valid arrangement has been found!"
                )
                self.draw_board()

                self.stats.config(
                    text=f"Search attempts: {self.attempts:,}"
                )

                self.finish()
                return

        self.stats.config(
            text=f"Animation steps: {self.event_index:,}"
        )

        self.after_id = self.root.after(self.delay(), self.animate)

    def finish(self):
        self.running = False
        self.paused = False

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.number.config(state="readonly")
        self.start_button.config(state="normal")
        self.pause_button.config(text="Ⅱ Pause")

        # Leave the first valid arrangement visible.
        self.draw_board()

        self.status.config(
            text="Finished: displayed one valid arrangement."
        )
        self.stats.config(
            text=f"Search attempts: {self.attempts:,}"
        )

    def pause(self):
        if not self.running:
            return

        self.paused = not self.paused

        if self.paused:
            if self.after_id is not None:
                self.root.after_cancel(self.after_id)
                self.after_id = None

            self.pause_button.config(text="▶ Resume")
            self.status.config(text="Animation paused.")
        else:
            self.pause_button.config(text="Ⅱ Pause")
            self.animate()

    def reset(self, keep_selection=False):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.running = False
        self.paused = False
        self.events = []
        self.event_index = 0
        self.queens = [-1] * SIZE
        self.attempts = 0
        self.total_arrangements = 0

        self.number.config(state="readonly")
        self.start_button.config(state="normal")
        self.pause_button.config(text="Ⅱ Pause")

        self.draw_board()
        self.result.config(
            text="Choose the number of queens and click Count & Animate."
        )
        self.status.config(text="Ready.")
        self.stats.config(text="Attempts: 0")


if __name__ == "__main__":
    root = tk.Tk()
    app = NQueensVisualizer(root)
    root.mainloop()