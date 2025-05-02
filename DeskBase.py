import logging
import logging.config
from src.ui_main import MainApp
from DeskBase_logging import LOGGING_INFO

logging.config.dictConfig(LOGGING_INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app = MainApp()

    window_width = 1080
    window_height = 720
    position_right = app.winfo_screenwidth()//2 - window_width/2
    position_down = app.winfo_screenheight()//2 - window_height/2
    app.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    logger.info("DeskBase initialized")

    app.mainloop()
    logger.info("DeskBase destroyed")
