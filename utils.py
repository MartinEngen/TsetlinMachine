from functools import reduce
from operator import xor, or_, and_


def eval_and(conjunction):
    return reduce(and_, conjunction) #all(conjunction)


def eval_or(conjunction):
    return reduce(or_, conjunction) #return any(conjunction)


def eval_xor(conjunction):
    return reduce(xor, conjunction)


def type_1_feedback(inputs: list):
    for input in len(inputs):
        print("EACH INPUT (X1 AND X1)")


def type_1_threshold(t, vote_sum):
    return (t - max(-t, min(t, vote_sum)))/(2 * t)


def type_2_threshold(t, vote_sum):
    return (t + max(-t, min(t, vote_sum)))/(2 * t)