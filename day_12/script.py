import pathlib as pl
from dataclasses import dataclass, field
from time import perf_counter as timer
import heapq as hq
from collections import defaultdict

Coordinate = tuple[int, int]
ALPHABET = "abcdefghijklmnopqrstuvwxyz"
CLEANUP = {"S": "a", "E": "z"}


@dataclass(slots=True, order=True)
class NavNode:
    distance: int = 0
    position: Coordinate = field(default=(0, 0), compare=False)


my_dir: pl.Path = pl.Path(__file__).parent
parsed_data: list[str] = list()
with open(my_dir / "input.txt") as input_file:
    parsed_data = [line.strip() for line in input_file]

# Note to self: (0,0) is top-left.
print(f"Field size WxH: {len(parsed_data[0])}x{len(parsed_data)}")
print(*parsed_data, sep="\n")


def initial_coordinates(data: list[str]) -> tuple[Coordinate, Coordinate]:
    start_coord = None
    end_coord = None
    for y, line in enumerate(data):
        for x, char in enumerate(line):
            if char == "S":
                start_coord = (x, y)
            if char == "E":
                end_coord = (x, y)
        if start_coord is not None and end_coord is not None:
            break
    return start_coord, end_coord


def step_delta(map_data: list[str], start: Coordinate, end: Coordinate) -> int:
    xa, ya = start
    xb, yb = end
    height_start = map_data[ya][xa]
    height_end = map_data[yb][xb]
    height_start = CLEANUP.get(height_start, height_start)
    height_end = CLEANUP.get(height_end, height_end)
    height_start = ALPHABET.index(height_start)
    height_end = ALPHABET.index(height_end)
    return height_end - height_start


def distance(start: Coordinate, end: Coordinate) -> int:
    dx = abs(start[0] - end[0])
    dy = abs(start[1] - end[1])
    return dx + dy


def adjacent_coords(
    center: Coordinate, far_corner: Coordinate
) -> tuple[Coordinate, ...]:
    retval: list[Coordinate] = []
    x, y = center
    up = x, y - 1
    down = x, y + 1
    left = x - 1, y
    right = x + 1, y
    if x > 0:
        retval.append(left)
    if x < far_corner[0]:
        retval.append(right)
    if y > 0:
        retval.append(up)
    if y < far_corner[1]:
        retval.append(down)
    return tuple(retval)


def track_back(
    paths: list[list[Coordinate | None]], start: Coordinate, end: Coordinate
) -> int:
    steps: int = 0
    current: Coordinate = end
    while current != start:
        steps += 1
        current = paths[current[1]][current[0]]
    return steps


def print_map(paths: list[list[Coordinate | None]]) -> None:
    translation = {(1, 0): "<", (-1, 0): ">", (0, 1): "^", (0, -1): "v"}
    for y, line in enumerate(paths):
        for x, point in enumerate(line):
            if point is None:
                print(" ", end="")
                continue
            dx = x - point[0]
            dy = y - point[1]
            print(translation[(dx, dy)], end="")
        print("")


def a_star(
    map_data: list[str], start: Coordinate, end: Coordinate
) -> list[list[Coordinate | None]]:
    map_end = len(map_data[0]) - 1, len(map_data) - 1
    # Let the record state: I did this calculation wrong initially and made the
    # sentinel "this place has not been visited yet" value small enough that it
    # could actually show up. The factor 10 should *should* fix this.
    default_distance = map_end[0] * map_end[1] * 10

    # camefrom map; lists which direction to go from each coordinate.
    reverse_map: list[list[Coordinate | None]] = [
        [None] * len(map_data[0]) for _ in range(len(map_data))
    ]

    # gScore; cheapest path cost from start to given coordinate.
    cost_to: dict[Coordinate, int] = defaultdict(lambda: default_distance)
    cost_to[start] = 0

    # fScore; "best guess" final path cost
    cost_forward: dict[Coordinate, int] = defaultdict(lambda: default_distance)
    cost_forward[start] = distance(start, end)

    # Instead of tracking the fScore separately, the 'distance' field of the
    # NavNode objects will track that information.
    open_queue: list[NavNode] = [NavNode(distance(start, end), start)]
    best: NavNode = NavNode(distance(start, end), start)
    print(f"Navigating from {start} to {end} (distance {best.distance})")

    while len(open_queue) > 0:
        candidate_point = hq.heappop(open_queue).position
        # print(f"Checking around {candidate_point}")
        if candidate_point == end:
            break
        neighbours = adjacent_coords(candidate_point, map_end)
        for option in neighbours:
            # print(f"assessing {option}")
            calc_distance = cost_to[candidate_point] + 1
            height = step_delta(map_data, candidate_point, option)
            if height <= 1 and calc_distance < cost_to[option]:
                # print(f"{option} potentially next step.")
                reverse_map[option[1]][option[0]] = candidate_point
                cost_to[option] = calc_distance
                if not any(item.position == option for item in open_queue):
                    open_queue.append(
                        NavNode(calc_distance + distance(option, end), option)
                    )
                    # print(f"{open_queue[-1]} added for further checking.")
        hq.heapify(open_queue)
        # print(f"{len(open_queue)} nodes to check. ({';'.join(str(x) for x in open_queue)})")
    return reverse_map


def star_one(data: list[str]) -> tuple[str, list[list[Coordinate | None]]]:
    start, end = initial_coordinates(data)
    path = a_star(data, start, end)
    print_map(path)
    dist = track_back(path, start, end)
    return str(dist), path


def star_two(data: list[list[str]]) -> str:
    start, end = initial_coordinates(data)
    print(f"{start} -> {end}")
    lengths: list[int] = []
    for i in range(len(data)):
        real_start = (start[0], i)
        path = a_star(data, real_start, end)
        length = track_back(path, real_start, end)
        print(f"starting from {real_start} gives {length} steps to the end.")
        lengths.append(length)
    return str(min(lengths))


s1_start: float = timer()
first_star, round_two_data = star_one(parsed_data)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(parsed_data)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
