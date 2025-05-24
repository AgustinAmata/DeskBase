import logging
class standardFilter(logging.Filter):
    def filter(self, record):
        return record.levelno != logging.ERROR

class errorFilter(logging.Filter):
    def filter(self, record):
        return record.levelname == "ERROR"

LOGGING_INFO = {
  "version": 1,
  "disable_existing_loggers": False,
  "formatters": {
    "simple": {
      "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
  },
  "filters":{
    "standardLogFilter": {
      "()": standardFilter
    },
    "errorLogFilter": {
      "()": errorFilter
    }
  },
  "handlers":{
    "standard": {
      "class": "logging.handlers.RotatingFileHandler",
      "level": "DEBUG",
      "formatter": "simple",
      "filters": ["standardLogFilter"],
      "filename": "./DeskBase_standard.log",
      "mode": "a"
    },
    "error": {
      "class": "logging.handlers.RotatingFileHandler",
      "level": "ERROR",
      "formatter": "simple",
      "filters": ["errorLogFilter"],
      "filename": "./DeskBase_errors.log",
      "mode": "a"
    }
  },
  "root": {
    "level": "DEBUG",
    "handlers": ["standard", "error"]
  },
  "loggers": {
    "matplotlib": {
    "level": "WARNING",
    "handlers": ["standard", "error"],
    },
    "PIL": {
      "level": "WARNING",
      "handlers": ["standard", "error"],
    },
  }
}