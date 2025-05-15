import logging
import logging.config
from src.ui_main import MainApp
from DeskBase_logging import LOGGING_INFO

logging.config.dictConfig(LOGGING_INFO)
logger = logging.getLogger(__name__)

def main():
    app = MainApp()
    logger.info("DeskBase initialized")

    app.mainloop()
    logger.info("DeskBase destroyed")    

if __name__ == "__main__":
    main()