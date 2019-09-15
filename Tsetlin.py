import random


class Tsetlin:
    def __init__(self, n, should_invert, designated_literal):
        # n is the number of states per action
        self.n = n
        # Initial state selected randomly
        self.state = random.choice([self.n, self.n+1])
        self.should_invert = should_invert
        self.designated_literal = designated_literal


    def reward(self):
        if self.state <= self.n and self.state > 1:
            self.state -= 1
        elif self.state > self.n and self.state < 2*self.n:
            self.state += 1

    def penalize(self):
        if self.state <= self.n:
            self.state += 1
        elif self.state > self.n:
            self.state -= 1

    def is_include(self):
        if self.state <= self.n:
            return 0
        else:
            return 1

    def literal_value(self, literal):
        if self.should_invert:
            return int(not literal)
        else:
            return int(literal)


