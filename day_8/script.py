import pathlib as pl
from time import perf_counter as timer
from itertools import product

#Remember our conversation about type hints? This here is a "type alias," 
# basically a more convenient way to write out a complex type. In this case,
# a field is a list containing lists of integers.
Field = list[list[int]]


my_dir: pl.Path = pl.Path(__file__).parent
parsed_data: list[str] = list()
with open(my_dir / "input.txt") as input_file:
    for line in input_file:
        parsed_data.append(line.strip())


def construct_field(width:int, height:int, list_of_rows:bool=True) -> Field:
    """Constructs a field of the given width and height, initialized to all 0s.
    if list_of_rows is true, the outer list will contain <height> lists of length
    <width>, vice-versa otherwise."""
    if list_of_rows:
        return [[0] * width for _ in range(height)]
    return [[0] * height for _ in range(width)]


def parse_field(raw_data: list[str]) -> tuple[Field, Field]:
    """Takes a representation of a field in the form of a list of strings where
    each string is a single row and each character is a single cell-value. Returns
    both the row-order field and the column-order field."""
    height = len(raw_data)
    width = len(raw_data[0])
    rows: Field = construct_field(width, height, True)
    columns: Field = construct_field(width, height, False)
    for y, row in enumerate(raw_data):
        for x, cell in enumerate(row):
            rows[y][x] = int(cell)
            columns[x][y] = int(cell)
    return rows, columns


def scan_line_visible(raw_data: list[int]) -> list[bool]:
    """Reads a single line of integer values, then returns a list of booleans
    where any True means the value is visible either from the start or the end
    of the given list. I.E, scan_line_visible([1,2,3,3,3,2,1]) will return [True,
    True,True,False,True,True,True]"""
    forward = [False] * len(raw_data)
    backward = [False] * len(raw_data)
    highest = raw_data[0]
    forward[0] = forward[-1] = True
    for cell, height in enumerate(raw_data):
        if height > highest:
            forward[cell] = True
            highest = height
    highest = raw_data[-1]
    for cell, height in enumerate(raw_data[::-1]):
        if height > highest:
            backward[cell] = True
            highest = height
    visible = [x or y for x, y in zip(forward, backward[::-1])]
    return visible


def scan_line_range(raw_data: list[int]) -> list[int]:
    """Reads a single line of integer values, then returns a list of scenic 
    scores for that line."""
    retval = [0] * len(raw_data)

    for index, height in enumerate(raw_data[1:-1], start=1):
        left, right = 0, 0
        for look in raw_data[index - 1 :: -1]:
            left += 1
            if look >= height:
                break
        for look in raw_data[index + 1 :]:
            right += 1
            if look >= height:
                break
        retval[index] = left * right
    return retval


def merge_bool_fields(rows: Field, columns: Field) -> Field:
    """Takes two fields of boolean values and constructs a new Field where each
    cell is False unless that cell was True in either input field."""
    retval = construct_field(len(columns), len(rows), True)
    for x, y in product(range(len(columns)), range(len(rows))):
        retval[y][x] = rows[y][x] or columns[x][y]
    return retval


def merge_int_fields(rows: Field, columns: Field) -> Field:
    """Takes two fields and constructs a new Field where each cell is the product
    of those cells in the input Fields."""
    retval = construct_field(len(columns), len(rows), True)
    for x, y in product(range(len(columns)), range(len(rows))):
        retval[y][x] = rows[y][x] * columns[x][y]
    return retval


def print_bool_field(to_show: Field) -> None:
    """prints a representation of a Field where any Truthy value is represented
    by an X and all other values are represented by a space."""
    for line in to_show:
        print("".join("X" if cell else " " for cell in line))


def star_one(data: list[str]) -> tuple[str, Field, Field]:
    # 2020 too high
    row_order, col_order = parse_field(data)
    row_visible = [scan_line_visible(row) for row in row_order]
    col_visible = [scan_line_visible(col) for col in col_order]
    visible_trees = merge_bool_fields(row_visible, col_visible)
    print_bool_field(visible_trees)
    #Returning the parsed fields, since they will be needed for the 2nd star.
    return str(sum(sum(row) for row in visible_trees)), row_order, col_order


def star_two(rows: Field, columns: Field) -> str:
    # 168000 too low
    row_ranges = [scan_line_range(row) for row in rows]
    col_ranges = [scan_line_range(col) for col in columns]
    scores = merge_int_fields(row_ranges, col_ranges)
    return str(max(max(row) for row in scores))


s1_start: float = timer()
first_star, rows, cols = star_one(parsed_data)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(rows, cols)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
