"""
Database middleware package.
"""

# Safe imports with fallbacks
__all__ = []

try:
    from .connection_pool import ConnectionPoolMiddleware
    __all__.append("ConnectionPoolMiddleware")
except ImportError as e:
    print(f"Warning: Could not import connection_pool: {e}")

try:
    from .transaction_manager import TransactionManagerMiddleware
    __all__.append("TransactionManagerMiddleware")
except ImportError as e:
    print(f"Warning: Could not import transaction_manager: {e}")

try:
    from .query_optimizer import QueryOptimizerMiddleware
    __all__.append("QueryOptimizerMiddleware")
except ImportError as e:
    print(f"Warning: Could not import query_optimizer: {e}")

# Initialize __all__ if empty
if not __all__:
    __all__ = []
