import logging

logger = logging.getLogger(__name__)


def log_inputs(func):
    # Decorator to log function inputs
    def wrapper(*args, **kwargs):
        arg_types = [type(arg) for arg in args]
        kwarg_types = {k: type(v) for k, v in kwargs.items()}
        logger.info(f"Running {func.__name__} with args: {args}, types: {arg_types}")
        logger.info(f"and kwargs: {kwargs}, types: {kwarg_types}")
        return func(*args, **kwargs)
    return wrapper
