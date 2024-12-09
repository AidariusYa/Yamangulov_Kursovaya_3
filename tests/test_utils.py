import json
import os
from typing import Any
from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import format_date, get_currency_rates, get_stock_prices, greetings, import_from_excel, start_month

# Получаем абсолютный путь до текущей директории
current_dir = os.path.dirname(os.path.abspath(__file__))

# Создаем путь до файла user_settings.json относительно текущей директории.
rel_json_path = os.path.join(current_dir, "../user_settings.json")
abs_json_path = os.path.abspath(rel_json_path)

# Создаем тестовый JSON файл для тестов
test_json_data = {
    "user_currencies": ["USD", "EUR"],
    "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
}

with open(abs_json_path, "w") as f:
    json.dump(test_json_data, f)


@patch("requests.get")
def test_get_currency_rates(mock_get: Any) -> None:
    """Функция тестирует составление списка словарей с валютами. Курсы валюты импортируются по API"""

    mock_get.return_value.json.return_value = {
        "base": "USD",
        "date": "2024-08-06",
        "conversion_rates": {"USD": 1, "EUR": 0.85}
    }

    expected_result = [
        {"currency": "USD", "rate": 1},
        {"currency": "EUR", "rate": 0.85},
    ]

    assert get_currency_rates(abs_json_path) == expected_result


@patch("requests.get")
def test_get_stock_prices(mock_get: Any) -> None:
    """Функция тестирует составление списка словарей с акциями. Стоимости акций импортируются по API"""

    mock_get.return_value.json.return_value = {
        "data": [
            {"symbol": "AAPL", "close": 189.68214},
            {"symbol": "AMZN", "close": 189.68214},
            {"symbol": "GOOGL", "close": 189.68214},
            {"symbol": "MSFT", "close": 189.68214},
            {"symbol": "TSLA", "close": 189.68214},
        ]
    }

    expected_result = [
        {"stock": "AAPL", "price": 189.68214},
        {"stock": "AMZN", "price": 189.68214},
        {"stock": "GOOGL", "price": 189.68214},
        {"stock": "MSFT", "price": 189.68214},
        {"stock": "TSLA", "price": 189.68214},
    ]

    assert get_stock_prices(abs_json_path) == expected_result


@pytest.mark.parametrize(
    "date, greetings_output",
    [
        ("2018-02-16 11:01:58", "Доброе утро"),
        ("2018-02-16 12:01:58", "Добрый день"),
        ("2018-02-16 21:01:58", "Добрый вечер"),
        ("2018-02-16 03:01:58", "Доброй ночи"),
    ],
)
def test_greetings(date: str, greetings_output: str) -> None:
    """Функция тестирует вывод приветствия в зависимости от времени суток"""
    assert greetings(date) == greetings_output


@pytest.mark.parametrize(
    "input_date, expected_start_month",
    [
        ("2018-02-16 12:01:58", "2018-02-01 00:00:00"),
        ("2021-12-29 22:32:24", "2021-12-01 00:00:00"),
    ],
)
def test_start_month(input_date: str, expected_start_month: str) -> None:
    """Функция тестирует вывод начала месяца от предоставленной даты"""
    assert start_month(input_date) == pd.to_datetime(expected_start_month)


@pytest.mark.parametrize(
    "date, formatted_date",
    [
        ("16.02.2018", "2018-02-16"),
        ("01.01.2001", "2001-01-01"),
        ("1.02.2018", "2018-02-01"),
    ],
)
def test_format_date(date: str, formatted_date: str) -> None:
    """Функция тестирует форматирование даты"""
    assert format_date(date) == formatted_date


@patch("pandas.read_excel")
def test_import_from_excel(mock_read_excel: Any) -> None:
    """Функция тестирует импорт данных из Excel файла в DataFrame"""

    # Настраиваем mock для возвращаемого DataFrame
    mock_read_excel.return_value = pd.DataFrame({
        "Дата операции": ["01.12.2021 10:00:00", "15.12.2021 10:00:00"],
        "Сумма операции с округлением": [100, 200]
    })

    result = import_from_excel("operations.xlsx")
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (2, 2)
    assert result["Сумма операции с округлением"].sum() == 300  # Проверяем сумму


if __name__ == "__main__":
    pytest.main()
