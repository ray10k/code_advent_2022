import pathlib as pl
import os

base_path:pl.Path = pl.Path(os.getcwd())
print(base_path)
input("Press enter to initialize scripts.")
for i in range(1,26):
    day_directory = base_path / f"day_{i}"
    os.makedirs(day_directory,exist_ok=True)
    with open(day_directory/"script.py","w") as script_file:
        script_file.write("""import pathlib as pl
from dataclasses import dataclass
from time import perf_counter as timer

@dataclass
class DataNode:
    ...

my_dir:pl.Path = pl.Path(__file__).parent
parsed_data:list[DataNode] = list()
with open(my_dir / "input.txt") as input_file:
    for line in input_file:
        #parse line, add to parsed_data
        ...

def star_one(data:list[DataNode]) -> tuple[str,list[DataNode]]:
    pass

def star_two(data:list[DataNode]) -> str:
    pass

s1_start:float = timer()
first_star,round_two_data = star_one(parsed_data)
s1_end:float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start:float = timer()
second_star = star_two(round_two_data)
s2_end:float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
""")
    open(day_directory/"input.txt","w").close()
    