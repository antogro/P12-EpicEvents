import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import os
import logging
import sys
from dotenv import load_dotenv

load_dotenv()

SENTRY_DSN = os.getenv("SENTRY_DSN", "")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[
        SqlalchemyIntegration(),
        LoggingIntegration(
            level="INFO",
            event_level="ERROR"
        ),
    ],
    traces_sample_rate=1.0,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def exception_handler(exc_type, exc_value, exc_traceback):
    """Capture et enregistre les erreurs inattendues dans un fichier et sur Sentry."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_message = f"❌ Exception Inattendue : {exc_value}"
    logger.error(error_message, exc_info=(exc_type, exc_value, exc_traceback))
    sentry_sdk.capture_exception(exc_value)  # Capture dans Sentry


sys.excepthook = exception_handler
sys.stderr.reconfigure(encoding='utf-8')
