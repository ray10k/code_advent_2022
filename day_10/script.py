import pathlib as pl
from dataclasses import dataclass
from time import perf_counter as timer


class SimulatedCPU:
    def __init__(self, program: list[str], trapped_cycles: list[int]):
        self.cycles_to_wait: int = 0
        self.cycles_executed: int = -1
        self.register_value: int = 1
        self.suspended_value: int = 1
        self.trapped_cycles: list[int] = trapped_cycles.copy()
        self.trapped_values: list[int] = [0] * len(trapped_cycles)
        self.program: list[int] = program.copy()
        self.active_program = iter(program)

    def reset_program(self) -> None:
        self.cycles_to_wait = 0
        self.cycles_executed = -1
        self.register_value = 1
        self.suspended_value = 1
        self.trapped_values = [0] * len(self.trapped_values)
        self.active_program = iter(self.program)

    def do_tick(self) -> None:
        # Check if a program is running, start a new one if it's not.
        if self.active_program is None:
            self.reset_program()
        # Increment program counter
        self.cycles_executed += 1
        # Check if the current register value is important or not
        if self.cycles_executed in self.trapped_cycles:
            index = self.trapped_cycles.index(self.cycles_executed)
            self.trapped_values[index] = self.cycles_executed * self.register_value
        # Handle operations that take more than one tick
        if self.cycles_to_wait > 0:
            self.cycles_to_wait -= 1
            return
        # Since there are no more ticks to wait, handle the results of any pending
        # operations.
        self.register_value = self.suspended_value
        current_instruction = next(self.active_program)
        if current_instruction.startswith("noop"):
            return
        elif current_instruction.startswith("addx"):
            _, amount = current_instruction.strip().split(" ")
            self.suspended_value += int(amount)
            self.cycles_to_wait = 1
            return
        print(f"unknown instruction: {current_instruction}")

    def get_pixel(self) -> str:
        if self.cycles_executed % 40 in range(
            self.register_value - 1, self.register_value + 2
        ):
            return "█"
        return " "


def grouper(iterable, length):
    iterators = [iter(iterable)] * length
    return zip(*iterators)


my_dir: pl.Path = pl.Path(__file__).parent
parsed_data: list[str] = list()
with open(my_dir / "input.txt") as input_file:
    parsed_data.extend(input_file.readlines())


def star_one(data: list[str]) -> str:
    important_cycles = [20, 60, 100, 140, 180, 220]
    cpu = SimulatedCPU(data, important_cycles)
    try:
        while True:
            cpu.do_tick()
    except:
        # Should happen when the program is completed.
        pass
    return str(sum(cpu.trapped_values))


def star_two(data: list[str]) -> str:
    cpu = SimulatedCPU(data, [])
    retval: list[str] = []
    try:
        while True:
            cpu.do_tick()
            retval.append(cpu.get_pixel())
    except:
        # should happen when the program is completed.
        pass
    lines = ["".join(letters) for letters in grouper(retval, 40)]
    newline = "\n"
    return f"\n{newline.join(lines)}"


s1_start: float = timer()
first_star = star_one(parsed_data)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(parsed_data)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
