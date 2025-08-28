import logging
from typing import Literal
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# -------------------------------
# Environment files to load
# -------------------------------
ENV_PATHS = (".env.template", ".env")

# Default logging formats
LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# -------------------------------
# Telegram Bot settings
# -------------------------------
class BotSettings(BaseModel):
    """
    Settings related to Telegram bot.
    """

    token: str  # Bot API token
    # NOTE: don't run with debug turned on in production!
    debug: bool = True


# -------------------------------
# Database settings
# -------------------------------
class DataBaseSettings(BaseModel):
    """
    Async SQLAlchemy database configuration.
    """

    url: str  # Database connection URL
    echo: bool = False  # Log SQL queries
    echo_pool: bool = False  # Log connection pool activity
    pool_size: int = 50  # Connection pool size
    max_overflow: int = 10  # Extra connections beyond pool size


# -------------------------------
# Logging configuration
# -------------------------------
class LoggingConfig(BaseModel):
    """
    Configure application logging.
    """

    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"  # Default logging level

    log_format: str = LOG_DEFAULT_FORMAT
    log_date_format: str = LOG_DATE_FORMAT
    log_file: str = "bot.log"  # File to store logs

    @property
    def log_level_value(self) -> int:
        """
        Convert string log level to numeric value for logging module.
        Example: "info" -> logging.INFO
        """
        return logging.getLevelNamesMapping()[self.log_level.upper()]


# -------------------------------
# Main settings
# -------------------------------
class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env files.
    Supports nested configuration using "__" delimiter.
    """

    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=ENV_PATHS,  # Load values from these files
        case_sensitive=False,  # Environment variable names are case-insensitive
        env_nested_delimiter="__",  # Nested settings use double underscore
        env_prefix="BOT__",  # All env vars should start with BOT__
    )

    bot: BotSettings
    db: DataBaseSettings
    logging: LoggingConfig = LoggingConfig()  # Default logging config


# -------------------------------
# Global settings instance
# -------------------------------
settings = Settings()
