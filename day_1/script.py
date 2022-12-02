import pathlib as pl
from dataclasses import dataclass
from time import perf_counter as timer


@dataclass
class ElfCalories:
    carrying: list[int] = None
    total: int = 0

    def __init__(self, values: list[int]):
        self.carrying = values
        self.total = sum(values)

    def __add__(self, other):
        if isinstance(other, int):
            return other + self.total


my_dir: pl.Path = pl.Path(__file__).parent
parsed_data: list[ElfCalories] = list()
with open(my_dir / "input.txt") as input_file:
    buffer: list[int] = []
    for line in input_file:
        line = line.strip()
        if line != "":
            number: int = int(line)
            buffer.append(number)
        else:
            elf: ElfCalories = ElfCalories(buffer)
            parsed_data.append(elf)
            buffer.clear()


def star_one(data: list[ElfCalories]) -> tuple[str, list[ElfCalories]]:
    max_elf: ElfCalories = max(data, key=lambda elf: elf.total)
    return (str(max_elf.total), data)


def star_two(data: list[ElfCalories]) -> str:
    data.sort(key=lambda elf: elf.total, reverse=True)
    return str(sum(elf.total for elf in data[0:3]))


s1_start: float = timer()
first_star, round_two_data = star_one(parsed_data)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(round_two_data)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
