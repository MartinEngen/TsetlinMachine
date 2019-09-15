import json
import random

from Clause import Clause
from Tsetlin import Tsetlin
from utils import eval_xor, type_1_feedback, type_2_feedback, type_1_threshold, type_2_threshold


def generate_tsetlins(n_tsetlins_per_clause: int, n_states_per_decision: int) -> list:
    tsetlins = []
    # Make every other Tsetlin's consider inverted.
    for i in range(n_tsetlins_per_clause):
        print(int(i/2))
        if i % 2 == 0:
            tsetlins.append(Tsetlin(n_states_per_decision, False, int(i/2)))
        else:
            tsetlins.append(Tsetlin(n_states_per_decision, True, int(i/2)))

    return tsetlins


def generate_clauses(n_clauses: int, n_tsetlins_per_clause: int, n_states_per_decision: int) -> list:
    return [Clause(generate_tsetlins(n_tsetlins_per_clause, n_states_per_decision)) for _ in range(n_clauses)]


def get_training_data(t: str) -> list:
    filename = "training_data.json"
    if filename:
        with open(filename, 'r') as f:
            return json.load(f)[t]


def obtain_conjunctive_clauses(clause, tr):
    x1 = tr[0]
    x2 = tr[1]

    input_list = [x1, x1, x2, x2]

    # CHECK STATE OF EACH AUTOMATA
    # BUT ONLY 2 AT A TIME, INVERSE AND NON INVERSE
    conjuction = []
    for index, ta in enumerate(clause.tsetlins):
        if ta.is_include():
            conjuction.append(ta.literal_value(input_list[index]))

    return conjuction


if __name__ == '__main__':
    n_tsetlins_per_clause = 4
    n_clauses = 2
    s = 2.9
    t = 1
    n_states_per_decision = 3

    clauses = generate_clauses(n_clauses, n_tsetlins_per_clause, n_states_per_decision)
    training_data = get_training_data('XOR')

    # Train here.
    for i in range(1):
        tr = training_data[i % len(training_data)]
        data = tr.copy()
        del data[-1]

        y = tr[2]

        clauses_output = []
        for clause in clauses:
            clauses_output.append(obtain_conjunctive_clauses(clause, tr))

        votes = []
        for c in clauses_output:
            votes.append(eval_xor(c))

        sum_votes = sum(votes)

        if y == 1:
            if sum_votes == 0:
                for index, res in enumerate(votes):
                    current_clause = clauses[index]
                    type_1_feedback(data, current_clause, res, s)

        else:
            if sum_votes > 0:
                ## False Positive
                for index, res in enumerate(votes):
                    if res:
                        current_clause = clauses[index]
                        type_2_feedback(data, current_clause, res, s)

            else:
                pass

    print("*** TRANING IS DONE.. ****")
    clauses[0].show_current_clause()
    clauses[0].show_states_per_ta()

    clauses[1].show_current_clause()
    clauses[1].show_states_per_ta()
