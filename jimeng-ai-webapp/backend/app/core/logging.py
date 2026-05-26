import logging
import sys
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    """配置日志基础设施"""
    # 创建日志目录
    log_dir = "./logs"
    os.makedirs(log_dir, exist_ok=True)

    # 创建根日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 日志格式 - 不包含AK/SK等敏感信息
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件输出（按大小轮转）
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 过滤敏感信息的日志过滤器
    class SensitiveDataFilter(logging.Filter):
        def filter(self, record):
            msg = record.getMessage()
            # 屏蔽AK/SK相关日志（如果存在）
            sensitive_keys = ["VOLC_ACCESS_KEY", "VOLC_SECRET_KEY", "access_key", "secret_key"]
            for key in sensitive_keys:
                if key in msg:
                    return False
            return True

    for handler in logger.handlers:
        handler.addFilter(SensitiveDataFilter())

    return logger


logger = setup_logging()