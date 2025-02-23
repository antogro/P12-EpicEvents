import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


def exception_handler(exc_type, exc_value, exc_traceback):
    """Capture et enregistre les erreurs inattendues dans un fichier."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error(" Une erreur inattendue s'est produite", exc_info=(
        exc_type, exc_value, exc_traceback))


sys.excepthook = exception_handler
sys.stderr.reconfigure(encoding='utf-8')
