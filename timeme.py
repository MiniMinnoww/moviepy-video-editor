import time


def timeme(function, _return="time", *args):
    """
    Simple function that measures the time a function takes.
    Use:

    from timeme import timeme

    def foo():
        return 1
    timeme(foo, 'time')

    To add arguments to your function you will need to fill in the function, _return and argument, then add your functions arguments at the end.
    Use:

    from timeme import timeme

    def foo(x, y, z):
        return x + y + z

    timeme(foo, 'time', 40, 50, 60)

    Where 40, 50, 60 will correspond to the argument x, y, z


    :param function: The function to run
    :param _return: The type of return. Can be 'time' (the time taken), 'return' (the return value of the function) or both (return value and time taken)
    :return: Time taken / Return value of function
    """
    start = time.time()
    ret = function(*args)
    end = time.time() - start
    if _return == "time":
        return end
    elif _return == "return":
        return ret
    elif _return == "both":
        return ret, end
    else:
        raise ValueError("_return must be 'time', 'return', or 'both")


class stopwatch:
    """
    Simple class to time something. You can call start() to start timer, and stop() to stop timer and return stopwatch value
    """
    def __init__(self):
        self.startTime = 0

    def start(self):
        self.startTime = time.time()

    def stop(self):
        return time.time() - self.startTime