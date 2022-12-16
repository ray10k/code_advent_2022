import pathlib as pl
from dataclasses import dataclass, field
from time import perf_counter as timer
import re
from typing import Iterator

COORDINATE_PATTERN = re.compile(r"x=(-?\d+), y=(-?\d+)")


@dataclass(frozen=True, slots=True, order=True)
class s_range:
    start: int = field(init=True, repr=True, compare=True)
    end: int = field(init=True, repr=True, compare=False)

    def __str__(self) -> str:
        return f"Range from {self.start} to {self.end} ({self.end-self.start})"

    def in_range(self, x) -> bool:
        return x >= self.start and x < self.end


@dataclass(slots=True)
class Sensor:
    x: int = 0
    y: int = 0
    beacon_x: int = 0
    beacon_y: int = 0
    distance: int = 0

    def __init__(self, line: str):
        coords = COORDINATE_PATTERN.findall(line.strip())
        coords = [(int(x), int(y)) for x, y in coords]
        (self.x, self.y), (self.beacon_x, self.beacon_y) = coords
        self.distance = abs(self.x - self.beacon_x) + abs(self.y - self.beacon_y)

    def __str__(self) -> str:
        return (
            f"Sensor at ({self.x};{self.y}) Beacon at ({self.beacon_x};{self.beacon_y})"
        )

    def horizontal_range(self, y: int) -> s_range:
        delta_y = max(self.y, y) - min(self.y, y)
        # Closest point on the given height is outside the range. Terminate with
        # a zero-length range.
        if delta_y > self.distance:
            return s_range(self.x, self.x)
        # Closest point on the given height is exactly as far removed from the
        # sensor as its nearest beacon. Return a length-one range.
        if delta_y == self.distance:
            return s_range(self.x, self.x)
        # Closest point on the given height is somewhere in the sensor's range.
        remainder = self.distance - delta_y
        return s_range(self.x - remainder, (self.x + remainder + 1))

    def in_range(self, x, y) -> bool:
        dist_to = abs(self.x - x) + abs(self.y - y)
        return dist_to <= self.distance

    def outside_border(self) -> Iterator[tuple[int, int]]:
        yield (self.x, self.y + self.distance + 1)
        yield (self.x, self.y - (self.distance + 1))
        for y in range(-1, self.distance + 1):
            remainder = self.distance - y
            yield (self.x - remainder, self.y + y + 1)
            yield (self.x + remainder, self.y + y + 1)
            yield (self.x - remainder, self.y - (y + 1))
            yield (self.x + remainder, self.y - (y + 1))


# quick test.
middle = Sensor("x=3, y=3 then x=2, y=2")
print(middle)
edge_points = set(middle.outside_border())
for y in range(8):
    for x in range(8):
        if x == middle.x and y == middle.y:
            print("+", end="")
        elif x == middle.beacon_x and y == middle.beacon_y:
            print("=", end="")
        elif (x, y) in edge_points:
            print("#", end="")
        elif middle.in_range(x, y):
            print("*", end="")
        else:
            print(".", end="")
    print("")


def dedup_ranges(ranges: list[s_range]) -> list[s_range]:
    left: s_range = ranges[0]
    retval: list[s_range] = []
    for right in ranges[1:]:
        # Discard empty ranges.
        if right.start == right.end:
            continue
        # Merge ranges that start inside other ranges.
        if right.start <= left.end:
            left = s_range(left.start, max(left.end, right.end))
        # If the left and right ranges do not overlap, add the left to the list
        # and carry on with a 'new' range.
        else:
            retval.append(left)
            left = right
    retval.append(left)
    return retval


def clamp_range(ranges: list[s_range], extremes: s_range) -> list[s_range]:
    retval = []
    for rn in ranges:
        if rn.start < extremes.start:
            if rn.end > extremes.start and rn.end < extremes.end:
                retval.append(s_range(extremes.start, rn.end))
                continue
            elif rn.end > extremes.start:
                return [extremes]
            else:
                continue
        if rn.end > extremes.end:
            if rn.start < extremes.end:
                retval.append(s_range(rn.start, extremes.end))
                continue
            else:
                continue
        retval.append(rn)
    return retval


my_dir: pl.Path = pl.Path(__file__).parent
parsed_data: list[Sensor] = list()
with open(my_dir / "input.txt") as input_file:
    parsed_data = [Sensor(line) for line in input_file]


def star_one(data: list[Sensor]) -> str:
    critical_height: int = 2000000
    print("sensor count:", len(data))
    ranges: list[s_range] = [
        sensor.horizontal_range(critical_height) for sensor in data
    ]
    print("range count before deduplication:", len(ranges))
    ranges.sort()
    ranges = dedup_ranges(ranges)
    print("deduped ranges:", *(str(rn) for rn in ranges))
    return str(sum(rn.end - rn.start for rn in ranges))


def star_two(data: list[Sensor]) -> str:
    limits = s_range(0, 4000001)
    print("Note: This is a very inefficient way of doing things, but it works.")
    print("Expect this to run for upward of 210 seconds.")
    for index, sensor in enumerate(data):
        for x, y in sensor.outside_border():
            if not limits.in_range(x) or not limits.in_range(y):
                continue
            if any(sn.in_range(x, y) for sn in data):
                continue
            return str((x * 4000000) + y)
        print(f"Sensor {index} checked.")


s1_start: float = timer()
first_star = star_one(parsed_data)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(parsed_data)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
