import json
import os
from datetime import datetime as dt
from typing import Any
from unittest.mock import patch

import pandas as pd
from dateutil.relativedelta import relativedelta as rdt

from src.reports import log

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


# Получаем текущую дату
current_date = dt.now().strftime("%Y-%m-%d %H:%M:%S")


def test_log_file() -> Any:
    """Функция тестирует открывание файла reports_log.txt"""

    @log(filename=reports_log)
    def spending_by_category(transactions: pd.DataFrame, category: str, date: str = current_date) -> str:
        """Функция принимает на вход датафрейм с транзакциями, категорию, дату.
        И возвращает суммарные траты по заданной категории за последние три месяца (от переданной даты)."""
        # Форматируем дату

        date_updated = dt.strptime(date, "%Y-%m-%d %H:%M:%S")
        previous_month_date = date_updated + rdt(months=-48)
        transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")

        # Создаем отфильтрованный по заданному периоду времени DataFrame

        filtered_df = transactions[
            (previous_month_date <= transactions["Дата операции"]) & (transactions["Дата операции"] <= date)
        ]
        df_cleaned = filtered_df.dropna()
        grouped_df = df_cleaned[df_cleaned["Категория"] == category]
        total_amount = grouped_df["Сумма платежа"].sum()

        # Формируем список словарей с результатами
        result_output = {
            "category": category,
            "period": {"from": str(previous_month_date), "to": str(date)},
            "total_amount": abs(total_amount),
        }

        # Формируем json-ответ

        json_output = json.dumps(result_output, ensure_ascii=False, indent=4)

        with patch("builtins.open") as mocked_file:
            mocked_file.assert_called_once_with(reports_log, "w")
        return json_output
