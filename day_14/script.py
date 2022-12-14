from collections import namedtuple
import pathlib as pl
from time import perf_counter as timer
import re
from typing import Iterator

# Save walls (and settled sand) as a list-of-sets. Index in list is vertical
# value, each set contains the horizontal coordinates.
Solids = list[set[int]]
Point = namedtuple("Point", "x y")


class IntegerSet(set):
    """Spoofed "set" that says it contains *all* integers."""

    def __contains__(self, __o: object) -> bool:
        return isinstance(__o, int)


my_dir: pl.Path = pl.Path(__file__).parent
parsed_data = None
with open(my_dir / "input.txt") as input_file:
    parsed_data = [line.strip() for line in input_file]


def sliding_window(iterable, count):
    iterators = [iterable[i:] for i in range(count)]
    return zip(*iterators)


def parse_solids(data: list[str]) -> Solids:
    all_points = set()
    point_patt = re.compile(r"(\d+),(\d+)")
    for line in data:
        # Each line has at least two and at most infinity coordinates.
        points = point_patt.findall(line)
        for start, end in sliding_window(points, 2):
            a: Point = Point(int(start[0]), int(start[1]))
            b: Point = Point(int(end[0]), int(end[1]))
            all_points.update(line_iterator(a, b))
    height = max(all_points, key=lambda pt: pt.y)
    retval: list[set[int]] = [set() for _ in range(height.y + 1)]
    for point in all_points:
        retval[point.y].add(point.x)
    return retval


def print_sand(walls: Solids, sands: Solids) -> None:
    height = len(walls)
    left = min(sands[height - 2])
    right = max(sands[height - 2])
    print(f"Visible height: {height}. Visible width:{left}-{right}")
    for y, (wall, sand) in enumerate(zip(walls, sands)):
        line = ">"
        for x in range(left - 1, right + 2):
            if x in wall:
                line += "#"
            elif x in sand:
                line += "O"
            elif y == 0 and x == 500:
                line += "+"
            else:
                line += " "
        print(line, "<", sep="")


def line_iterator(start: Point, end: Point) -> Iterator[Point]:
    if start.x == end.x:
        x = start.x
        y_range = range(min(start.y, end.y), max(start.y, end.y) + 1)
        return (Point(x, y) for y in y_range)
    y = start.y
    x_range = range(min(start.x, end.x), max(start.x, end.x) + 1)
    return (Point(x, y) for x in x_range)


def do_tick(initial_state: Solids, drop_point: Point = Point(500, 0)) -> bool:
    x, y = drop_point
    if x in initial_state[0]:
        return False
    for y, layer in enumerate(initial_state):
        if y > len(initial_state):
            return False
        if x not in layer:
            y += 1
            continue
        if x - 1 not in layer:
            y += 1
            x -= 1
            continue
        if x + 1 not in layer:
            y += 1
            x += 1
            continue
        initial_state[y - 1].add(x)
        return True


def star_one(data: list[str]) -> str:
    walls = parse_solids(data)
    sand = parse_solids(data)
    sand_dropped: int = 0
    while do_tick(sand):
        sand_dropped += 1
    print_sand(walls, sand)
    return str(sand_dropped)


def star_two(data: list[str]) -> str:
    solids = parse_solids(data)
    solids.append(set())
    solids.append(IntegerSet())
    walls = parse_solids(data)
    walls.append(set())
    walls.append(IntegerSet())
    sand_dropped: int = 0
    while do_tick(solids):
        sand_dropped += 1
    print_sand(walls, solids)
    return str(sand_dropped)


s1_start: float = timer()
first_star = star_one(parsed_data)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(parsed_data)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
