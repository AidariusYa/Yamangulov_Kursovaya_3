import json
import os
from typing import Any
from unittest.mock import patch

import pandas as pd
from dotenv import load_dotenv

from src.views import web_main

load_dotenv(".env")

API_KEY_FOR_CURRENCY = os.getenv("API_KEY_FOR_CURRENCY")
API_KEY_FOR_STOCK = os.getenv("API_KEY_FOR_STOCK")

# Получаем абсолютный путь до текущей директории
current_dir = os.path.dirname(os.path.abspath(__file__))

# Создаем путь до файла operations.xlsx относительно текущей директории
rel_xlsx_path = os.path.join(current_dir, "../data/operations.xlsx")
abs_xlsx_path = os.path.abspath(rel_xlsx_path)

# Создаем тестовый DataFrame для имитации данных из Excel
test_data = {
    "Дата операции": ["15.02.2018 10:00:00", "16.02.2018 11:00:00", "17.02.2018 12:00:00"],
    "Сумма": [100, 200, 300],
}
test_df = pd.DataFrame(test_data)


def test_web_main() -> Any:
    """Функция тестирует работу функции web_main"""
    with (
        patch("src.utils.get_currency_rates") as mock_get_currency_rates,
        patch("src.utils.get_stock_prices") as mock_get_current_stocks,
        patch("src.utils.import_from_excel") as mock_import_from_excel,
        patch("src.utils.cards_info") as mock_cards_info,
        patch("src.utils.top_transactions") as mock_top_transactions,
    ):
        # Настраиваем моки
        mock_import_from_excel.return_value = test_df
        mock_get_currency_rates.return_value = [
            {"currency": "USD", "rate": 1},
            {"currency": "EUR", "rate": 0.9466},
        ]
        mock_get_current_stocks.return_value = [
            {"stock": "AAPL", "price": 242.84},
            {"stock": "AMZN", "price": 227.03},
            {"stock": "GOOGL", "price": 174.51},
            {"stock": "MSFT", "price": 443.57},
            {"stock": "TSLA", "price": 389.22},
        ]
        mock_cards_info.return_value = [
            {"last_digits": "*4556", "total_spent": 9115.3, "cashback": 91.15},
            {"last_digits": "*5441", "total_spent": 196143.78, "cashback": 1961.44},
            {"last_digits": "*7197", "total_spent": 17671.41, "cashback": 176.71},
        ]
        mock_top_transactions.return_value = [
            {"date": "15.02.2018", "amount": 30000.0, "category": "Пополнения", "description": "Перевод с карты"},
            {"date": "15.02.2018", "amount": 30000.0, "category": "Пополнения", "description": "Перевод с карты"},
            {"date": "09.02.2018", "amount": 30000.0, "category": "Пополнения", "description": "Перевод с карты"},
            {"date": "09.02.2018", "amount": 30000.0, "category": "Пополнения", "description": "Перевод с карты"},
            {"date": "15.02.2018", "amount": 29963.87, "category": "Пополнения", "description": "Перевод с карты"},
        ]
        expected_output = {
            "greeting": "Добрый день",  # Обновите это значение, если оно должно быть другим
            "cards": [
                {"last_digits": "*4556", "total_spent": 9115.3, "cashback": 91.15},
                {"last_digits": "*5441", "total_spent": 196143.78, "cashback": 1961.44},
                {"last_digits": "*7197", "total_spent": 17671.41, "cashback": 176.71},
            ],
            "top_transactions": [
                {"date": "15.02.2018", "amount": 30000.0, "category": "Пополнения", "description": "Перевод с карты"},
                {"date": "15.02.2018", "amount": 30000.0, "category": "Пополнения", "description": "Перевод с карты"},
                {"date": "09.02.2018", "amount": 30000.0, "category": "Пополнения", "description": "Перевод с карты"},
                {"date": "09.02.2018", "amount": 30000.0, "category": "Пополнения", "description": "Перевод с карты"},
                {"date": "15.02.2018", "amount": 29963.87, "category": "Пополнения", "description": "Перевод с карты"},
            ],
            "currency_rates": [
                {"currency": "USD", "rate": 1},
                {"currency": "EUR", "rate": 0.9466},
            ],
            "stock_prices": [
                {"stock": "AAPL", "price": 242.84},
                {"stock": "AMZN", "price": 227.03},
                {"stock": "GOOGL", "price": 174.51},
                {"stock": "MSFT", "price": 443.57},
                {"stock": "TSLA", "price": 389.22},
            ],
        }

        # Преобразуем ожидаемый вывод в JSON
        expected_json_output = json.dumps(expected_output, ensure_ascii=False, indent=4)

        # Проверяем, что функция возвращает ожидаемый результат
        assert web_main(abs_xlsx_path) == expected_json_output
