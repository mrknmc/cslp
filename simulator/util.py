

def log(msg, level=None, label=None):
    """
    Print to stdout
    """
    if label is not None:
        print("{0}: {1}".format(label, msg))
