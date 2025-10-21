# Configuration Module

This module handles all configuration settings for middleware components.

## 📁 Files

- `settings.py` - Base settings using Pydantic
- `middleware_config.py` - Main middleware configuration and setup
- `__init__.py` - Package exports

## 🔧 Usage

```python
from middleware.config import MiddlewareConfig, MiddlewareSettings

# Create custom settings
settings = MiddlewareSettings(debug=True, rate_limit_requests=200)

# Setup middleware
config = MiddlewareConfig(settings)
config.setup_middleware(app)
```

## ⚙️ Configuration Options

All settings can be configured via environment variables with the `MIDDLEWARE_` prefix:

- `MIDDLEWARE_DEBUG` - Enable debug mode
- `MIDDLEWARE_SECRET_KEY` - JWT secret key
- `MIDDLEWARE_RATE_LIMIT_REQUESTS` - Rate limit requests per window
- `MIDDLEWARE_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)