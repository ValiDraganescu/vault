# this function logs the class name and the function name
import time

def log(function):
    def wrapper(*args, **kwargs):
        print(f"{args[0].__class__.__name__}.{function.__name__}")
        return function(*args, **kwargs)
    return wrapper


def timed_log(show_time: bool | None = False):
    def decorator(function):
        def wrapper(*args, **kwargs):
            log_str = f"{args[0].__class__.__name__}.{function.__name__}"
            start_time = time.time()
            result = function(*args, **kwargs)
            if show_time:
                end_time = time.time()
                elapsed_time = end_time - start_time
                log_str = f"{log_str}({elapsed_time})"
            print(log_str)
            return result
        return wrapper
    return decorator