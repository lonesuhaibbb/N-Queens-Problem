def solve_n_queens(n):
    board = [-1] * n
    solutions = []

    def is_safe(row, col):
        for prev_row in range(row):
            prev_col = board[prev_row]

            if prev_col == col:
                return False

            if abs(prev_col - col) == abs(prev_row - row):
                return False

        return True

    def backtrack(row):
        if row == n:
            solutions.append(board.copy())
            return

        for col in range(n):
            if is_safe(row, col):
                board[row] = col
                backtrack(row + 1)
                board[row] = -1

    backtrack(0)
    return solutions


try:
    n = int(input("Enter the number of queens: "))

    if n < 1:
        print("Please enter a positive integer.")
    else:
        solutions = solve_n_queens(n)

        print(f"\nSolutions for {n}-Queens: {len(solutions)}")

        for solution in solutions:
            for col in solution:
                row = ["."] * n
                row[col] = "Q"
                print(" ".join(row))
            print()

except ValueError:
    print("Invalid input. Please enter an integer.")