import random
from functools import reduce
from operator import xor, or_, and_


def eval_and(conjunction):
    return reduce(and_, conjunction) #all(conjunction)


def eval_or(conjunction):
    return reduce(or_, conjunction) #return any(conjunction)


def eval_xor(conjunction):
    if not conjunction:
        return False
    else:
        return reduce(xor, conjunction)


def medium_chance(s):
    return random.random() < (s - 1) / s

def small_chance(s):
    return random.random() < 1 / s

def type_1_feedback(inputs: list, clause, clause_result, s):
    # Fights False Negatives
    # Clause was 1 or TRUE
    if clause_result:
        # One Way
        for index, current_input in enumerate(inputs):
            tsetlins = clause.get_x_ta(index)
            # print(f'Length: {len(tsetlins)} - index: {index}')
            ######## NORMAL ########
            is_include = tsetlins[0].is_include

            if is_include:
                if current_input == 1:
                    if random.random() < (s-1)/s:
                        # Give Reward
                        tsetlins[0].reward()

            else:
                if current_input == 1:
                    if random.random() < (s-1)/s:
                        tsetlins[0].penalize()
                        # Give Penalty
                else:
                    if random.random() < 1 / s:
                        tsetlins[0].reward()

            ######## INVERSE #############
            inverse_is_include = tsetlins[1].is_include
            if inverse_is_include:
                # Inverse Right side
                if current_input == 0:
                    if random.random() < (s - 1) / s:
                        # Give Reward
                        tsetlins[1].reward()

            else:
                # Inverse Right side
                if current_input == 0:
                    if random.random() < (s - 1) / s:
                        tsetlins[1].penalize()
                        # Give Penalty
                else:
                    if random.random() < 1 / s:
                        tsetlins[1].reward()

    else:
        for index, current_input in enumerate(inputs):
            # print(f'current input -> {current_input}')
            tsetlins = clause.get_x_ta(index)
            # print(f'Length: {len(tsetlins)} - index: {index}')
            ######## NORMAL ########
            is_include = tsetlins[0].is_include

            if is_include:
                if small_chance(s):
                    tsetlins[0].penalize()

            # Exclude
            else:
                if small_chance(s):
                    tsetlins[0].reward()

            ######## INVERSE #############
            inverse_is_include = tsetlins[1].is_include
            if inverse_is_include:
                # Inverse Right side
                if random.random() < (s - 1) / s:
                    # Give Reward
                    tsetlins[1].reward()

            else:
                if small_chance(s):
                    tsetlins[1].reward()


def type_2_feedback(inputs: list, clause, clause_result, s):
    # Fights False Positive,
    # Clause was 1 or TRUE
    if clause_result:
        # One Way
        for index, current_input in enumerate(inputs):
            tsetlins = clause.get_x_ta(index)

            ######## NORMAL ########
            is_include = tsetlins[0].is_include

            if is_include:
                # No Action
                pass

            else:
                if current_input == 0:
                    tsetlins[0].penalize()

            ######## INVERTED ########
            is_include = tsetlins[1].is_include

            if is_include:
                pass

            else:
                if current_input == 1:
                    tsetlins[0].penalize()


def type_1_threshold(t, vote_sum):
    return (t - max(-t, min(t, vote_sum)))/(2 * t)


def type_2_threshold(t, vote_sum):
    return (t + max(-t, min(t, vote_sum)))/(2 * t)
