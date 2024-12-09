import json
import logging
import os
from datetime import datetime as dt
from functools import wraps
from typing import Any

import pandas as pd
from dateutil.relativedelta import relativedelta as rdt

from src.utils import df

# Получаем абсолютный путь до текущей директории
current_dir = os.path.dirname(os.path.abspath(__file__))

# Создаем путь до файла логов относительно текущей директории
rel_log_file_path = os.path.join(current_dir, "../logs/reports.log")
abs_log_file_path = os.path.abspath(rel_log_file_path)

# Создаем путь до файла "reports_log.txt" относительно текущей директории
rel_mylog_path = os.path.join(current_dir, "../logs/reports_log.txt")
abs_mylog_path = os.path.abspath(rel_mylog_path)
reports_log = abs_mylog_path

# Создаем путь до файла operations.xlsx относительно текущей директории
rel_xlsx_path = os.path.join(current_dir, "../data/operations.xlsx")
abs_xlsx_path = os.path.abspath(rel_xlsx_path)

# Добавляем логгер, который записывает логи в файл.
logger = logging.getLogger("reports")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(abs_log_file_path, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Получаем текущую дату
current_date = dt.now().strftime("%Y-%m-%d %H:%M:%S")


def log(filename: str) -> Any:
    """Декоратор для логирования вызовов функции. Логирует данные отчета в файл"""

    def decorator(func: Any) -> Any:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            log_message = ""  # Инициализация по умолчанию

            try:
                result = func(*args, **kwargs)
                log_message = result
                return result
            except Exception as e:
                log_message = f"my_function error: {e}. Input:{args}, {kwargs}"
                raise e

            finally:
                with open(filename, "w", encoding="utf-8") as file:
                    file.write(log_message + "\n")

        return wrapper

    return decorator


@log(filename=reports_log)
def spending_by_category(transactions: pd.DataFrame, category: str, date: str = current_date) -> str:
    """Функция принимает на вход датафрейм с транзакциями, категорию, дату.
    И возвращает суммарные траты по заданной категории за последние три месяца (от переданной даты)."""

    # Форматируем дату
    logger.info("Дата отформатирована")
    date_updated = dt.strptime(date, "%Y-%m-%d %H:%M:%S")
    previous_month_date = date_updated + rdt(months=-48)
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    # Создаем отфильтрованный по заданному периоду времени DataFrame
    logger.info("DataFrame отфильтрован по периоду дат")
    df_filter = transactions.loc[
        (transactions["Дата операции"].between(previous_month_date, date)) & (transactions["Категория"] == category)
    ]
    df_cleaned = df_filter.dropna().copy()
    df_cleaned["Дата операции"] = df_cleaned["Дата операции"].astype(str)
    output_list_dicts = df_cleaned.to_dict("records")

    # Формируем json-ответ
    logger.info("json-ответ с транзакциями по указанной категории и за указанный период времени успешно создан")
    json_output = json.dumps(output_list_dicts, ensure_ascii=False, indent=4)
    return json_output


if __name__ == "__main__":
    print(spending_by_category(df, "Транспорт"))
