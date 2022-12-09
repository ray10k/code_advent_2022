import pathlib as pl
from dataclasses import dataclass
from time import perf_counter as timer
from typing import Iterable, Iterator

# Typedef since I'll be using a lot of two-position tuples. May not be any more
# concise, but at least it's a little easier to read.
coordinate = tuple[int, int]

# Dict to quickly translate the directions into motion vectors.
DIRECTIONS: dict[str, coordinate] = {
    "U": (0, 1),
    "L": (-1, 0),
    "D": (0, -1),
    "R": (1, 0),
}
# Dictionary mapping the relative distance between two nodes, and the move that
# the second node should make.
STEPS: dict[coordinate, coordinate] = {
    (2, 2): (1, 1),
    (2, 1): (1, 1),
    (2, 0): (1, 0),
    (2, -1): (1, -1),
    (2, -2): (1, -1),
    (1, 2): (1, 1),
    (1, 1): (0, 0),
    (1, 0): (0, 0),
    (1, -1): (0, 0),
    (1, -2): (1, -1),
    (0, 2): (0, 1),
    (0, 1): (0, 0),
    (0, 0): (0, 0),
    (0, -1): (0, 0),
    (0, -2): (0, -1),
    (-1, 2): (-1, 1),
    (-1, 1): (0, 0),
    (-1, 0): (0, 0),
    (-1, -1): (0, 0),
    (-1, -2): (-1, -1),
    (-2, 2): (-1, 1),
    (-2, 1): (-1, 1),
    (-2, 0): (-1, 0),
    (-2, -1): (-1, -1),
    (-2, -2): (-1, -1),
}


@dataclass(frozen=True)
class Movement:
    """Class representing a single sequence of movements."""

    distance: int
    direction: str

    def step_iterator(self, initial_position: coordinate) -> Iterator[coordinate]:
        """Iterator that yields all the positions that are visited as part of this
        movement, excluding the initial position (since that one has to be
        known already.)"""
        dx, dy = DIRECTIONS[self.direction]
        x, y = initial_position
        return ((x + dx * s, y + dy * s) for s in range(1, self.distance + 1))


def coordinate_delta(origin: coordinate, other: coordinate) -> coordinate:
    """Returns a vector indicating the relative movement between the two given
    vectors."""
    return (other[0] - origin[0], other[1] - origin[1])


def move_tail(head: coordinate, tail: coordinate) -> coordinate:
    """Calculates the new position of the tail, based on the position of the
    head."""
    movement = coordinate_delta(tail, head)
    bump = STEPS[movement]
    return (tail[0] + bump[0], tail[1] + bump[1])


my_dir: pl.Path = pl.Path(__file__).parent
parsed_data: list[Movement] = list()
with open(my_dir / "input.txt") as input_file:
    for line in input_file:
        # Parsing is easy this time; each line has a letter, a space, and one or
        # more numbers. Just split on the space to get the info needed.
        direction, distance = line.strip().split(" ")
        parsed_data.append(Movement(int(distance), direction))


def sliding_window(iterable: Iterable[any], size=2):
    """Iterator that 'walks' over an iterable, `size` items at a time."""
    iterators = [iter(iterable[i:]) for i in range(size)]
    return zip(*iterators)


def star_one(data: list[Movement]) -> str:
    visited_spaces: set[coordinate] = {(0, 0)}
    tail_position = (0, 0)
    head_position = (0, 0)
    for instruction in data:
        for step in instruction.step_iterator(head_position):
            head_position = step
            tail_position = move_tail(head_position, tail_position)
            visited_spaces.add(tail_position)
    return str(len(visited_spaces))


def star_two(data: list[Movement]) -> str:
    visited_spaces: set[coordinate] = {(0, 0)}
    rope: list[coordinate] = [(0, 0)] * 10
    for instruction in data:
        for step in instruction.step_iterator(rope[0]):
            rope[0] = step
            for head, tail in sliding_window(range(10)):
                rope[tail] = move_tail(rope[head], rope[tail])
            visited_spaces.add(rope[9])
    return str(len(visited_spaces))


s1_start: float = timer()
first_star = star_one(parsed_data)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(parsed_data)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
