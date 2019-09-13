import random
import time
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import statistics
import numpy as np
import json

from utils import eval_xor, eval_and, eval_or, type_1_threshold, type_1_feedback, type_2_threshold

POSITIVE = 'positive'
NEGATIVE = 'negative'

class Clause:
    def __init__(self, polarity: bool, tsetlins: list):
        # Polarity Focus (polarity = True => y=1 | polarity = False => y=0)
        self.polarity = polarity

        # This Clause's assigned team of tsetlins
        self.tsetlins = tsetlins


class Tsetlin:
    def __init__(self, n, should_invert):
        # n is the number of states per action
        self.n = n
        # Initial state selected randomly
        self.state = random.choice([self.n, self.n+1])

        self.should_invert = should_invert

    def is_include(self):
        if self.state >= self.n:
            return True
        else:
            return False

    def reward(self) -> None:
        if self.n >= self.state > 1:
            self.state -= 1
        elif self.n < self.state < 2*self.n:
            self.state += 1

    def penalize(self) -> None:
        if self.state <= self.n:
            self.state += 1
        elif self.state > self.n:
            self.state -= 1

    def make_decision(self) -> bool:
        if self.state <= self.n:
            return True
        else:
            return False

    def literal_value(self, literal):
        if self.should_invert:
            return not literal
        else:
            return bool(literal)


def get_penalty_limit(m: int) -> float:
    if m <= 3:
        return m * 0.2
    else:
        return 0.6 - (m - 3) * 0.2


def give_feedback(current_threshold: float, tsetlin: object) -> None:
    if random.random() < current_threshold:
        tsetlin.reward()
    else:
        tsetlin.penalize()


def count_yes_replies(l: list) -> int:
    return l.count(True)


def count_false_replies(l: list) -> int:
    return l.count(False)


def generate_tsetlins(n_tsetlins_per_clause: int, n_states_per_decision: int) -> list:
    tsetlins = []
    # Make every other Tsetlin's consider inverted.
    for i in range(n_tsetlins_per_clause):
        if i % 2 == 0:
            tsetlins.append(Tsetlin(n_states_per_decision, False))
        else:
            tsetlins.append(Tsetlin(n_states_per_decision, True))

    return tsetlins


def generate_clauses(n_clauses: int, n_tsetlins_per_clause: int, n_states_per_decision: int) -> list:
    clauses = {
        POSITIVE: [],
        NEGATIVE: []
    }
    for i in range(n_clauses):
        positive_clause = Clause(True,  generate_tsetlins(n_tsetlins_per_clause, n_states_per_decision))
        negative_clause = Clause(False, generate_tsetlins(n_tsetlins_per_clause, n_states_per_decision))

        clauses[POSITIVE].append(positive_clause)
        clauses[NEGATIVE].append(negative_clause)

    return clauses

def get_training_data(t: str) -> list:
    filename = "training_data.json"
    if filename:
        with open(filename, 'r') as f:
            return json.load(f)[t]



def obtain_conjunctive_clauses(clause, tr):
    x1 = tr[0]
    x2 = tr[1]
    y = tr[2]

    input_list = [x1, x1, x2, x2]

    # CHECK STATE OF EACH AUTOMATA
    # BUT ONLY 2 AT A TIME, INVERSE AND NON INVERSE
    print(f'{x1} - {x2}')
    conjuction = []
    for index, ta in enumerate(clause.tsetlins):
        # EACH TA.
        if ta.is_include():
            conjuction.append(ta.literal_value(input_list[index]))
        else:
            print("-- Exclude --")

    print("=========== CONJUNCTION ============")
    print(conjuction)

        # X1 -> X2 -> -X1 -> -X2
        # FIRST TWO,    CHECK x1
        # Second Two,   Check x2

        #print(f'eval {ta.literal_value(x1)} - Include? {ta.is_include()}')
        #print("Each TA running")




    # WE WANT TO FIGURE OUT WHAT x1 | x2 to Inclue, and what if INVERSE OR NO
    # ta1_opinion = team[0].consider_literal(x1)
    # ta2_opinion = team[1].consider_literal(x1)
    # ta3_opinion = team[2].consider_literal(x2)
    # ta4_opinion = team[3].consider_literal(x2)

    # res = [ta1_opinion, ta2_opinion, ta3_opinion, ta4_opinion]

    # print(f'Opinions: ta1: {ta1_opinion} ta2: {ta2_opinion} ta3: {ta3_opinion} ta4: {ta4_opinion}')
    return conjuction



def train_tsetlin_machine():
    n_tsetlins_per_clause = 4
    n_clauses = 2
    s = 3.9
    t = 1
    n_states_per_decision = 3
    # 0 1 0 1 1 1 0 1 1 1 1 0
    bits1 = (0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1)
    #bits2 = (0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0)
    bits2 = [False, False, False, False, False, True, True, True, False, True, True, False]

    conjunction_test = [False, True, False, True]
    res = eval_xor(conjunction_test)
    print(res)
    print(eval_and(conjunction_test))
    print(eval_or(conjunction_test))
    # Produce Machines
    # Every even item in list is +
    # Every odd  item is -
    # Collect each team (4x TA in each)
    clauses = generate_clauses(n_clauses, n_tsetlins_per_clause, n_states_per_decision)
    training_data = get_training_data('XOR')
    # LOOP TRAIN HERE...
    for i in range(10):

        # GetNextTrainingExample
        tr = training_data[i % len(training_data)]

        #print(tr[0])
        data = tr.copy()
        del data[-1]

        #print("DATA: " + str(data))
        y = tr[2]
        c = {
            POSITIVE: [],
            NEGATIVE: []
        }
        for positive_clauses in clauses[POSITIVE]:
            c[POSITIVE].append(obtain_conjunctive_clauses(positive_clauses, tr))

        for negative_clauses in clauses[NEGATIVE]:
            c[NEGATIVE].append(obtain_conjunctive_clauses(negative_clauses, tr))

        votes = 0
        # print(c)
        ## WHAT DID IT MEAN?
        for conjunction in c[POSITIVE]:
            # print(eval_or(conjunction)) # LOOKING FOR TRUE (Y=1)
            con_vote = eval_xor(conjunction)
            if(con_vote):
                votes = votes + 1

        for conjunction in c[NEGATIVE]:
            # print(eval_or(conjunction)) # LOOKING FOR FALSE (Y=0)
            con_vote = eval_xor(conjunction)
            if(con_vote):
                votes = votes - 1


        # FEEDBACK
        for positive_clause in clauses[POSITIVE]:
            if y == 1:
                if random.random() <= type_1_threshold(t, votes):
                    type_1_feedback(data, positive_clause)
                    # TEAM IS GOING THROUGH Type 1 FEEDBACK
                    print("TYPE I FEEDBACK")


            else:
                if random.random() <= type_2_threshold(t, votes):
                    print("TYPE II FEEDBACK")

        for negative_clauses in clauses[NEGATIVE]:
            if(y == 1):
                if random.random() <= type_2_threshold(t, votes):

                    print("NEGATIVE TYPE II FEEDBACK")
                    print(negative_clauses)
            else:
                if random.random() <= type_1_threshold(t, votes):
                    type_1_feedback(data, negative_clauses)
                    print("NEGATIVE TYPE I FEEDBACK")




if __name__ == '__main__':
    n_tsetlins_per_clause = 4
    n_clauses = 2
    s = 3.9
    t = 1
    n_states_per_decision = 3
    train_tsetlin_machine()
    COLOR_WHEEL = ['k', 'g', 'm', 'r', 'c', 'b']
    n_rounds = 500

    plots = []
    total_result = []

    # Create instances of the individual sensors
    # tsetlins = [Tsetlin(n_states_per_decision, invert_bool) for i in range(n_tsetlins_per_clause)]

    tsetlins = []
    """
    for i in range(n_tsetlins_per_clause):
        if i % 2 == 0:
            tsetlins.append(Tsetlin(n_states_per_decision, give_bool))
        else:
            tsetlins.append(Tsetlin(n_states_per_decision, invert_bool))
    """

    results = []
    sum_yes_replies = []

    for round_index in range(n_rounds):
        round_decisions = [tsetlin.make_decision() for tsetlin in tsetlins]
        round_yes_replies = count_yes_replies(round_decisions)
        round_penalty_limit = get_penalty_limit(round_yes_replies)
        [give_feedback(round_penalty_limit, tsetlin) for tsetlin in tsetlins]
