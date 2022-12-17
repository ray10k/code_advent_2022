import pathlib as pl
from dataclasses import dataclass, field
from collections import deque
from time import perf_counter as timer
import re


@dataclass
class Valve:
    name:str
    other_valves:list[str]
    flow_rate:int
    
    def __init__(self,names:list[str],flow_rate:str):
        self.name = names[0]
        self.other_valves = [other for other in names[1:]]
        self.flow_rate = int(flow_rate)
    
    def __str__(self)->str:
        return f"Valve {self.name}. Flow rate {self.flow_rate}, connects to valves {', '.join(self.other_valves)}"


@dataclass(order=True)
class NavStep:
    time_remaining:int = field(default=30,init=True,compare=False)
    current_node:str = field(default="",init=True,compare=False)
    to_visit:set[str] = field(default_factory=set,init=True,compare=False,hash=False)
    visited:list[tuple[str,...]] = field(default_factory=list,init=True,compare=False,hash=False)

VALVE_PATTERN = re.compile(r"[A-Z]{2}")
FLOW_PATTERN = re.compile(r"flow rate=(\d+)")
my_dir: pl.Path = pl.Path(__file__).parent
parsed_data: list[Valve] = list()

with open(my_dir / "input.txt") as input_file:
    for line in input_file:
        flow_rate = FLOW_PATTERN.search(line)[1]
        valve_names = VALVE_PATTERN.findall(line)
        parsed_data.append(Valve(valve_names,flow_rate))

print(*parsed_data,sep="\n")

def shortest_path(start:str,end:str,connections:dict[str,tuple[str,...]]) -> tuple[str,...]:
    candidates:deque[list[str]] = deque()
    candidates.append([start])
    while len(candidates) > 0:
        current = candidates.popleft()
        neighbours = connections[current[-1]]
        for neigh in neighbours:
            if neigh not in current:
                candidates.append([*current,neigh])
            if neigh == end:
                return tuple(candidates[-1][1:])

def score_path(path:list[str],valves:dict[str,Valve]) -> int:
    total = 0
    flow_per_min = 0
    for i in range(1,31):
        total += flow_per_min
        if path[i] == 'valve':
            flow_per_min += valves[path[i-1]].flow_rate
    return total

def star_one(data: list[Valve]) -> str:
    #1820 too low
    path_cache:dict[tuple[str,str],list[str]] = dict()
    connections:dict[str,tuple[str,...]] = {vl.name:tuple(vl.other_valves) for vl in data}
    
    good_valves:set[str] = set(vl.name for vl in data if vl.flow_rate > 0)
    print(f"Valves with flow: [{' '.join(good_valves)}]")

    valve_names:dict[str,Valve] = {vl.name:vl for vl in data}
    
    paths_found:set[int] = set()
    to_check:deque[NavStep] = deque([NavStep(current_node=data[0].name,to_visit=good_valves)])
    current:NavStep = None

    
    while len(to_check) > 0:
        current = to_check.pop()
        start:str=current.current_node
        for end in current.to_visit:
            if (start,end) not in path_cache:
                found_path = shortest_path(start,end,connections)
                path_cache[(start,end)] = found_path
            path = path_cache[(start,end)]
            full_path = current.visited.copy()
            full_path.append(path)

            remaining_valves = set(current.to_visit)
            remaining_valves.remove(end)

            time = sum(len(pth) for pth in full_path) + (len(full_path)-1)
            if time >= 31 or len(remaining_valves) == 0:
                recon_path = [data[0].name]
                for segment in full_path:
                    recon_path.extend(segment)
                    recon_path.append('valve')
                if len(recon_path) < 31:
                    recon_path.extend('..' for _ in range(31-len(recon_path)))
                ps = score_path(recon_path,valve_names)
                paths_found.add(ps)
                print('.',end='')
                continue
            to_check.append(NavStep(time,end,remaining_valves,full_path))
    #print(f"Cache: {' '.join(f'{s}->{e}:{len(path)} 'for (s,e),path in path_cache.items())}")
    print("")
    return str(max(paths_found))


def star_two(data: list[Valve]) -> str:
    pass


s1_start: float = timer()
first_star = star_one(parsed_data)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(parsed_data)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
