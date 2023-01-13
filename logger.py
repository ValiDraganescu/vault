# this function logs the class name and the function name

def log(function):
    def wrapper(*args, **kwargs):
        print(f"{args[0].__class__.__name__}.{function.__name__}")
        return function(*args, **kwargs)
    return wrapper