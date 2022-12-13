import pathlib as pl
from itertools import zip_longest
from functools import cmp_to_key
from time import perf_counter as timer
import re

TOKEN_PATTERN = re.compile(r"(\[|\]|\d+)")


def listify(to_parse: str) -> list:
    retval = []
    stack = [retval]
    tokens = TOKEN_PATTERN.findall(to_parse)

    for token in tokens:
        if token == "[":
            stack[-1].append([])
            stack.append(stack[-1][-1])
        elif token == "]":
            stack.pop()
        else:
            stack[-1].append(int(token))
    return retval[0]


def check_order(left: str, right: str) -> bool:
    # print(f"{left} check against {right}")
    l_struct = listify(left)
    r_struct = listify(right)
    l_stack = []
    r_stack = []
    while True:
        if is_stack(l_struct) and is_stack(r_struct):
            if len(l_struct) == 0 and len(r_struct) == 0:
                # print('Dropping one stack-level')
                l_struct = l_stack.pop()
                r_struct = r_stack.pop()
                continue
            if len(l_struct) == 0 or len(r_struct) == 0:
                return len(l_struct) == 0

        if is_stack(l_struct[0]) and is_stack(r_struct[0]):
            # print('Rising one stack-level.')
            l_stack.append(l_struct)
            r_stack.append(r_struct)
            l_struct = l_struct.pop(0)
            r_struct = r_struct.pop(0)
            continue

        if is_number(l_struct[0]) and is_number(r_struct[0]):
            # print(f"Number comparison {l_struct[0]} vs {r_struct[0]}")
            if l_struct[0] == r_struct[0]:
                l_struct.pop(0)
                r_struct.pop(0)
                continue
            return l_struct[0] < r_struct[0]

        if is_number(l_struct[0]):
            # print(f"Stacking {l_struct[0]} left.")
            l_struct[0] = [l_struct[0]]
            continue
        elif is_number(r_struct[0]):
            # print(f"Stacking {r_struct[0]} right.")
            r_struct[0] = [r_struct[0]]
            continue
        # print("One stack exhausted.")
        return len(l_struct) < len(r_struct)


def is_stack(item: list | int) -> bool:
    return isinstance(item, list)


def is_number(item: list | int) -> bool:
    return isinstance(item, int)


def grouper(iterable, count: int):
    iterators = [iter(iterable)] * count
    return zip_longest(*iterators, fillvalue="")


my_dir: pl.Path = pl.Path(__file__).parent
parsed_data: list[str] = list()
with open(my_dir / "input.txt") as input_file:
    parsed_data = [line.strip() for line in input_file]


def star_one(data: list[str]) -> str:
    # 6640 too high
    valids: list[int] = []
    for index, (left, right, _) in enumerate(grouper(data, 3), start=1):
        if check_order(left, right):
            valids.append(index)
    return str(sum(valids))


def star_two(data: list[str]) -> str:
    # 23086 too high
    def comparison(left, right) -> int:
        if check_order(left, right):
            return -1
        return 1

    clean_data = [line for line in data if line != ""]
    clean_data.append("[[2]]")
    clean_data.append("[[6]]")
    clean_data.sort(key=cmp_to_key(comparison))
    index_a = clean_data.index("[[2]]") + 1
    index_b = clean_data.index("[[6]]") + 1
    return str(index_a * index_b)


s1_start: float = timer()
first_star = star_one(parsed_data)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(parsed_data)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
