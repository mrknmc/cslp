
class SimulationException(Exception):
    """Common base-class so can catch both of the exceptions below."""
    pass

class InputError(SimulationException):
    """This exception is raised when the input contains an error."""
    pass


class InputWarning(SimulationException):
    """This exception is raised when the input contains something
    that requires a warning."""
    pass
