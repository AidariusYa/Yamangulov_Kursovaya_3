import json
import logging
import os
from datetime import datetime
from typing import Callable, Optional

import pandas as pd

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../logs")

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

abs_file_path = os.path.join(log_dir, "reports.log")

logger = logging.getLogger("reports")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(abs_file_path, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def report_decorator(file_name: str = "default_report.json") -> Callable:
    """Создание декоратора, который будет записывать результаты функции-отчета в файл"""

    def decorator(func) -> Callable:
        def wrapper(*args, **kwargs) -> json:
            result = func(*args, **kwargs)
            result.to_json(path_or_buf=file_name, orient="records", force_ascii=False, indent=4)
            return result

        return wrapper

    return decorator


@report_decorator()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние три месяца"""
    logger.info("Ищем траты по конкретной категории")
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    three_months_ago = date - pd.DateOffset(months=3)
    transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y")

    filtered_operations = transactions[
        (transactions["Категория"] == category) &
        (three_months_ago <= transactions["Дата платежа"]) &
        (transactions["Дата платежа"] <= date)
        ]

    logger.info(f"Найдено {len(filtered_operations)} операций по категории '{category}' за указанный период.")
    return filtered_operations
