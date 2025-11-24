# src/utils/transactions.py
import functools
import time
from typing import Optional


class TransactionSession:
    """
    Context Manager that simulates a database transaction.
    If an exception occurs inside the 'with' block, it rolls back.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.active = False
        self.status = "PENDING"

    def __enter__(self):
        """Called when entering the 'with' block."""
        print(f"--- [Session {self.session_id}] START: Locking Resources ---")
        self.active = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called when exiting the 'with' block.
        exc_type is not None if an error occurred.
        """
        if exc_type:
            self.rollback(exc_val)
            # Return True to suppress the exception (optional),
            # or False to let it bubble up (usually better for APIs).
            return False
        else:
            self.commit()

    def commit(self):
        self.status = "COMMITTED"
        print(f"--- [Session {self.session_id}] COMMIT: Changes saved ---")

    def rollback(self, error):
        self.status = "ROLLED_BACK"
        print(f"!!! [Session {self.session_id}] ROLLBACK: Reverting due to error: {error} !!!")


# --- The Advanced Decorator ---

def transactional(func):
    """
    Decorator that wraps a function in a TransactionSession.
    Uses functools.wraps to keep the original function's name/docstring.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # We generate a fake session ID for this example
        current_time = int(time.time())
        session_id = f"TX-{current_time}"

        with TransactionSession(session_id):
            return func(*args, **kwargs)

    return wrapper