import pathlib as pl
from dataclasses import dataclass
from time import perf_counter as timer
from collections import Counter


@dataclass
class Backpack:
    left_pocket: Counter = None
    right_pocket: Counter = None
    shared_item: str = ""

    def __init__(self, packing_list: str):
        pocket_size = len(packing_list) // 2
        left_list = packing_list[0:pocket_size]
        right_list = packing_list[pocket_size:]
        self.left_pocket = Counter(left_list)
        self.right_pocket = Counter(right_list)
        left_set = set(left_list)
        right_set = set(right_list)
        self.shared_item = (left_set & right_set).pop()

    def __str__(self) -> str:
        return f"{''.join(self.left_pocket.keys())}-{''.join(self.right_pocket.keys())} ({self.shared_item})"

    def item_set(self) -> set[str]:
        return set(self.left_pocket) | set(self.right_pocket)


ALPHABET = "abcdefghijklmnopqrstuvwxyz"


def priority(item: str) -> int:
    letter = item[0]
    result = 27 if letter.isupper() else 1
    result += ALPHABET.index(letter.lower())
    return result


def grouper(iterable, count = 3):
    iterators = [iter(iterable)] * count
    return zip(*iterators)

my_dir: pl.Path = pl.Path(__file__).parent
parsed_data: list[Backpack] = list()
with open(my_dir / "input.txt") as input_file:
    for line in input_file:
        parsed_data.append(Backpack(line.strip()))

def star_one(data: list[Backpack]) -> str:
    return str(sum(priority(datum.shared_item) for datum in data))

def star_two(data: list[Backpack]) -> str:
    running_total = 0
    for left, middle, right in grouper(data):
        shared = left.item_set() & middle.item_set() & right.item_set()
        shared = shared.pop()
        running_total += priority(shared)
    return str(running_total)


s1_start: float = timer()
first_star = star_one(parsed_data)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(parsed_data)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
