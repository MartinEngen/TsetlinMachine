import random
import time
from builtins import print

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import statistics
import numpy as np
import json

from utils import eval_xor, eval_and, eval_or, type_1_threshold, type_1_feedback, type_2_threshold, type_2_feedback

POSITIVE = 'positive'
NEGATIVE = 'negative'


class Clause:
    def __init__(self, polarity: bool, tsetlins: list):
        # Polarity Focus (polarity = True => y=1 | polarity = False => y=0)
        self.polarity = polarity

        # This Clause's assigned team of tsetlins
        self.tsetlins = tsetlins

    def get_x_ta(self, x_num):
        return [self.tsetlins[x_num * 2], self.tsetlins[(x_num * 2) + 1]]


    def show_current_clause(self):
        c = []
        for ta in self.tsetlins:
            if ta.is_include():
                st = ''
                if ta.should_invert:
                    st = '-'
                c.append(f'{st}X{ta.designated_literal}')
        print(c)


class Tsetlin:
    def __init__(self, n, should_invert, designated_literal):
        # n is the number of states per action
        self.n = n
        # Initial state selected randomly
        self.state = random.choice([self.n, self.n+1])

        self.should_invert = should_invert

        self.designated_literal = designated_literal


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

    def is_include(self):
        if self.state > self.n:
            return True
        else:
            return False

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
    # First two is x0 -> next is x1
    tsetlins = []
    # Make every other Tsetlin's consider inverted.
    for i in range(n_tsetlins_per_clause):
        if i % 2 == 0:
            tsetlins.append(Tsetlin(n_states_per_decision, False, int(i/2)))
        else:
            tsetlins.append(Tsetlin(n_states_per_decision, True, int(i/2)))

    for i, ta in enumerate(tsetlins):
        print(f'Ta {i} - x:{ta.designated_literal} - should_invert: {ta.should_invert}')
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
    conjuction = []
    for index, ta in enumerate(clause.tsetlins):
        # EACH TA.
        if ta.is_include():
            conjuction.append(ta.literal_value(input_list[index]))

    return conjuction

def print_clause_states(clause):
    for index, ta in enumerate(clause.tsetlins):
        print(f'Ta # {index} -> {ta.state}')

def train_tsetlin_machine():
    n_tsetlins_per_clause = 4
    n_clauses = 2
    s = 3.9
    t = 1
    n_states_per_decision = 100
    # 0 1 0 1 1 1 0 1 1 1 1 0
    bits1 = (0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1)
    #bits2 = (0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0)
    bits2 = [False, False, False, False, False, True, True, True, False, True, True, False]

    conjunction_test = [False, True, False, True]
    res = eval_xor(conjunction_test)
    clauses = generate_clauses(n_clauses, n_tsetlins_per_clause, n_states_per_decision)
    training_data = get_training_data('XOR')
    # LOOP TRAIN HERE...
    success = 0
    for i in range(10):
        tr = training_data[i % len(training_data)]
        data = tr.copy()
        del data[-1]

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
        positive_results = []
        negative_results = []
        for conjunction in c[POSITIVE]:
            con_vote = eval_xor(conjunction)
            positive_results.append(con_vote)
            if(con_vote):
                votes = votes + 1

        for conjunction in c[NEGATIVE]:
            con_vote = eval_xor(conjunction)
            negative_results.append(con_vote)

            if(con_vote):
                votes = votes - 1
        print(f'{votes} vote when y={y}')
        if(i > 1000):
            if votes > 0 and y == 1:
                success = success + 1
            if votes <= 0 and y == 0:
                success = success + 1

        # FEEDBACK
        for index, positive_clause in enumerate(clauses[POSITIVE]):
            positive_clause.show_current_clause()
            if(index == 0):
                pass
                #print("================= FIRST OF POSITIVE CLAUSES =========================")
                #print_clause_states(positive_clause)
            if y == 1:
                if random.random() <= type_1_threshold(t, votes):
                    clause_result = positive_results[index]
                    type_1_feedback(data, positive_clause, clause_result, s)
                    # TEAM IS GOING THROUGH Type 1 FEEDBACK
                    # print("TYPE I FEEDBACK")
            else:
                if random.random() <= type_2_threshold(t, votes):
                    clause_result = positive_results[index]
                    type_2_feedback(data, positive_clause, clause_result, s)
                    # print("TYPE II FEEDBACK")

        for index, negative_clause in enumerate(clauses[NEGATIVE]):
            if(index == 100):
                print("================= FIRST OF NEGATIVE CLAUSES =========================")
                print_clause_states(negative_clause)

            if y == 1:
                if random.random() <= type_2_threshold(t, votes):
                    clause_result = negative_results[index]
                    type_2_feedback(data, negative_clause, clause_result, s)
                    # print("NEGATIVE TYPE II FEEDBACK")
                    # print(negative_clauses)
            else:
                if random.random() <= type_1_threshold(t, votes):
                    clause_result = negative_results[index]
                    type_1_feedback(data, negative_clause, clause_result, s)



if __name__ == '__main__':
    n_tsetlins_per_clause = 4
    n_clauses = 2
    s = 3.9
    t = 1
    n_states_per_decision = 3

    train_tsetlin_machine()



