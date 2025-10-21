# Database Middleware

This package provides database-related middleware components.

## 📁 Components

### ConnectionPoolMiddleware
- Database connection pool management
- Configurable pool sizes
- Connection lifecycle management

### TransactionManagerMiddleware
- Automatic transaction management
- Rollback on errors
- Transaction isolation levels

### QueryOptimizerMiddleware
- Query performance monitoring
- Automatic query optimization
- Slow query detection

## 🔧 Usage

```python
from middleware.database import (
    ConnectionPoolMiddleware,
    TransactionManagerMiddleware,
    QueryOptimizerMiddleware
)

app.add_middleware(ConnectionPoolMiddleware, pool_size=10)
app.add_middleware(TransactionManagerMiddleware, auto_commit=True)
app.add_middleware(QueryOptimizerMiddleware, enable_profiling=True)
```

## 📋 TODO

- [ ] Implement multi-database support
- [ ] Add connection health monitoring
- [ ] Implement query result caching
- [ ] Add database migration support
- [ ] Support for read/write splitting