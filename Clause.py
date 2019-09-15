from Tsetlin import Tsetlin


class Clause:
    def __init__(self, tsetlins: list):
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

    def show_states_per_ta(self):
        states = []

        for ta in self.tsetlins:
            st=''
            if ta.should_invert:
                st = '-'
            states.append(f'{st}X{ta.designated_literal}({ta.state}) ({ta.is_include()})')

        print(states)


def generate_tsetlins(n_tsetlins_per_clause: int, n_states_per_decision: int) -> list:
    tsetlins = []
    # Make every other Tsetlin inverted.
    # Tsetlins will be created in pairs to consider the same literal (one inverted and one normally)
    for i in range(n_tsetlins_per_clause):
        if i % 2 == 0:
            tsetlins.append(
                Tsetlin(n_states_per_decision, False, int(i/2))
            )
        else:
            tsetlins.append(
                Tsetlin(n_states_per_decision, True, int(i/2))
            )

    return tsetlins


def generate_clauses(n_clauses: int, n_tsetlins_per_clause: int, n_states_per_decision: int) -> list:
    return [Clause(
        generate_tsetlins(n_tsetlins_per_clause, n_states_per_decision)
    ) for _ in range(n_clauses)]
