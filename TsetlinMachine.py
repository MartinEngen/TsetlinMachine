import time

from Clause import generate_clauses
from utils import get_training_data, eval_xor, type_1_feedback, type_2_feedback
import eel


def calculate_clause_output(clauses: list, sample_x: list) -> list:
    all_clause_outputs = []
    for clause in clauses:
        clause_output = 1
        all_exclude = 1

        for index, x in enumerate(sample_x):
            # Get Tsetlins in charge of this input
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
    stacked_bar_chart_n_groups = 5

    # Initiate some containers
    training_accuracy = []
    percent_on_all_inputs = []

    accum_votes_categories = [f'0 to {rounds/stacked_bar_chart_n_groups}']
    accum_votes_series = [{
        'name': '0 votes against target 0',
        'data': [0 for _ in range(stacked_bar_chart_n_groups)]
    },{
        'name': '1 votes against target 0',
        'data': [0 for _ in range(stacked_bar_chart_n_groups)]
    },
    {
        'name': '2 votes against target 0',
        'data': [0 for _ in range(stacked_bar_chart_n_groups)]
    },
    {
        'name': '0 votes against target 1',
        'data': [0 for _ in range(stacked_bar_chart_n_groups)]
    },
    {
        'name': '1 votes against target 1',
        'data': [0 for _ in range(stacked_bar_chart_n_groups)]
    },
    {
        'name': '2 votes against target 1',
        'data': [0 for _ in range(stacked_bar_chart_n_groups)]
    }]

    accum_votes_series_index = 0

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

        if i % len(training_data) == 0 and i != 0:
            last_4_rounds_accuracy = sum(training_accuracy[-4:]) / 4
            percent_on_all_inputs.append(last_4_rounds_accuracy)
        else:
            percent_on_all_inputs.append(None)


        if i != 0 and i % int(rounds/stacked_bar_chart_n_groups) == 0:
            accum_votes_series_index += 1
            accum_votes_categories.append(f'{int((rounds / stacked_bar_chart_n_groups) * accum_votes_series_index)} to '
                                          f'{int((rounds / stacked_bar_chart_n_groups) * (accum_votes_series_index + 1))}')

        # Collect data
        if sum_votes == 0 and sample_y == 0:
            accum_votes_series[0]['data'][accum_votes_series_index] += 1

        elif sum_votes == 1 and sample_y == 0:
            accum_votes_series[1]['data'][accum_votes_series_index] += 1

        elif sum_votes == 2 and sample_y == 0:
            accum_votes_series[2]['data'][accum_votes_series_index] += 1

        elif sum_votes == 0 and sample_y == 1:
            accum_votes_series[3]['data'][accum_votes_series_index] += 1

        elif sum_votes == 1 and sample_y == 1:
            accum_votes_series[4]['data'][accum_votes_series_index] += 1

        elif sum_votes == 2 and sample_y == 1:
            accum_votes_series[5]['data'][accum_votes_series_index] += 1


        if sum_votes > 0 and sample_y == 1 or sum_votes == 0 and sample_y == 0:
            training_accuracy.append(1)
        else:
            training_accuracy.append(0)

    sum_correct = sum(training_accuracy)
    percent_correct = sum_correct/len(training_accuracy)

    training_result_data = {
        'percent_on_all_inputs': percent_on_all_inputs,
        'accum_votes_series': accum_votes_series,
        'accum_votes_categories': accum_votes_categories
    }

    return training_result_data


def isCorrectClauseLength(n):
    if n == 2:
        return True
    else:
        return False

if __name__ == '__main__':
    eel.init('web') # GUI related

    n_tsetlins_per_clause = 4  # Must be 2x input
    n_clauses = 2  # Must be same amount as input
    """
     As a rule of thumb, a large s leads to more ”ﬁne grained” clauses, that is, clauses with more literals, 
     while a small s produces ”coarser” clauses, with fewer literals included.
    """
    s = 3.9
    t = 1  # Not used, but is indication of how big chance for a feedback to occur based on sum_votes
    n_states_per_decision = 100
    training_rounds = 1000

    bit_operators_to_learn = ['xor', 'and', 'or']


    results_dict = {
        'xor': {
            'title': 'XOR Result',
            'ta_states': []
        },
        'and': {
            'title': 'AND Result',
            'ta_states': []
        },
        'or': {
            'title': 'OR Result',
            'ta_states': []

        }
    }


    @eel.expose
    def run_operators():
        for operator in bit_operators_to_learn:

            clauses = generate_clauses(n_clauses, n_tsetlins_per_clause, n_states_per_decision)
            training_result_data = train_clauses(clauses, training_rounds, operator)

            print("***  Training Done ****")
            print(f'Operator {operator}')
            clauses[0].show_current_clause()
            clauses[0].show_states_per_ta()

            clauses[1].show_current_clause()
            clauses[1].show_states_per_ta()

            r = results_dict[operator]
            r['ta_states'] = []

            round_accuracy = {
                'name': f'Training Result {operator}',
                'data': training_result_data['percent_on_all_inputs']
            }

            r['round_accuracy'] = round_accuracy
            r['accum_votes_series'] = training_result_data['accum_votes_series']
            r['accum_votes_categories'] = training_result_data['accum_votes_categories']

            for index, clause in enumerate(clauses):
                ta_states = clause.get_ta_states_with_literals()
                clause_name = f'clause {index + 1}'
                data = []
                for ta_state in ta_states:
                    data.append(ta_state['state'])

                ta_states_graph_data = {
                    'name': clause_name,
                    'data': [d - n_states_per_decision for d in data]
                }
                r['ta_states'].append(ta_states_graph_data)


    @eel.expose
    def force_correct_result():
        for operator in bit_operators_to_learn:
            while True:
                clauses = generate_clauses(n_clauses, n_tsetlins_per_clause, n_states_per_decision)
                training_result_data = train_clauses(clauses, training_rounds, operator)

                clause_0_sum = clauses[0].sum_included_literals()
                clause_1_sum = clauses[1].sum_included_literals()

                clause_0 = clauses[0].current_clause()
                clause_1 = clauses[1].current_clause()

                if isCorrectClauseLength(clause_0_sum) and isCorrectClauseLength(clause_1_sum) and clause_0 != clause_1:
                    print("***  Training Done ****")
                    print(f'Operator {operator}')
                    clauses[0].show_current_clause()
                    clauses[0].show_states_per_ta()

                    clauses[1].show_current_clause()
                    clauses[1].show_states_per_ta()

                    r = results_dict[operator]
                    r['ta_states'] = []


                    round_accuracy = {
                        'name': f'Training Result {operator}',
                        'data': training_result_data['percent_on_all_inputs']
                    }

                    r['round_accuracy'] = round_accuracy
                    r['accum_votes_series'] = training_result_data['accum_votes_series']
                    r['accum_votes_categories'] = training_result_data['accum_votes_categories']

                    for index, clause in enumerate(clauses):
                        ta_states = clause.get_ta_states_with_literals()
                        clause_name = f'clause {index + 1}'
                        data = []
                        for ta_state in ta_states:
                            data.append(ta_state['state'])

                        ta_states_graph_data = {
                            'name': clause_name,
                            'data': [d - n_states_per_decision for d in data]
                        }
                        r['ta_states'].append(ta_states_graph_data)

                    break


    force_correct_result()
    @eel.expose  # Expose this function to Javascript
    def say_hello_py(x):
        print('Hello from %s' % x)

        return 'hello'

    @eel.expose
    def get_xor():
        xor_result = results_dict['xor']
        return {
            'result': xor_result
        }

    @eel.expose
    def get_and():
        and_result = results_dict['and']
        return {
            'result': and_result
        }

    @eel.expose
    def get_or():
        or_result = results_dict['or']
        return {
            'result': or_result
        }

    eel.start('main.html')
