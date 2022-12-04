import pathlib as pl
from dataclasses import dataclass
from time import perf_counter as timer


@dataclass(frozen=True, repr=True)
class PairJob:
    first_elf_start: int
    first_elf_end: int
    second_elf_start: int
    second_elf_end: int

    def has_full_overlap(self) -> bool:
        length_a = self.first_elf_end - self.first_elf_start
        length_b = self.second_elf_end - self.second_elf_start
        if length_a < length_b:
            # first elf is elf A.
            return (
                self.first_elf_start >= self.second_elf_start
                and self.first_elf_end <= self.second_elf_end
            )
        # Second elf is elf A, or both have same range.
        return (
            self.second_elf_start >= self.first_elf_start
            and self.second_elf_end <= self.first_elf_end
        )

    def has_any_overlap(self) -> bool:
        min_start = min(self.first_elf_start, self.second_elf_start)
        if min_start == self.first_elf_start:
            return self.second_elf_start <= self.first_elf_end
        return self.first_elf_start <= self.second_elf_end


# Possible situations:
# - No overlap; elf A is doing a lower range than elf B.
# - Partial overlap; start of elf A range is inside elf B range.
# - Full overlap; Start and end of both elves are the same.
# - Full overlap; Start and end of elf A range between extremes of elf B range.
# - Full overlap; Start of elf A range is start of elf B range, end of elf A range is inside elf B range.
# - Full overlap; Start of elf A range is inside elf B range, end of elf A range is end of elf B range.

# Steps to check:
# - Find shortest range. That is now elf A.
# - Check if start of elf A range >= start of elf B range.
# - Check if end of elf A range <= end of elf B range.

# Partial overlap check:
# - Find the lowest starting value.
# - Check if the other starting value is inside the range that the value previously found belongs to.


my_dir: pl.Path = pl.Path(__file__).parent
parsed_data: list[PairJob] = list()
with open(my_dir / "input.txt") as input_file:
    for line in input_file:
        elves = line.strip().split(",")
        steps = [int(x) for x in elves[0].split("-")]
        steps.extend(int(x) for x in elves[1].split("-"))
        if len(steps) != 4:
            print(f"ERROR! Line {line.strip()} did not parse correctly.")
            print(f"Values: <{' '.join(str(x) for x in steps)}>")
        parsed_data.append(PairJob(*steps))


def star_one(data: list[PairJob]) -> str:
    # 469 too low
    return str(sum(job.has_full_overlap() for job in data))


def star_two(data: list[PairJob]) -> str:
    return str(sum(job.has_any_overlap() for job in data))


s1_start: float = timer()
first_star = star_one(parsed_data)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(parsed_data)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
