import json
import sys
from os import path

from loguru import logger

from app.settings import LOG_DIR


# basic logs
LOG_FORMAT = "<green>{time:DD-MM-YYYY HH:mm:ss:SSSSSS}</green> | <level>{level: <6}</level> | " \
             "<normal>{extra[request_id]}</normal> | " \
             "<magenta>{name}</magenta>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - " \
             "<level><normal>{message}</normal></level>"

log_file_path = path.join(LOG_DIR, "log_file.log")

config = {
    "handlers": [
        {
            "sink": sys.stdout,
            "format": LOG_FORMAT,
            "colorize": True,
            "enqueue": True,
            "backtrace": True,
            "diagnose": True,
        }
    ]
}

logger.configure(**config)

logger.add(log_file_path, enqueue=True, format=LOG_FORMAT,
           filter=(lambda record: record["level"].name != "STATS"),
           backtrace=True, diagnose=True, serialize=True)


# stats log
STATS_LOG_FORMAT = "<green>{time:DD-MM_YYYY at HH:mm:ss:SSSSSS}</green> - <normal>{extra}</normal>"
stats_file_path = path.join(LOG_DIR, "stats_file.log")

logger.level("STATS", no=15, color="<yellow><bold>")


def stats_serialize(message):
    """Этот метод сериализует данные и записывает в файл"""
    message_record = {"data": message.record["extra"],
                      "timestamp": message.record["time"].strftime("%d.%m.%Y, %H:%M:%S:%f")}
    try:
        with open(stats_file_path, "a") as f:
            f.write(f"{json.dumps(message_record)}\n")
    except TypeError:
        # внутри футура
        pass


logger.add(stats_serialize, filter=(lambda record: record["level"].name == "STATS"),
           format=STATS_LOG_FORMAT, enqueue=True)
