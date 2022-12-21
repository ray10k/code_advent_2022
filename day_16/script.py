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
    current_node:str = field(default="",init=True,compare=False)
    to_visit:set[str] = field(default_factory=set,init=True,compare=False,hash=False)
    visited:list[str] = field(default_factory=list,init=True,compare=False,hash=False)
    elephant_visited:list[str] = field(default_factory=list,init=True,compare=False,hash=False)

VALVE_PATTERN = re.compile(r"[A-Z]{2}")
FLOW_PATTERN = re.compile(r"flow rate=(\d+)")
my_dir: pl.Path = pl.Path(__file__).parent
parsed_data: list[Valve] = list()

with open(my_dir / "input.txt") as input_file:
    for line in input_file:
        flow_rate = FLOW_PATTERN.search(line)[1]
        valve_names = VALVE_PATTERN.findall(line)
        parsed_data.append(Valve(valve_names,flow_rate))


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

def sliding_window(start:list,size=2):
    iterators = [iter(start[x:]) for x in range(size)]

    return zip(*iterators)

def score_path(path:list[str],valves:dict[str,Valve],minutes:int = 30) -> int:
    total = 0
    flow_per_min = 0
    if len(path) == 0:
        return 0
    for mnt,(prev,current) in zip(range(1,minutes+1),sliding_window(path)):
        total += flow_per_min
        if current == 'valve':
            flow_per_min += valves[prev].flow_rate
    time_left = 1 + (minutes - len(path))
    total += flow_per_min * max(time_left,0)
    return total

example_path = ('AA', 'DD', 'valve', 'CC', 'BB', 'valve', 'AA', 'II', 'JJ', 'valve', 'II','AA','DD','EE','FF','GG','HH','valve','GG','FF','EE','valve','DD','CC','valve','..','..','..','..','..','..','..','..','..','..')
example_2_path = ('AA', 'II', 'JJ', 'valve', 'II', 'AA', 'BB', 'valve', 'CC', 'valve')
example_2_elephant = ('AA', 'DD', 'valve', 'EE', 'FF', 'GG', 'HH', 'valve', 'GG', 'FF', 'EE', 'valve')
example_data = ["Valve AA has flow rate=0; tunnels lead to valves DD, II, BB",
"Valve BB has flow rate=13; tunnels lead to valves CC, AA",
"Valve CC has flow rate=2; tunnels lead to valves DD, BB",
"Valve DD has flow rate=20; tunnels lead to valves CC, AA, EE",
"Valve EE has flow rate=3; tunnels lead to valves FF, DD",
"Valve FF has flow rate=0; tunnels lead to valves EE, GG",
"Valve GG has flow rate=0; tunnels lead to valves FF, HH",
"Valve HH has flow rate=22; tunnel leads to valve GG",
"Valve II has flow rate=0; tunnels lead to valves AA, JJ",
"Valve JJ has flow rate=21; tunnel leads to valve II",]
test_valves = dict()
for line in example_data:
    fr = FLOW_PATTERN.search(line)[1]
    vn = VALVE_PATTERN.findall(line)
    test_valves[vn[0]] = Valve(vn,fr)

if score_path(example_path,test_valves) != 1651:
    print("ERROR! failed known-good test.")
else:
    print("Sanity test OK")

if score_path(example_2_path,test_valves,26)+score_path(example_2_elephant,test_valves,26) != 1707:
    print("ERROR! failed second known-good test.")
else:
    print("Sanity test 2 OK")

def star_one(data: list[Valve]) -> tuple[str,dict[tuple[str,str],list[str]]]:
    #1820 too low
    #Dictionary for valve-to-valve paths. Since the fastest route between, say,
    # AA and ZZ will not change, calculate once and cache the result. Lookups
    # are cheaper than calculations in this case!
    path_cache:dict[tuple[str,str],list[str]] = dict()
    #Convenience lookup table mapping which valves a given valve connects to.
    connections:dict[str,tuple[str,...]] = {vl.name:tuple(vl.other_valves) for vl in data}
    #Convenience lookup table to turn a valve name into the associated object.
    valve_names:dict[str,Valve] = {vl.name:vl for vl in data}
    
    #All valves with a flowrate greater than 0; I don't care about valves that,
    # when opened, do not contribute to the final outcome.
    good_valves:set[str] = set(vl.name for vl in data if vl.flow_rate > 0)


    #Set of all total flow-sums. When a path is calculated, the score for that
    # path is added to this set.
    paths_found:set[int] = set()
    #Stack of all partially explored paths.
    to_check:deque[NavStep] = deque([NavStep(current_node="AA",to_visit=good_valves,visited=["AA"])])
    current:NavStep = None

    stack_depth = 0

    while len(to_check) > 0:
        stack_depth = max(stack_depth,len(to_check))
        current = to_check.pop()
        start:str=current.current_node
        for end in current.to_visit:
            if (start,end) not in path_cache:
                found_path = shortest_path(start,end,connections)
                path_cache[start,end] = found_path

            full_path = [*current.visited,*path_cache[start,end],"valve"]

            remaining_valves = set(current.to_visit)
            remaining_valves.remove(end)

            time = len(full_path)
            if time >= 31 or len(remaining_valves) == 0:
                ps = score_path(full_path,valve_names)
                paths_found.add(ps)
                continue
            to_check.append(NavStep(end,remaining_valves,full_path))
    print("Stack depth:",stack_depth)
    return str(max(paths_found)),path_cache


def star_two(data: list[Valve],path_cache: dict[tuple[str,str],list[str]]) -> str:
    good_valves = set(vl.name for vl in data if vl.flow_rate > 0)
    #Convenience lookup table mapping which valves a given valve connects to.
    connections:dict[str,tuple[str,...]] = {vl.name:tuple(vl.other_valves) for vl in data}
    #Convenience lookup table to turn a valve name into the associated object.
    valve_names:dict[str,Valve] = {vl.name:vl for vl in data}
    to_check:deque[NavStep] = deque()
    to_check.append(NavStep("AA",good_valves,["AA"],["AA"]))

    current_step:NavStep = None
    flow_totals:set[int] = set()
    loop_counter = 0

    while len(to_check) > 0:
        current_step = to_check.pop()
        loop_counter += 1
        if loop_counter == 10000:
            loop_counter = 0
            print(f"Stack size: {len(to_check)}. Paths: {len(current_step.visited)} and {len(current_step.elephant_visited)}. Unchecked: {len(current_step.to_visit)}")

        #Favour the non-elephant 'player'
        elephant_turn:bool = (len(current_step.visited) > len(current_step.elephant_visited))
        path_so_far:list[str] = current_step.elephant_visited if elephant_turn else current_step.visited
        other_path:list[str] = current_step.visited if elephant_turn else current_step.elephant_visited

        current_valve:str = path_so_far[0] if len(path_so_far) == 1 else path_so_far[-2]
        for target_valve in current_step.to_visit:
            if (current_valve,target_valve) not in path_cache:
                pth = shortest_path(current_valve,target_valve,connections)
                path_cache[current_valve,target_valve] = pth
            path = path_cache[current_valve,target_valve]
            full_path = [*path_so_far,*path,"valve"]
            remaining_valves = set(current_step.to_visit)
            remaining_valves.remove(target_valve)
            if (len(full_path) >= 27 and elephant_turn) or len(remaining_valves) == 0:
                player_score = score_path(other_path,valve_names,26)
                elephant_score = score_path(full_path,valve_names,26)
                flow_totals.add(player_score+elephant_score)
                continue
            
            if elephant_turn:
                to_check.append(NavStep(target_valve,remaining_valves,other_path,full_path))
            else:
                to_check.append(NavStep(target_valve,remaining_valves,full_path,other_path))
    return str(max(flow_totals))


s1_start: float = timer()
first_star,cache = star_one(parsed_data)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(parsed_data,cache)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
