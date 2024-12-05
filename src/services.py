import json
import logging
import os
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))

rel_file_path = os.path.join(current_dir, "../logs/services.log")
abs_file_path = os.path.abspath(rel_file_path)

logger = logging.getLogger("services")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(abs_file_path, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def high_cashback_categories_analyze(data, year, month):
    """
    Анализирует выгодные категории повышенного кешбэка за указанный год и месяц.

    :param data: Список транзакций, где каждая транзакция - это словарь с ключами "category", "amount", "date".
    :param year: Год для анализа.
    :param month: Месяц для анализа.
    :return: JSON с анализом кешбэка по категориям.
    """
    cashback_summary = {}

    for transaction in data:
        transaction_date = datetime.strptime(transaction["date"], "%Y-%m-%d")
        if transaction_date.year == year and transaction_date.month == month:
            category = transaction["category"]
            amount = transaction["amount"]
            if category not in cashback_summary:
                cashback_summary[category] = 0
            cashback_summary[category] += amount

    logging.info(f"Анализ повышенных категорий кешбэка завершен для {year}-{month}: {cashback_summary}")
    return json.dumps(cashback_summary, ensure_ascii=False)
