import logging
from typing import Any, Dict

from pythonjsonlogger import jsonlogger
from sqlalchemy import log as sa_log


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        log_record["time"] = log_record.pop("asctime")
        if "name" in log_record:
            log_record["logger"] = log_record.pop("name")
        log_record["level"] = log_record.pop("levelname")
        if "process" in log_record:
            log_record["pid"] = log_record.pop("process")
        if "funcName" in log_record:
            log_record["method"] = log_record.pop("funcName")
        if "module" in log_record:
            log_record["class_name"] = log_record.pop("module")

        # Добавляем поля из extra в log_record
        if hasattr(record, "extra"):
            for key, value in record.extra.items():
                log_record[key] = value


def setup_logging() -> None:
    logger_level = "INFO"

    handler = logging.StreamHandler()
    formatter = CustomJsonFormatter(
        '{"time": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
    )  # type: ignore[no-untyped-call, unused-ignore]
    handler.setFormatter(formatter)
    handler.set_name("default")
    handler.setLevel(logger_level)
    logging.basicConfig(handlers=[handler], level=logger_level)

    # Mute SQLAlchemy default logger handler
    sa_log._add_default_handler = lambda _: None
