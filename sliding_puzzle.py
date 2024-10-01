"""
15-piece sliding puzzle

A puzzle configuration is represented as a Slider15 value -
  A tuple of 4 tuples, each containing 4 ints.

  The 15 pieces are represented by the numbers 1-15, and the blank space is
  represented by the number 0.  Therefore, each integer from 0-15 should appear exactly
  once in a given puzzle configuration.

The private functions, beginning with _, are used as helpers to implement the successors
   function.  You do not need to invoke them in your program.
"""

import time
import heapq

Slider15 = tuple[
    tuple[int, int, int, int],
    tuple[int, int, int, int],
    tuple[int, int, int, int],
    tuple[int, int, int, int],
]

## This is the target puzzle configuration for which a solver should search.
FINISHED_SLIDER = (
    (0, 1, 2, 3),
    (4, 5, 6, 7),
    (8, 9, 10, 11),
    (12, 13, 14, 15),
)


def print_slider15(slider: Slider15):
    """
    Print out the puzzle configuration using latin letters to represent the pieces.

    :param slider: The puzzle configuration to print
    """
    chars = " ABCDEFGHIJKLMNO"
    for row in slider:
        for val in row:
            print(chars[val], end=" ")
        print()
    print()


def _find_zero(slider: Slider15) -> tuple[int, int]:
    """
    Find the row and column where the blank space is in the puzzle.

    :param slider: A puzzle configuration
    :return: The row number and column number of the blank space.
    """
    for i, row in enumerate(slider):
        for j, val in enumerate(row):
            if val == 0:
                return i, j


def _slide_down_to(r: int, c: int, slider: Slider15) -> Slider15:
    r0 = tuple(0 if i == c else x for i, x in enumerate(slider[0])) if r == 1 else slider[0]
    r1 = tuple(slider[0][i] if i == c else x for i, x in enumerate(slider[1])) if r == 1 else tuple(
        0 if i == c else x for i, x in enumerate(slider[1])) if r == 2 else slider[1]
    r2 = tuple(slider[1][i] if i == c else x for i, x in enumerate(slider[2])) if r == 2 else tuple(
        0 if i == c else x for i, x in enumerate(slider[2])) if r == 3 else slider[2]
    r3 = tuple(slider[2][i] if i == c else x for i, x in enumerate(slider[3])) if r == 3 else slider[3]
    return r0, r1, r2, r3


def _slide_up_to(r: int, c: int, slider: Slider15) -> Slider15:
    r0 = tuple(slider[1][i] if i == c else x for i, x in enumerate(slider[0])) if r == 0 else slider[0]
    r1 = tuple(0 if i == c else x for i, x in enumerate(slider[1])) if r == 0 else tuple(
        slider[2][i] if i == c else x for i, x in enumerate(slider[1])) if r == 1 else slider[1]
    r2 = tuple(0 if i == c else x for i, x in enumerate(slider[2])) if r == 1 else tuple(
        slider[3][i] if i == c else x for i, x in enumerate(slider[2])) if r == 2 else slider[2]
    r3 = tuple(0 if i == c else x for i, x in enumerate(slider[3])) if r == 2 else slider[3]
    return r0, r1, r2, r3


def _slide_right_in_row_to(col: int, row: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    a, b, c, d = row
    return (
        0 if col == 1 else a,
        a if col == 1 else 0 if col == 2 else b,
        b if col == 2 else 0 if col == 3 else c,
        c if col == 3 else d
    )


def _slide_left_in_row_to(col: int, row: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    a, b, c, d = row
    return (
        b if col == 0 else a,
        c if col == 1 else 0 if col == 0 else b,
        d if col == 2 else 0 if col == 1 else c,
        0 if col == 2 else d
    )


def _slide_right_to(r: int, c: int, slider: Slider15) -> Slider15:
    r0, r1, r2, r3 = slider
    return (
        _slide_right_in_row_to(c, r0) if r == 0 else r0,
        _slide_right_in_row_to(c, r1) if r == 1 else r1,
        _slide_right_in_row_to(c, r2) if r == 2 else r2,
        _slide_right_in_row_to(c, r3) if r == 3 else r3
    )


def _slide_left_to(r: int, c: int, slider: Slider15) -> Slider15:
    r0, r1, r2, r3 = slider
    return (
        _slide_left_in_row_to(c, r0) if r == 0 else r0,
        _slide_left_in_row_to(c, r1) if r == 1 else r1,
        _slide_left_in_row_to(c, r2) if r == 2 else r2,
        _slide_left_in_row_to(c, r3) if r == 3 else r3
    )


def successors_of_slider15(slider: Slider15) -> list[Slider15]:
    """
    Return the list of all successor states of the given puzzle configuration.
    """
    r, c = _find_zero(slider)
    succs = []
    if r > 0:
        succs.append(_slide_down_to(r, c, slider))
    if r < 3:
        succs.append(_slide_up_to(r, c, slider))
    if c > 0:
        succs.append(_slide_right_to(r, c, slider))
    if c < 3:
        succs.append(_slide_left_to(r, c, slider))
    return succs


##given a Slider15, returns the number of misplaced tiles.
def misplaced_tiles(state, goal):
    misplaced_count = 0
    for i in range(4):
        for j in range(4):
            if state[i][j] != 0 and state[i][j] != goal[i][j]:
                misplaced_count += 1
    return misplaced_count


##second heuristic function: Sum of Manhattan distance
def manhattan_distance(state, goal):
    distance = 0
    for i in range(4):
        for j in range(4):
            if state[i][j] != 0:
                for x in range(4):
                    for y in range(4):
                        if goal[x][y] == state[i][j]:
                            distance += abs(i - x) + abs(j - y)
    return distance


##function implementing the A* algorithm.
##        - Inputs: a Slider15 and a heuristic function,
##        - Outputs: a list of Slider15 values representing the path
##                     from the initial configuration to the target configuration
def a_star(initial_state, goal_state, heuristic_function):
    fringe = []
    heapq.heappush(fringe, (0, initial_state))  # (priority, state)

    cost_so_far = {str(initial_state): 0}  # Cost to reach each state
    came_from = {str(initial_state): None}  # To track the path

    while fringe:
        current_cost, current_state = heapq.heappop(fringe)

        if current_state == goal_state:
            path = []
            while current_state:
                path.append(current_state)
                current_state = came_from[str(current_state)]
            return path[::-1]  #reversed to get the path from start to goal

        for neighbor in successors_of_slider15(current_state):
            new_cost = cost_so_far[str(current_state)] + 1
            neighbor_str = str(neighbor)

            if neighbor_str not in cost_so_far or new_cost < cost_so_far[neighbor_str]:
                cost_so_far[neighbor_str] = new_cost
                priority = new_cost + heuristic_function(neighbor, goal_state)
                heapq.heappush(fringe, (priority, neighbor))
                came_from[neighbor_str] = current_state

    return None  #in case no solution


if __name__ == "__main__":

    ## This is the initial puzzle configuration

    puzzle = (
        (9, 1, 5, 3),
        (4, 6, 2, 7),
        (8, 12, 15, 0),
        (14, 13, 11, 10),
    )

    #calculated misplaced tiles
    misplaced_count = misplaced_tiles(puzzle, FINISHED_SLIDER)
    print(f"Number of Misplaced Tiles: {misplaced_count}")

    print("\nSolving with misplaced tiles heuristic:")
    start_time = time.time()
    solution = a_star(puzzle, FINISHED_SLIDER, misplaced_tiles)
    end_time = time.time()
    print(f"Solution found in {len(solution) - 1} moves")
    print(f"Time taken: {end_time - start_time:.4f} seconds\n")
    for step in solution:
        print_slider15(step)

    total_distance = manhattan_distance(puzzle, FINISHED_SLIDER)
    print(f"\nTotal Manhattan Distance: {total_distance}")

    print("\nSolving with Manhattan distance heuristic:")
    start_time = time.time()
    solution = a_star(puzzle, FINISHED_SLIDER, manhattan_distance)
    end_time = time.time()
    print(f"Solution found in {len(solution) - 1} moves")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    for step in solution:
        print_slider15(step)
