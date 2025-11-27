"""
Configuration management for HeartbeatMonitor.

Uses Pydantic Settings for type-safe configuration with environment variable support.
Follows the SuperClaims pattern of optional services with graceful degradation.

Environment Variables:
    HEARTBEAT_INTERVAL: Expected interval between heartbeats (default: 60)
    HEARTBEAT_ALLOWED_MISSES: Number of misses before alert (default: 3)
    HEARTBEAT_TOLERANCE: Tolerance window in seconds (default: 0)
    
    # API Mode
    API_HOST: API server host (default: 0.0.0.0)
    API_PORT: API server port (default: 8000)
    API_WORKERS: Number of uvicorn workers (default: 4)
    
    # Database (optional)
    DATABASE_URL: PostgreSQL connection string
    DB_POOL_SIZE: Connection pool size (default: 5)
    DB_MAX_OVERFLOW: Max overflow connections (default: 10)
    
    # Redis (optional)
    REDIS_URL: Redis connection string
    REDIS_TTL: Cache TTL in seconds (default: 3600)
    
    # Logging
    LOG_LEVEL: Logging level (default: INFO)
    LOG_FILE: Log file path (optional)
    JSON_LOGS: Enable JSON structured logging (default: false)
    
    # Security
    API_KEY: API key for authentication (optional)
    CORS_ORIGINS: Comma-separated allowed origins (default: *)
    MAX_UPLOAD_SIZE_MB: Max file upload size (default: 10)

Example:
    # Basic usage
    from app.config import get_settings
    
    settings = get_settings()
    print(f"Interval: {settings.heartbeat_interval}s")
    
    # With environment overrides
    import os
    os.environ['HEARTBEAT_INTERVAL'] = '120'
    settings = get_settings()
    print(f"Interval: {settings.heartbeat_interval}s")  # 120
"""

import os
import logging
from typing import Optional, List
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    Follows SuperClaims pattern:
    - Required settings have defaults
    - Optional services (DB, Redis) are None by default
    - Graceful degradation if optional services unavailable
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ========== Core Monitoring Settings ==========
    
    heartbeat_interval: int = Field(
        default=60,
        description="Expected interval between heartbeats in seconds",
        ge=1,
        le=86400  # Max 24 hours
    )
    
    heartbeat_allowed_misses: int = Field(
        default=3,
        description="Number of consecutive misses before alert",
        ge=1,
        le=100
    )
    
    heartbeat_tolerance: int = Field(
        default=0,
        description="Tolerance window in seconds for late heartbeats",
        ge=0,
        le=3600  # Max 1 hour
    )
    
    # ========== API Server Settings ==========
    
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host"
    )
    
    api_port: int = Field(
        default=8000,
        description="API server port",
        ge=1,
        le=65535
    )
    
    api_workers: int = Field(
        default=4,
        description="Number of uvicorn workers",
        ge=1,
        le=32
    )
    
    api_title: str = Field(
        default="Kairós API",
        description="API title for documentation"
    )
    
    api_version: str = Field(
        default="1.0.0",
        description="API version"
    )
    
    # ========== Database Settings (Optional) ==========
    
    database_url: Optional[str] = Field(
        default=None,
        description="PostgreSQL connection string (e.g., postgresql://user:pass@localhost/db)"
    )
    
    db_pool_size: int = Field(
        default=5,
        description="Database connection pool size",
        ge=1,
        le=50
    )
    
    db_max_overflow: int = Field(
        default=10,
        description="Max overflow connections beyond pool size",
        ge=0,
        le=50
    )
    
    db_pool_timeout: int = Field(
        default=30,
        description="Connection pool timeout in seconds",
        ge=1,
        le=300
    )
    
    # ========== Redis Settings (Optional) ==========
    
    redis_url: Optional[str] = Field(
        default=None,
        description="Redis connection string (e.g., redis://localhost:6379/0)"
    )
    
    redis_ttl: int = Field(
        default=3600,
        description="Cache TTL in seconds",
        ge=60,
        le=86400
    )
    
    redis_max_connections: int = Field(
        default=10,
        description="Max Redis connections",
        ge=1,
        le=100
    )
    
    # ========== Logging Settings ==========
    
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    log_file: Optional[str] = Field(
        default=None,
        description="Log file path (logs to stdout if not specified)"
    )
    
    json_logs: bool = Field(
        default=False,
        description="Enable JSON structured logging"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v_upper
    
    # ========== Security Settings ==========
    
    api_key: Optional[str] = Field(
        default=None,
        description="API key for authentication (optional but recommended in production)"
    )
    
    cors_origins: str = Field(
        default="*",
        description="Comma-separated list of allowed CORS origins"
    )
    
    max_upload_size_mb: int = Field(
        default=10,
        description="Maximum file upload size in MB",
        ge=1,
        le=100
    )
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str) -> str:
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            # Clean up whitespace
            return ",".join([origin.strip() for origin in v.split(",")])
        return v
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # ========== Feature Flags ==========
    
    enable_database: bool = Field(
        default=False,
        description="Enable database persistence (requires DATABASE_URL)"
    )
    
    enable_redis: bool = Field(
        default=False,
        description="Enable Redis caching (requires REDIS_URL)"
    )
    
    enable_metrics: bool = Field(
        default=True,
        description="Enable Prometheus metrics endpoint"
    )
    
    # ========== Computed Properties ==========
    
    @property
    def has_database(self) -> bool:
        """Check if database is configured and enabled."""
        return self.enable_database and self.database_url is not None
    
    @property
    def has_redis(self) -> bool:
        """Check if Redis is configured and enabled."""
        return self.enable_redis and self.redis_url is not None
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024
    
    def model_post_init(self, __context) -> None:
        """Post-initialization validation and warnings."""
        # Warn about optional services
        if self.enable_database and not self.database_url:
            logger.warning(
                "Database enabled but DATABASE_URL not set. "
                "Database features will be unavailable."
            )
        
        if self.enable_redis and not self.redis_url:
            logger.warning(
                "Redis enabled but REDIS_URL not set. "
                "Caching features will be unavailable."
            )
        
        # Warn about security in production
        if self.api_host == "0.0.0.0" and not self.api_key:
            logger.warning(
                "API running without authentication (API_KEY not set). "
                "This is NOT recommended for production!"
            )
        
        # Info about enabled features
        features = []
        if self.has_database:
            features.append("database")
        if self.has_redis:
            features.append("redis")
        if self.enable_metrics:
            features.append("metrics")
        
        if features:
            logger.info(f"Enabled optional features: {', '.join(features)}")
        else:
            logger.info("Running in basic mode (no optional features enabled)")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are only loaded once.
    Call this function to access settings throughout the application.
    
    Returns:
        Settings instance
        
    Example:
        >>> from app.config import get_settings
        >>> settings = get_settings()
        >>> print(settings.api_port)
        8000
    """
    return Settings()


def reload_settings() -> Settings:
    """
    Reload settings (clears cache).
    
    Useful for testing or when environment variables change.
    
    Returns:
        Fresh Settings instance
        
    Example:
        >>> import os
        >>> os.environ['API_PORT'] = '9000'
        >>> settings = reload_settings()
        >>> print(settings.api_port)
        9000
    """
    get_settings.cache_clear()
    return get_settings()


# ========== Environment-Specific Configurations ==========

def get_development_settings() -> Settings:
    """Get settings for development environment."""
    os.environ.setdefault("LOG_LEVEL", "DEBUG")
    os.environ.setdefault("API_WORKERS", "1")
    os.environ.setdefault("ENABLE_DATABASE", "false")
    os.environ.setdefault("ENABLE_REDIS", "false")
    return reload_settings()


def get_production_settings() -> Settings:
    """Get settings for production environment."""
    os.environ.setdefault("LOG_LEVEL", "INFO")
    os.environ.setdefault("JSON_LOGS", "true")
    os.environ.setdefault("API_WORKERS", "4")
    
    # Require API key in production
    if "API_KEY" not in os.environ:
        logger.warning(
            "API_KEY not set in production environment! "
            "This is a security risk."
        )
    
    return reload_settings()


def get_test_settings() -> Settings:
    """Get settings for testing environment."""
    os.environ.setdefault("LOG_LEVEL", "WARNING")
    os.environ.setdefault("API_WORKERS", "1")
    os.environ.setdefault("ENABLE_DATABASE", "false")
    os.environ.setdefault("ENABLE_REDIS", "false")
    return reload_settings()


# ========== Configuration Validation ==========

def validate_settings() -> tuple[bool, list[str]]:
    """
    Validate settings and return any errors/warnings.
    
    Returns:
        Tuple of (is_valid, list_of_issues)
        
    Example:
        >>> is_valid, issues = validate_settings()
        >>> if not is_valid:
        ...     for issue in issues:
        ...         print(f"⚠️  {issue}")
    """
    issues = []
    
    try:
        settings = get_settings()
        
        # Check critical settings
        if settings.heartbeat_interval < 1:
            issues.append("heartbeat_interval must be >= 1")
        
        if settings.heartbeat_allowed_misses < 1:
            issues.append("heartbeat_allowed_misses must be >= 1")
        
        # Check optional services
        if settings.enable_database and not settings.database_url:
            issues.append("enable_database is true but DATABASE_URL not set")
        
        if settings.enable_redis and not settings.redis_url:
            issues.append("enable_redis is true but REDIS_URL not set")
        
        # Security checks
        if settings.api_host == "0.0.0.0" and not settings.api_key:
            issues.append(
                "API exposed publicly (0.0.0.0) without authentication "
                "(consider setting API_KEY)"
            )
        
        if settings.cors_origins == "*":
            issues.append(
                "CORS allows all origins (*) - restrict in production "
                "by setting CORS_ORIGINS"
            )
        
        return len(issues) == 0, issues
        
    except Exception as e:
        issues.append(f"Failed to load settings: {e}")
        return False, issues


if __name__ == "__main__":
    """CLI utility to display current settings."""
    print("🔧 HeartbeatMonitor Configuration\n")
    print("=" * 60)
    
    settings = get_settings()
    
    print("\n📊 Monitoring Settings:")
    print(f"  Interval: {settings.heartbeat_interval}s")
    print(f"  Allowed Misses: {settings.heartbeat_allowed_misses}")
    print(f"  Tolerance: {settings.heartbeat_tolerance}s")
    
    print("\n🌐 API Settings:")
    print(f"  Host: {settings.api_host}")
    print(f"  Port: {settings.api_port}")
    print(f"  Workers: {settings.api_workers}")
    print(f"  Authentication: {'✅ Enabled' if settings.api_key else '❌ Disabled'}")
    
    print("\n🗄️  Optional Services:")
    print(f"  Database: {'✅ Enabled' if settings.has_database else '❌ Disabled'}")
    print(f"  Redis: {'✅ Enabled' if settings.has_redis else '❌ Disabled'}")
    print(f"  Metrics: {'✅ Enabled' if settings.enable_metrics else '❌ Disabled'}")
    
    print("\n📝 Logging:")
    print(f"  Level: {settings.log_level}")
    print(f"  File: {settings.log_file or 'stdout'}")
    print(f"  JSON Format: {'✅ Yes' if settings.json_logs else '❌ No'}")
    
    print("\n🔒 Security:")
    print(f"  CORS Origins: {settings.cors_origins}")
    print(f"  Max Upload: {settings.max_upload_size_mb}MB")
    
    print("\n" + "=" * 60)
    
    # Validate configuration
    is_valid, issues = validate_settings()
    if is_valid:
        print("\n✅ Configuration is valid!")
    else:
        print("\n⚠️  Configuration Issues:")
        for issue in issues:
            print(f"  • {issue}")
    
    print()
