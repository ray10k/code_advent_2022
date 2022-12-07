import pathlib as pl
from dataclasses import dataclass, field
from time import perf_counter as timer
from typing import Protocol


# Define an "overarching" main class to hold the two things needed down the line:
# a way to identify a directory/file, and a function to get the total size.
class OSNode(Protocol):
    name: str

    def size(self) -> int:
        ...


# A class to hold a directory. Since it extends the OSNode class, it has to have
# the name and size properties.
@dataclass
class OSDirectory(OSNode):
    name: str
    parent: "OSDirectory"
    # Contents is a dictionary of all node-names in this directory, plus a reference
    # to their actual nodes. Was originally a list, made into a dictionary due
    # to premature optimization; I expected to need the file names somehow in
    # the second star.
    contents: dict[str, OSNode] = field(default_factory=dict)

    def size(self) -> int:
        # since the challenge says that the size of a directory is the sum of all
        # files contained within (including subdirectories,) just get the result
        # of adding all sizes contained within.
        return sum(x.size() for x in self.contents.values())

    def __str__(self) -> str:
        # function to print out the current directory name, plus all files/
        # directories contained inside.
        retval = f"{self.name}/"
        retval += "\n\t".join(
            f"{item.name}{'/' if isinstance(item,OSDirectory) else ''}"
            for item in self.contents.values()
        )
        return retval


# Since a file is really just a name and a size, the OSFile class is similarly
# simple.
@dataclass
class OSFile(OSNode):
    name: str
    size_bytes: int

    def size(self) -> int:
        return self.size_bytes


# An iterator that "walks" over every directory and returns *only* the directory
# sizes. Say you give this a directory containing another directory, then this
# will first give you the size of the directory you gave it, then the size of
# the first directory in there, then (assuming the first directory has no further
# nested directories) the size of the second directory, and so forth.
def directory_tree_iterator(initial_directory: OSDirectory):
    # The trick I'm using is to manually do what for-x-in-y normally handles in
    # the background: make an iterator that runs over a series of OSNodes.
    # Instead of just running over the iterator's items right away, manually grab
    # the next item until an iterator runs out. When the grabbed item is a directory,
    # yield the size of said directory then add the iterator for that directory
    # to the list of iterators. Then, when an iterator runs out of items to yield,
    # remove it from the list of iterators.
    # Effectively, the directories variable holds a stack of iterators. An iterator
    # is just an object that will yield an item every time you feed it into the
    # next() function, or raise a StopIteration error when it's out of items to
    # yield. Also, an iterator will keep track of how far into its collection it
    # has gone so far, meaning you can keep an iterator around until you need it.
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
    # This function takes the console output (the puzzle input) and constructs a
    # file system tree. Thankfully, the input consistently runs ls before using
    # cd, so at no point can you get into a situation where a cd command tries
    # to enter a directory that you didn't even know existed.
    # Essentially, this function replicates (a simplified version of) how a file
    # system can build up a system of files-in-directories.
    retval = OSDirectory("/", None)
    current_directory = retval
    for instruction in instructions:
        if instruction == "$ ls":
            # ls does not change the current active directory and can be ignored.
            continue
        elif instruction.startswith("$ cd"):
            # Isolate the instruction of which directory is being entered.
            folder = instruction[4:].strip()
            if folder == "/":
                # Jump back to the root node. Conveniently, the root node is kept
                # accessible as the return value.
                current_directory = retval
            elif folder == "..":
                # Go up one level in the structure.
                current_directory = current_directory.parent
            else:
                # Since neither special case applies, the folder has to be a
                # "real" folder; a member of the current directory. Thankfully,
                # the input contains no situation where you are given an
                # instruction to enter a nonexistant directory.
                current_directory = current_directory.contents[folder]
        elif instruction.startswith("dir "):
            # dir only shows up after an ls, but there is no reason to pay
            # special attention to this constraint.
            dir_name = instruction[4:]
            current_directory.contents[dir_name] = OSDirectory(
                dir_name, current_directory
            )
        else:
            # Only remaining option is that the current line details a file.
            size, name = instruction.split(" ")
            size = int(size)
            current_directory.contents[name] = OSFile(name, size)
    return retval


# Standard input loading; Find out where in the file system this script is, strip
# off the last part of the path and replace it with "input.txt" then just load
# in the file's contents as a list of strings.
my_dir: pl.Path = pl.Path(__file__).parent
parsed_data: list[str] = list()
with open(my_dir / "input.txt") as input_file:
    parsed_data = input_file.readlines()

parsed_data = [datum.strip() for datum in parsed_data]

print(f"instructions: {len(parsed_data)}")


def star_one(data: list[str]) -> tuple[str, OSDirectory]:
    root = construct_tree(data)
    # filter() makes an iterator that, before yielding each item, checks if that
    # item meets whatever requirement you give (in this case, if the size of
    # the current directory is 100,000 or less.)
    filtered_sizes = filter(lambda x: x <= 100000, directory_tree_iterator(root))
    # Due to the filtering happening above, this line just gives the sum of all
    # directory sizes 100,000 and under, plus the parsed file system. No need
    # to construct the file system more than once, and said system will be
    # needed for the second star.
    return str(sum(filtered_sizes)), root


def star_two(data: OSDirectory) -> str:
    # My brain was a little fried here, so just wrote everything out. The system
    # has a total capacity of 70m and needs 30m for an update. Check how much
    # space is in use by grabbing the size of the root node (meaning, the sum
    # total of all files, effectively,) then calculate how much needs to be
    # freed up.
    used_space = data.size()
    total_space = 70000000
    free_space = total_space - used_space
    needed_space = 30000000
    space_to_free = needed_space - free_space
    # Another filtered iterator. This time, the filtered_sizes iterator will
    # only return directories that are at least as large as the minimum amount
    # of space needed for the update.
    filtered_sizes = filter(lambda x: x >= space_to_free, directory_tree_iterator(data))
    # min() can take an iterator and return the smallest value inside. Since the
    # challenge just asks the size of the smallest directory with a size
    # greater than the amount of space that has to be freed up, this is the
    # solution to the second challenge.
    return str(min(filtered_sizes))


# Standard timing and execution of the script.
s1_start: float = timer()
first_star, round_two_data = star_one(parsed_data)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(round_two_data)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
