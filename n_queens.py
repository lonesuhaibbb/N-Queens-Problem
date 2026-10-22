BOARD_SIZE = 8


def solve_n_queens(n):
    board = [-1] * BOARD_SIZE
    solutions = []

    def is_safe(row, col):
        for prev_row in range(row):
            prev_col = board[prev_row]

            if prev_col == col:
                return False

            if abs(prev_col - col) == abs(prev_row - row):
                return False

        return True

    def backtrack(row, queens_left):
        if queens_left == 0:
            solutions.append(board.copy())
            return

        if row == BOARD_SIZE:
            return

        if BOARD_SIZE - row < queens_left:
            return

        # Try leaving this row empty.
        backtrack(row + 1, queens_left)

        # Try placing a queen in each column.
        for col in range(BOARD_SIZE):
            if is_safe(row, col):
                board[row] = col
                backtrack(row + 1, queens_left - 1)
                board[row] = -1

    backtrack(0, n)
    return solutions


def display_board(solution):
    for col in solution:
        row = ["."] * BOARD_SIZE

        if col != -1:
            row[col] = "Q"

        print(" ".join(row))

    print()


def main():
    print("N-Queens Solver")
    print("Chessboard: 8 x 8")
    print("Maximum non-attacking queens: 8")

    try:
        n = int(input("Enter the number of queens (1-16): "))

        if n < 1 or n > 16:
            print("Please enter a number between 1 and 16.")
            return

        if n > BOARD_SIZE:
            print(f"\nNo solution: an 8x8 board can hold at most 8")
            print("queens without attacking each other.")
            print("Number of valid arrangements: 0")
            return

        solutions = solve_n_queens(n)

        print(f"\nQueens: {n}")
        print(f"Total valid arrangements: {len(solutions)}")

        if solutions:
            print("\nFirst valid arrangement:")
            display_board(solutions[0])
        else:
            print("No valid arrangement exists.")

    except ValueError:
        print("Invalid input. Please enter an integer.")


if __name__ == "__main__":
    main()