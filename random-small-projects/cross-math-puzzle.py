"""Cross-math puzzle generator.

Grid layout (size=7, so 3 numbers per row/column):

    n  op  n  op  n  =  result
    op     op     op    op
    n  op  n  op  n  =  result
    op     op     op    op
    n  op  n  op  n  =  result
    =      =      =     =
    r  op  r  op  r  =  corner

Odd-indexed rows/cols are operators; even-indexed are numbers or results.
The second-to-last row/col is the "=" separator row/col.
The last row/col holds results.
"""

import random
import time
from dataclasses import dataclass, field
from typing import Optional

# ── Types ──────────────────────────────────────────────────────────────────────

Cell = Optional[int | str]
Grid = list[list[Cell]]

OPERATORS = ("+", "-", "x", "/")

# ── Arithmetic ─────────────────────────────────────────────────────────────────

def apply_op(a: int, op: str, b: int) -> int:
    match op:
        case "+": return a + b
        case "-": return a - b
        case "x": return a * b
        case "/": return a // b if b != 0 else 0
        case _: raise ValueError(f"Unknown operator: {op!r}")


def evaluate(numbers: list[int], operators: list[str]) -> int:
    """Evaluate a flat arithmetic expression respecting multiplication priority."""
    if len(numbers) == 1:
        return numbers[0]
    
    nums = list(numbers)
    ops = list(operators)

    # First pass: multiplication / division
    i = 0
    while i < len(ops):
        if ops[i] in ("x", "/"):
            nums[i] = apply_op(nums[i], ops[i], nums[i + 1])
            del nums[i + 1]
            del ops[i]
        else:
            i += 1

    # Second pass: addition / subtraction
    result = nums[0]
    for op, num in zip(ops, nums[1:]):
        result = apply_op(result, op, num)
    return result

# ── Random helpers ─────────────────────────────────────────────────────────────

def rand_number(lo: int = 1, hi: int = 20) -> int:
    return random.randint(lo, hi)

def rand_op() -> str:
    return random.choice(OPERATORS)

# ── Grid structure helpers ─────────────────────────────────────────────────────

@dataclass
class PuzzleLayout:
    """Precomputed index sets for a given grid size."""
    size: int
    sep: int = field(init=False)   # separator row/col index
    last: int = field(init=False)  # result row/col index

    def __post_init__(self) -> None:
        self.sep = self.size - 2
        self.last = self.size - 1

    def is_separator(self, i: int, j: int) -> bool:
        return i == self.sep or j == self.sep

    def is_number_cell(self, i: int, j: int) -> bool:
        return i % 2 == 0 and j % 2 == 0

    def is_h_operator(self, i: int, j: int) -> bool:
        return i % 2 == 0 and j % 2 == 1

    def is_v_operator(self, i: int, j: int) -> bool:
        return i % 2 == 1 and j % 2 == 0

    def row_numbers(self, grid: Grid, row: int) -> list[int]:
        return [grid[row][j] for j in range(0, self.sep, 2)]  # type: ignore[misc]

    def row_operators(self, grid: Grid, row: int) -> list[str]:
        return [grid[row][j] for j in range(1, self.sep, 2)]  # type: ignore[misc]

    def col_numbers(self, grid: Grid, col: int) -> list[int]:
        return [grid[i][col] for i in range(0, self.sep, 2)]  # type: ignore[misc]

    def col_operators(self, grid: Grid, col: int) -> list[str]:
        return [grid[i][col] for i in range(1, self.sep, 2)]  # type: ignore[misc]

# ── Puzzle generation ──────────────────────────────────────────────────────────

def _blank_grid(size: int) -> Grid:
    return [[None] * size for _ in range(size)]


def _fill_interior(grid: Grid, layout: PuzzleLayout) -> None:
    """Place random numbers and operators in the interior (non-result) cells."""
    sep, last = layout.sep, layout.last
    for i in range(last):
        for j in range(last):
            if i == sep or j == sep:
                # Separator row/col: "=" on even positions, None on odd
                grid[i][j] = "=" if (i == sep and j % 2 == 0) or (j == sep and i % 2 == 0) else None
            elif layout.is_number_cell(i, j):
                grid[i][j] = rand_number()
            elif layout.is_h_operator(i, j):
                grid[i][j] = rand_op()
            elif layout.is_v_operator(i, j):
                grid[i][j] = rand_op()
            # Odd/odd intersections stay None


def _compute_results(grid: Grid, layout: PuzzleLayout) -> None:
    """Fill the result column and row from the interior values."""
    sep, last = layout.sep, layout.last

    # Horizontal results → rightmost column
    for i in range(0, sep, 2):
        grid[i][last] = evaluate(layout.row_numbers(grid, i), layout.row_operators(grid, i))

    # Vertical results → bottom row
    for j in range(0, sep, 2):
        grid[last][j] = evaluate(layout.col_numbers(grid, j), layout.col_operators(grid, j))


def _fill_result_row_operators(grid: Grid, layout: PuzzleLayout) -> None:
    """Place random operators between the vertical results in the bottom row."""
    sep = layout.sep
    for j in range(1, sep, 2):
        grid[layout.last][j] = rand_op()


def _fill_result_col_operators(grid: Grid, layout: PuzzleLayout) -> bool:
    """
    Choose operators for the result column so that evaluating it top-to-bottom
    equals the bottom-row expression.  Returns False if no valid assignment exists.
    """
    sep, last = layout.sep, layout.last

    # Target: evaluate the bottom result row
    bottom_numbers   = layout.row_numbers(grid, last)
    bottom_operators = layout.row_operators(grid, last)
    target = evaluate(bottom_numbers, bottom_operators)

    # Result-column numbers (already computed)
    col_numbers = [grid[i][last] for i in range(0, sep, 2)]

    # We need to find operators for positions (1, last), (3, last), …
    op_rows = list(range(1, sep, 2))
    n_ops = len(op_rows)

    # Brute-force over all operator combinations (3^n_ops at most, typically ≤9)
    from itertools import product
    for ops in product(OPERATORS, repeat=n_ops):
        if evaluate(col_numbers, list(ops)) == target:  # type: ignore[arg-type]
            for row, op in zip(op_rows, ops):
                grid[row][last] = op
            grid[sep][last] = "="
            grid[last][sep] = "="
            grid[last][last] = target
            return True

    return False


def generate_puzzle(size: int = 7, max_attempts: int = 1_000) -> Grid:
    """
    Generate a cross-math puzzle grid of the given size.

    size must be odd and ≥ 5 (e.g. 5, 7, 9).
    Raises RuntimeError if no valid puzzle is found within max_attempts.
    """
    if size < 5 or size % 2 == 0:
        raise ValueError("size must be an odd integer ≥ 5")

    layout = PuzzleLayout(size)

    for _ in range(max_attempts):
        grid = _blank_grid(size)
        _fill_interior(grid, layout)
        _compute_results(grid, layout)
        _fill_result_row_operators(grid, layout)
        if _fill_result_col_operators(grid, layout):
            return grid

    raise RuntimeError(f"Could not generate a valid puzzle after {max_attempts} attempts")

# ── Display ────────────────────────────────────────────────────────────────────

def format_cell(cell: Cell) -> str:
    if cell is None:
        return "   "
    if isinstance(cell, int):
        return f"{cell:3d}"
    return f"  {cell}"


def display_puzzle(grid: Grid) -> None:
    for row in grid:
        print("  ".join(format_cell(c) for c in row))


# ── Batch generation with timing ───────────────────────────────────────────────

def generate_puzzles_with_timing(
    count: int = 10,
    size: int = 7,
    max_attempts: int = 1_000,
) -> None:
    """Generate `count` puzzles, print each one, then show a timing summary."""
    times: list[float] = []

    for i in range(1, count + 1):
        t_start = time.perf_counter()
        puzzle = generate_puzzle(size=size, max_attempts=max_attempts)
        t_end = time.perf_counter()

        elapsed = t_end - t_start
        times.append(elapsed)

        # display_puzzle(puzzle)
        
        if i % 1000 == 0:
            print(f"  Generated {i:,} puzzles...")

    # ── Summary ────────────────────────────────────────────────────────────────
    total   = sum(times)
    average = total / len(times)

    print(f"\n{'=' * 50}")
    print("  Timing Summary")
    print(f"{'=' * 50}")
    if count <= 100:
        print(f"  {'Puzzle':<10} {'Time (ms)':>12}")
        print(f"  {'-'*10} {'-'*12}")
        for idx, t in enumerate(times, start=1):
            print(f"  {idx:<10} {t * 1_000:>12.3f}")
        print(f"  {'-'*10} {'-'*12}")
    print(f"  {'Count':<10} {count:>12}")
    print(f"  {'Total':<10} {total * 1_000:>12.3f} ms")
    print(f"  {'Average':<10} {average * 1_000:>12.3f} ms")
    print(f"  {'Min':<10} {min(times) * 1_000:>12.3f} ms")
    print(f"  {'Max':<10} {max(times) * 1_000:>12.3f} ms")
    print(f"{'=' * 50}\n")


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    generate_puzzles_with_timing(count=1000000, size=5)