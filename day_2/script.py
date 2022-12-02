import pathlib as pl
from dataclasses import dataclass
from time import perf_counter as timer

#AX = rock
#BY = paper
#CZ = scissors

#X lose, Y draw, Z win

WINS = {"rock" : "paper","paper": "scissors","scissors":"rock"}
LOSSES = {"rock" : "scissors", "paper" : "rock","scissors": "paper"}
POINTS = {"X":0,"Y":3,"Z":6}

GESTURE_SCORES = {"X":1,"Y":2,"Z":3,"rock":1,"paper":2,"scissors":3}
RESULT_SCORES = {"AX":3,"AY":6,"AZ":0,"BX":0,"BY":3,"BZ":6,"CX":6,"CY":0,"CZ":3}
RESPONSES = {"AX":"Z","AY":"X","AZ":"Y","BX":"X","BY":"Y","BZ":"Z","CX":"X","CY":"Z","CZ":"Y"}
NAMES = {"A":"rock", "B":"paper", "C":"scissors", "X":"rock","Y":"paper","Z":"scissors"}
@dataclass
class RPSThrow:
    player_gesture:str
    opponent_gesture:str
    combined_gesture:str
    gesture_score:int
    result_score:int

    def __init__(self,single_round:str):
        self.opponent_gesture,self.player_gesture = single_round.strip().split(" ")
        self.combined_gesture = self.opponent_gesture+self.player_gesture
        self.gesture_score = GESTURE_SCORES[self.player_gesture]
        self.result_score = RESULT_SCORES[self.combined_gesture]

    def real_score(self) -> int:
        result_points = POINTS[self.player_gesture]
        other_gesture = NAMES[self.opponent_gesture]
        gesture_points = 0
        if self.player_gesture == "X": #lose
            gesture_points = GESTURE_SCORES[LOSSES[other_gesture]]
        elif self.player_gesture == "Y": #draw
            gesture_points = GESTURE_SCORES[other_gesture]
        elif self.player_gesture == "Z": #win
            gesture_points = GESTURE_SCORES[WINS[other_gesture]]
        return result_points+gesture_points

    def __str__(self) -> str:
        return f"{NAMES[self.opponent_gesture]} vs {NAMES[self.player_gesture]} -> {self.gesture_score+self.result_score}"

my_dir:pl.Path = pl.Path(__file__).parent
parsed_data:list[RPSThrow] = list()
with open(my_dir / "input.txt") as input_file:
    for line in input_file:
        #parse line, add to parsed_data
        parsed_data.append(RPSThrow(line))

print(*parsed_data,sep="; ")

def star_one(data:list[RPSThrow]) -> tuple[str,list[RPSThrow]]:
    return str(sum(throw.result_score+throw.gesture_score for throw in data)), data

def star_two(data:list[RPSThrow]) -> str:
    #11138 too low
    return str(sum(throw.real_score() for throw in data))

s1_start:float = timer()
first_star,round_two_data = star_one(parsed_data)
s1_end:float = timer()
print(f"The code for the first star: >{first_star}< ({s1_end - s1_start:0.4f} sec)")
s2_start:float = timer()
second_star = star_two(round_two_data)
s2_end:float = timer()
print(f"The code for the second star: >{second_star}< ({s2_end - s2_start:0.4f} sec)")
