# Middleware Package

This directory contains all middleware components for the WEB Final application.

## 📁 Structure

```
middleware/
├── config/          # Middleware configuration
├── auth/            # Authentication & Authorization
├── security/        # Security middleware
├── logging/         # Logging & Monitoring
├── caching/         # Caching middleware
├── api/             # API-specific middleware
├── database/        # Database middleware
└── utils/           # Utility middleware
```

## 🚀 Usage

```python
from middleware import MiddlewareConfig, MiddlewareChain

# Apply middleware configuration
app.add_middleware(MiddlewareConfig.setup_middleware())
```

## 📚 Documentation

Each subdirectory contains specific middleware implementations with their own documentation.