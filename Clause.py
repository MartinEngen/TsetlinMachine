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

    def get_ta_states_with_literals(self):
        result = []

        for ta in self.tsetlins:
            state = ta.state
            is_include = ta.is_include()
            literal = ta.designated_literal
            is_inverting = ta.should_invert

            ta_status = {
                'state': state,
                'is_include': is_include,
                'literal': literal,
                'is_inverting': is_inverting
            }

            result.append(ta_status)

        return result

    def sum_included_literals(self):
        sum = 0
        for ta in self.tsetlins:
            if ta.is_include():
                sum = sum + 1

        return sum

    def current_clause(self):
        c = []
        for ta in self.tsetlins:
            if ta.is_include():
                st = ''
                if ta.should_invert:
                    st = '-'
                c.append(f'{st}X{ta.designated_literal}')
        return c


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
