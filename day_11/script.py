import pathlib as pl
from collections.abc import Callable
from time import perf_counter as timer
from math import floor, prod
import re


class Monkey:
    def __init__(
        self,
        id: int,
        initial_items: list[int],
        operation: str,
        test: int,
        fail: int,
        pass_: int,
    ):
        self.id: int = id
        self.item_list: list[int] = initial_items
        _, op, num = operation.split(" ")
        oper: Callable[[int], int] = None
        if op == "*" and num == "old":
            oper = lambda x: x * x
        elif op == "*":
            num = int(num)
            oper = lambda x: x * num
        else:
            num = int(num)
            oper = lambda x: x + num
        self.operation: Callable[[int], int] = oper
        self.test: int = test
        self.fail_monkey: int = fail
        self.pass_monkey: int = pass_
        self.items_checked: int = 0
        self.max_test = test

    def check_all_items(self, relief=True) -> dict[int, list[int]]:
        retval = {self.pass_monkey: [], self.fail_monkey: []}
        self.items_checked += len(self.item_list)
        for item in self.item_list:
            item = self.operation(item)
            item = int(floor(item / 3)) if relief else item % self.max_test
            if item % self.test == 0:
                retval[self.pass_monkey].append(item)
            else:
                retval[self.fail_monkey].append(item)
        self.item_list = []
        return retval


def grouper(iterable, size):
    iterators = [iter(iterable)] * size
    return zip(*iterators)


NUMBER_REGEX = re.compile(r"(\d+)")
OPERATION_REGEX = re.compile(r"(old) (\*|\+) (old|\d+)")


def prep_monkeys(raw_data: list[str]) -> list[Monkey]:
    retval: list[Monkey] = list()
    for (
        id_line,
        items_line,
        operation_line,
        test_line,
        pass_line,
        fail_line,
        _,
    ) in grouper(raw_data, 7):
        id = int(NUMBER_REGEX.findall(id_line)[0])
        items = [int(item) for item in NUMBER_REGEX.findall(items_line)]
        operation = operation_line[19:].strip()
        test = int(NUMBER_REGEX.findall(test_line)[0])
        pass_ = int(NUMBER_REGEX.findall(pass_line)[0])
        fail_ = int(NUMBER_REGEX.findall(fail_line)[0])
        print(
            f"Monkey {id}. Has {len(items)} items. {operation}, test {test};{pass_}/{fail_}"
        )
        retval.append(Monkey(id, items, operation, test, fail_, pass_))
    return retval


my_dir: pl.Path = pl.Path(__file__).parent
parsed_data: list[str] = list()
with open(my_dir / "input.txt") as input_file:
    parsed_data = input_file.readlines()
parsed_data.append("BLANK")  # Makes parsing a little easier down the line.


def star_one(data: list[str]) -> str:
    monkeys = prep_monkeys(data)
    for i in range(20):
        # print(f"round {i+1}.")
        for monkey in monkeys:
            results = monkey.check_all_items()
            for id, items in results.items():
                monkeys[id].item_list.extend(items)
    monkeys.sort(key=lambda monkey: monkey.items_checked, reverse=True)
    monkey_business = monkeys[0].items_checked * monkeys[1].items_checked
    return str(monkey_business)


def star_two(data: list[Monkey]) -> str:
    monkeys = prep_monkeys(data)
    max_test = prod(set(mnk.test for mnk in monkeys))
    print(f"Product of all testing thresholds: {max_test}")
    for monkey in monkeys:
        monkey.max_test = max_test
    for i in range(10000):
        # print(f"round {i+1}.")
        for monkey in monkeys:
            results = monkey.check_all_items(relief=False)
            for id, items in results.items():
                monkeys[id].item_list.extend(items)
    monkeys.sort(key=lambda monkey: monkey.items_checked, reverse=True)
    monkey_business = monkeys[0].items_checked * monkeys[1].items_checked
    return str(monkey_business)


s1_start: float = timer()
first_star = star_one(parsed_data)
s1_end: float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start: float = timer()
second_star = star_two(parsed_data)
s2_end: float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
