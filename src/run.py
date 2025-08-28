import logging
import asyncio

from bot import start_bot
from db import db_helper
from core.config import settings

# -------------------------------
# Logger for this module
# -------------------------------
log = logging.getLogger(__name__)


async def run():
    """
    Main async function to initialize the database and start the bot.
    Ensures proper cleanup of database connections on exit.
    """

    # Initialize database
    await db_helper.init_db()

    try:
        await start_bot()
    except asyncio.CancelledError:
        # Clean exit without stacktrace on task cancellation
        logging.info("Bot task cancelled. Exiting gracefully...")
    except KeyboardInterrupt:
        # Clean exit on Ctrl+C
        logging.info("Bot stopped manually with Ctrl+C.")
    except Exception as e:
        logging.exception("Bot stopped with unexpected exception: %s", e)
    finally:
        # Always dispose the DB engine
        await db_helper.dispose()


if __name__ == "__main__":
    # Configure logging according to settings
    logging.basicConfig(
        filename=settings.logging.log_file if not settings.bot.debug else None,
        format=settings.logging.log_format,
        datefmt=settings.logging.log_date_format,
        level=settings.logging.log_level_value,
    )

    try:
        # Run the async main function
        asyncio.run(run())
    except KeyboardInterrupt:
        # This catches Ctrl+C during asyncio.run
        logging.info("Bot stopped manually with Ctrl+C at main level.")
