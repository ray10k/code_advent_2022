import pathlib as pl
from dataclasses import dataclass
from time import perf_counter as timer
import re


@dataclass
class MoveStep:
    size: int
    start: int
    end: int


initial_stacks = None

my_dir: pl.Path = pl.Path(__file__).parent
parsed_moves: list[MoveStep] = list()
with open(my_dir / "input.txt") as input_file:
    # Read the lines describing the initial stack arrangement.
    stack_lines: list[str] = []
    for line in input_file:
        if line.strip() == "":
            break
        # str.strip() will also delete leading spaces, which throws stuff out of
        # alignment. Instead, manually remove the line-break.
        stack_lines.append(line[0:-1])
    # Initialize the list-of-lists containing the initial arrangement of stacks.
    numbers = stack_lines[-1].split("   ")
    # Slightly awkward initialization, but it's an easy way to ensure there are
    # no same-reference lists in the outer list.
    initial_stacks = [list() for _ in range(len(numbers))]
    # Regex to identify a box and extract its letter. Also "identifies" whitespace
    # to keep the alignment correct.
    # I have a problem. I'll use regex. I have two problems...
    box_regex = re.compile("(\[(\w)\]|   ) ?")
    # Iterate over the input in reverse and insert the found crates on the stacks.
    for manifest in stack_lines[-2::-1]:
        boxes = box_regex.findall(manifest)
        print(f"Splitting manifest line {manifest}.")
        for pile, (_, label) in enumerate(boxes):
            if label == "":
                continue
            initial_stacks[pile].append(label)
    # Parse the rest of the input file to get the move instructions.
    number_regex = re.compile(" (\d+)")
    for line in input_file:
        size, start, end = number_regex.findall(line)
        size, start, end = int(size), int(start) - 1, int(end) - 1
        parsed_moves.append(MoveStep(size, start, end))

for pile_index, pile in enumerate(initial_stacks):
    print(f"Stack {pile_index}: {''.join(pile)}")
print(f"There are {len(parsed_moves)} instructions to run.")

star_one_stacks = [stack.copy() for stack in initial_stacks]
star_two_stacks = [stack.copy() for stack in initial_stacks]
buffer = []
for instruction in parsed_moves:
    for _ in range(instruction.size):
        crate = star_one_stacks[instruction.start].pop()
        star_one_stacks[instruction.end].append(crate)
        buffer.append(star_two_stacks[instruction.start].pop())
    for x in buffer[::-1]:
        star_two_stacks[instruction.end].append(x)
    buffer.clear()

print("Final arrangement of the stacks for star 1:")
for numb, stack in enumerate(star_one_stacks):
    print(f"{numb}: {' '.join(stack)};")

print("Final arrangement of the stacks for star 2:")
for numb, stack in enumerate(star_two_stacks):
    print(f"{numb}: {' '.join(stack)};")


def star_one(data: list[list[str]]) -> str:
    return "".join(datum[-1] for datum in data)


def star_two(data: list[list[str]]) -> str:
    return "".join(datum[-1] for datum in data)


s1_start: float = timer()
first_star = star_one(star_one_stacks)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(star_two_stacks)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
