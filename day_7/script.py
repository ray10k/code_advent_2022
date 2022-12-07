import pathlib as pl
from dataclasses import dataclass, field
from time import perf_counter as timer
from typing import Protocol


class OSNode(Protocol):
    name: str

    def size(self) -> int:
        ...


@dataclass
class OSDirectory(OSNode):
    name: str
    parent: "OSDirectory"
    contents: dict[str, OSNode] = field(default_factory=dict)

    def size(self) -> int:
        return sum(x.size() for x in self.contents.values())

    def __str__(self) -> str:
        retval = f"{self.name}/"
        retval += "\n\t".join(
            f"{item.name}{'/' if isinstance(item,OSDirectory) else ''}"
            for item in self.contents.values()
        )
        return retval


@dataclass
class OSFile(OSNode):
    name: str
    size_bytes: int

    def size(self) -> int:
        return self.size_bytes


def directory_tree_iterator(initial_directory: OSDirectory):
    directories = [iter(initial_directory.contents.items())]
    while len(directories) > 0:
        try:
            _, current_item = next(directories[-1])
            if isinstance(current_item, OSDirectory):
                directories.append(iter(current_item.contents.items()))
                yield current_item.size()
        except StopIteration:
            directories.pop()


def construct_tree(instructions: list[str]) -> OSDirectory:
    retval = OSDirectory("/", None)
    listing = False
    current_directory = retval
    for instruction in instructions:
        if listing:
            if instruction.startswith("dir "):
                dir_name = instruction[4:]
                current_directory.contents[dir_name] = OSDirectory(
                    dir_name, current_directory
                )
                continue
            elif not instruction.startswith("$"):
                size, name = instruction.split(" ")
                size = int(size)
                current_directory.contents[name] = OSFile(name, size)
                continue
        listing = False

        if instruction == "$ ls":
            listing = True
            continue
        elif instruction == "$ cd /":
            current_directory = retval
        elif instruction == "$ cd ..":
            current_directory = current_directory.parent
        elif instruction.startswith("$ cd "):
            dir_name = instruction[5:]
            current_directory = current_directory.contents[dir_name]
    return retval


my_dir: pl.Path = pl.Path(__file__).parent
parsed_data: list[str] = list()
with open(my_dir / "input.txt") as input_file:
    parsed_data = input_file.readlines()

parsed_data = [datum.strip() for datum in parsed_data]

print(f"instructions: {len(parsed_data)}")


def star_one(data: list[str]) -> tuple[str, OSDirectory]:
    root = construct_tree(data)
    filtered_sizes = filter(lambda x: x <= 100000, directory_tree_iterator(root))
    return str(sum(filtered_sizes)), root


def star_two(data: OSDirectory) -> str:
    used_space = data.size()
    total_space = 70000000
    free_space = total_space - used_space
    needed_space = 30000000
    space_to_free = needed_space - free_space
    filtered_sizes = filter(lambda x: x >= space_to_free, directory_tree_iterator(data))
    return str(min(filtered_sizes))


s1_start: float = timer()
first_star, round_two_data = star_one(parsed_data)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(round_two_data)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
