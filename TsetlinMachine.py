from Clause import generate_clauses
from utils import get_training_data, eval_xor, type_1_feedback, type_2_feedback


def calculate_clause_output(clauses: list, sample_x: list) -> list:
    all_clause_outputs = []
    for clause in clauses:
        clause_output = 1
        all_exclude = 1

        for index, x in enumerate(sample_x):
            # Get tsetlins in charge of this input
            ta = clause.tsetlins[index * 2]
            ta_negated = clause.tsetlins[(index * 2)+1]

            action_include = ta.is_include()
            action_include_negated = ta_negated.is_include()

            all_exclude = all_exclude and not(action_include == 1 or action_include_negated == 1)
            if (action_include == 1 and x == 0) or (action_include_negated == 1 and x == 1):
                clause_output = 0
                break

        clause_output = clause_output and not (all_exclude == 1)
        all_clause_outputs.append(clause_output)

    # Maps the list to only 1s and 0s
    return list(map(int, all_clause_outputs))


def train_clauses(clauses: list, rounds: int, current_operation: str):
    training_data = get_training_data(current_operation)
    for i in range(rounds):
        tr = training_data[i % len(training_data)]

        # X with only 2 bit and y removed
        sample_x = tr[:len(tr)-1]
        sample_y = tr[len(tr)-1]

        # Get Clause output
        clause_outputs = calculate_clause_output(clauses, sample_x)
        sum_votes = sum(clause_outputs)

        # sample_y is target for current sample
        if sample_y == 1:
            for index, res in enumerate(clause_outputs):
                current_clause = clauses[index]
                type_1_feedback(sample_x, current_clause, res, s)

            # True Positive
        # sample_y == 0
        else:
            # False Positives
            if sum_votes > 0:
                for index, res in enumerate(clause_outputs):
                    if res:
                        current_clause = clauses[index]
                        type_2_feedback(sample_x, current_clause, res, s)
            # True Negatives
            else:
                pass


if __name__ == '__main__':
    n_tsetlins_per_clause = 4  # Must be 2x input
    n_clauses = 2  # Must be same amount as input
    """
     As a rule of thumb, a large s leads to more ”ﬁne grained” clauses, that is, clauses with more literals, 
     while a small s produces ”coarser” clauses, with fewer literals included.
    """
    s = 3.9
    t = 1  # Not used, but is indication of how big chance for a feedback to occur based on sum_votes
    n_states_per_decision = 100
    training_rounds = 10000

    bit_operators_to_learn = ['XOR', 'AND', 'OR']

    for operator in bit_operators_to_learn:

        clauses = generate_clauses(n_clauses, n_tsetlins_per_clause, n_states_per_decision)
        train_clauses(clauses, training_rounds, operator)

        print("*** TRANING IS DONE.. ****")
        print(f'Operator {operator}')
        clauses[0].show_current_clause()
        clauses[0].show_states_per_ta()

        clauses[1].show_current_clause()
        clauses[1].show_states_per_ta()

