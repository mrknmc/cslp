import random


def log(msg, level=None, label=None):
    """
    Print to stdout
    """
    label = '{0}: '.format(label) if label else ''
    print('{0}{1}'.format(label if label else '', msg))


def weighted_choice(iterable, key=None):
    """
    This function picks an item in a list with a weigh of its rate
    against the sum of all the rates.

    The key parameter can be used to specify which item of the tuple
    to use as the weight.
    """
    if not key:
        key = lambda i: i[0]
    totals = []
    running_total = 0

    for i in iterable:
        running_total += key(i)
        totals.append(running_total)

    rnd = random.random() * running_total
    for i, total in enumerate(totals):
        if rnd < total:
            return iterable[i]
