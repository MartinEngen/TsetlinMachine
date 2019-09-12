import random
import time
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import statistics
import numpy as np

class Tsetlin:
    def __init__(self, n):
        # n is the number of states per action
        self.n = n
        # Initial state selected randomly
        self.state = random.choice([self.n, self.n+1])

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

if __name__ == '__main__':
    n_tsetlins_per_clause = 4
    n_clauses = 4
    s = 3.9
    t = 1
    n_states_per_decision = 3

    COLOR_WHEEL = ['k', 'g', 'm', 'r', 'c', 'b']
    n_rounds = 500

    plots = []
    total_result = []

    # Create instances of the individual sensors
    tsetlins = [Tsetlin(n_states_per_decision) for _ in range(n_tsetlins_per_clause)]
    results = []
    sum_yes_replies = []

    for round_index in range(n_rounds):
        round_decisions = [tsetlin.make_decision() for tsetlin in tsetlins]
        round_yes_replies = count_yes_replies(round_decisions)
        round_penalty_limit = get_penalty_limit(round_yes_replies)
        [give_feedback(round_penalty_limit, tsetlin) for tsetlin in tsetlins]