
import tkinter as tk
from tkinter import messagebox

BOARD_SIZE = 8

# Chessboard colors
LIGHT_SQUARE = "#F0D9B5"
DARK_SQUARE = "#779556"
QUEEN_COLOR = "#202020"


def solve_n_queens(n):
    """
    Count every valid arrangement of n non-attacking queens
    on an 8x8 board and save the first valid arrangement.
    """
    board = [-1] * BOARD_SIZE
    total_solutions = 0
    first_solution = None

    def backtrack(row, queens_left):
        nonlocal total_solutions, first_solution

        if queens_left == 0:
            total_solutions += 1

            if first_solution is None:
                first_solution = board.copy()

            return

        if row == BOARD_SIZE:
            return

        if BOARD_SIZE - row < queens_left:
            return

        # Option 1: Leave this row empty.
        board[row] = -1
        backtrack(row + 1, queens_left)

        # Option 2: Place a queen in this row.
        for col in range(BOARD_SIZE):
            safe = True

            for previous_row in range(row):
                previous_col = board[previous_row]

                # Ignore rows without queens.
                if previous_col == -1:
                    continue

                # Queens cannot share a column or diagonal.
                if previous_col == col:
                    safe = False
                    break

                if abs(previous_col - col) == abs(previous_row - row):
                    safe = False
                    break

            if safe:
                board[row] = col
                backtrack(row + 1, queens_left - 1)
                board[row] = -1

        board[row] = -1

    if 1 <= n <= BOARD_SIZE:
        backtrack(0, n)

    return total_solutions, first_solution


class NQueensApp:
    def __init__(self, root):
        self.root = root
        self.root.title("N-Queens Visual Solver")
        self.root.resizable(False, False)
        self.root.configure(bg="#F4F5F7")

        self.square_size = 64
        self.board_pixels = BOARD_SIZE * self.square_size

        heading = tk.Label(
            root,
            text="N-QUEENS VISUAL SOLVER",
            font=("Segoe UI", 19, "bold"),
            bg="#F4F5F7",
            fg="#243447"
        )
        heading.pack(pady=(15, 3))

        subtitle = tk.Label(
            root,
            text="Place queens without allowing them to attack each other",
            font=("Segoe UI", 9),
            bg="#F4F5F7",
            fg="#526170"
        )
        subtitle.pack(pady=(0, 12))

        controls = tk.Frame(root, bg="#F4F5F7")
        controls.pack(pady=5)

        tk.Label(
            controls,
            text="Number of queens (1–16):",
            font=("Segoe UI", 10),
            bg="#F4F5F7"
        ).grid(row=0, column=0, padx=5)

        self.queen_input = tk.Spinbox(
            controls,
            from_=1,
            to=16,
            width=5,
            font=("Segoe UI", 11),
            justify="center"
        )
        self.queen_input.delete(0, tk.END)
        self.queen_input.insert(0, "4")
        self.queen_input.grid(row=0, column=1, padx=5)

        self.solve_button = tk.Button(
            controls,
            text="Find Solution",
            command=self.find_solution,
            bg="#286749",
            fg="white",
            activebackground="#1F5038",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2"
        )
        self.solve_button.grid(row=0, column=2, padx=5)

        self.canvas = tk.Canvas(
            root,
            width=self.board_pixels,
            height=self.board_pixels,
            highlightthickness=3,
            highlightbackground="#344638"
        )
        self.canvas.pack(pady=12)

        self.result_label = tk.Label(
            root,
            text="Choose a number and click Find Solution.",
            font=("Segoe UI", 10, "bold"),
            bg="#F4F5F7",
            fg="#243447",
            wraplength=500
        )
        self.result_label.pack(pady=(2, 5))

        self.detail_label = tk.Label(
            root,
            text="The board will display the first valid arrangement.",
            font=("Segoe UI", 9),
            bg="#F4F5F7",
            fg="#526170"
        )
        self.detail_label.pack(pady=(0, 8))

        bottom_buttons = tk.Frame(root, bg="#F4F5F7")
        bottom_buttons.pack(pady=(0, 15))

        tk.Button(
            bottom_buttons,
            text="Clear Board",
            command=self.clear_board,
            font=("Segoe UI", 10),
            padx=12,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            bottom_buttons,
            text="Exit",
            command=root.destroy,
            font=("Segoe UI", 10),
            padx=12,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

        self.draw_board()

    def draw_board(self, solution=None):
        """Draw the chessboard and optionally place queens."""
        self.canvas.delete("all")

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                color = (
                    LIGHT_SQUARE
                    if (row + col) % 2 == 0
                    else DARK_SQUARE
                )

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=color
                )

                # Display row and column coordinates.
                if col == 0:
                    self.canvas.create_text(
                        x1 + 7,
                        y1 + 7,
                        text=str(8 - row),
                        fill="#344638",
                        font=("Segoe UI", 8, "bold"),
                        anchor="nw"
                    )

                if row == 7:
                    self.canvas.create_text(
                        x2 - 7,
                        y2 - 6,
                        text="abcdefgh"[col],
                        fill="#344638",
                        font=("Segoe UI", 8, "bold"),
                        anchor="se"
                    )

                # Draw a queen when this square contains one.
                if solution is not None and solution[row] == col:
                    center_x = x1 + self.square_size // 2
                    center_y = y1 + self.square_size // 2

                    self.canvas.create_text(
                        center_x,
                        center_y,
                        text="♛",
                        font=("Segoe UI Symbol", 43),
                        fill=QUEEN_COLOR
                    )

    def find_solution(self):
        """Validate input, calculate solutions and display the result."""
        try:
            n = int(self.queen_input.get())

            if not 1 <= n <= 16:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Please enter a whole number between 1 and 16."
            )
            return

        self.solve_button.config(state=tk.DISABLED)
        self.result_label.config(text="Calculating arrangements...")
        self.root.update_idletasks()

        try:
            if n > BOARD_SIZE:
                total, solution = 0, None
            else:
                total, solution = solve_n_queens(n)

            self.draw_board(solution)

            if total == 0:
                self.result_label.config(
                    text=f"No valid arrangements for {n} queens."
                )

                self.detail_label.config(
                    text="An 8x8 board can hold at most 8 "
                         "non-attacking queens."
                )
            else:
                self.result_label.config(
                    text=f"Total valid arrangements: {total:,}"
                )

                self.detail_label.config(
                    text=f"Displaying one valid arrangement "
                         f"with {n} queen(s)."
                )

        finally:
            self.solve_button.config(state=tk.NORMAL)

    def clear_board(self):
        """Remove the queens and reset the result text."""
        self.draw_board()
        self.result_label.config(
            text="Board cleared. Choose a number to continue."
        )
        self.detail_label.config(
            text="The board is ready for another calculation."
        )


if __name__ == "__main__":
    window = tk.Tk()
    app = NQueensApp(window)
    window.mainloop()