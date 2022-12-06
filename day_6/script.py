import pathlib as pl
from dataclasses import dataclass
from time import perf_counter as timer

raw_data = ""

my_dir: pl.Path = pl.Path(__file__).parent

with open(my_dir / "input.txt") as input_file:
    raw_data = input_file.readline()  # Only one line this time.


def sliding_window(iterable, length):
    iterators = [iter(iterable[n:]) for n in range(length)]
    return zip(*iterators)


def find_unique_sequence(data_stream: str, seq_length: int, offset: int = 0) -> int:
    retval: int = -1
    check_set = set()
    for index, symbols in enumerate(
        sliding_window(data_stream[offset:], seq_length), start=offset
    ):
        check_set.clear()
        check_set.update(symbols)
        if len(check_set) == seq_length:
            retval = index + seq_length
            break
    return retval


def star_one(data: str) -> str:
    # 1038 too low
    starting_index = find_unique_sequence(data, 4)
    return str(starting_index)


def star_two(data: str) -> str:
    starting_index = find_unique_sequence(data, 14)
    return str(starting_index)


s1_start: float = timer()
first_star = star_one(raw_data)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(raw_data)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
