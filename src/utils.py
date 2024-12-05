import json
import logging
import os
from datetime import datetime
import pandas as pd
import requests
from dotenv import load_dotenv

# Настройка логирования
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
log_file_path = os.path.join(project_root, "logs/utils.log")

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_file_path, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

load_dotenv()
API_KEY_FOR_CURRENCY = os.getenv("API_KEY_FOR_CURRENCY")
API_KEY_FOR_STOCK = os.getenv("API_KEY_FOR_STOCK")


def get_data_from_excel(file_path: str) -> pd.DataFrame:
    """Получение информации из файла Excel."""
    try:
        operations = pd.read_excel(file_path)
        logger.info("Успешное выполнение")
        return operations  # Возвращаем DataFrame
    except (ValueError, FileNotFoundError) as ex:
        logger.error(f"Произошла ошибка: {ex}")
        return pd.DataFrame()  # Возвращаем пустой DataFrame вместо списка


def operations_by_date(operations: pd.DataFrame, date: str) -> pd.DataFrame:
    """Возвращает операции за текущий месяц."""
    first_day_month = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").replace(day=1)
    operations["Дата операции"] = pd.to_datetime(operations["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    return operations[
        (operations["Дата операции"] >= first_day_month) &
        (operations["Дата операции"] <= datetime.strptime(date, "%Y-%m-%d %H:%M:%S"))
    ]


def user_greeting_by_hours() -> str:
    """Формирует приветствие на основе текущего времени."""
    logger.info("Приветствуем пользователя")
    current_hour = datetime.now().hour
    greetings = {
        (0, 6): "Доброй ночи",
        (6, 12): "Доброе утро",
        (12, 18): "Добрый день",
        (18, 24): "Добрый вечер"
    }
    for (start, end), greeting in greetings.items():
        if start <= current_hour < end:
            return greeting


def card_list(operations: pd.DataFrame) -> list:
    """Возвращает список о картах пользователя."""
    grouped_operations = operations.groupby("Номер карты")["Сумма операции с округлением"].sum().reset_index()
    grouped_operations["Cashback"] = (grouped_operations["Сумма операции с округлением"] // 100).astype(int)
    grouped_operations["LastFourDigits"] = grouped_operations["Номер карты"].astype(str).str[-4:]
    result = grouped_operations[["LastFourDigits", "Сумма операции с округлением", "Cashback"]]
    result.columns = ["last_digits", "total_spent", "cashback"]
    return result.to_dict(orient="records")


def top_five_transactions(operations: pd.DataFrame) -> list:
    """Получение списка 5 крупнейших по сумме платежа транзакций."""
    top_transactions = operations.nlargest(5, "Сумма операции с округлением")
    return [
        {
            "date": transaction["Дата операции"],
            "amount": transaction["Сумма операции с округлением"],
            "category": transaction["Категория"],
            "description": transaction["Описание"],
        }
        for transaction in top_transactions.to_dict(orient="records")
    ]


def currency_rates(file_json: str) -> list:
    """Получение списка курсов валют."""
    logger.info("Поиск курсов валют")
    try:
        with open(file_json, encoding="utf-8") as file:
            user_currencies = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as ex:
        logger.error(f"Ошибка при чтении файла с валютами: {ex}")
        return []

    result_currencies = []
    for currency in user_currencies.get("user_currencies", []):
        response = requests.get(
            f"https://v6.exchangerate-api.com/v6/1bb27ce69aa2781d3e315dd4/latest/USD={API_KEY_FOR_CURRENCY}"
            f"&base_currency={currency}&currencies=RUB"
        )
        if response.status_code == 200:
            rate = round(response.json()["data"]["RUB"]["value"], 2)
            result_currencies.append({"currency": currency, "rate": rate})
        else:
            logger.error(f"Ошибка при получении курса для {currency}: {response.status_code}")
    return result_currencies


def stock_prices(file_json: str) -> list:
    """Возвращает стоимость акций из S&P 500."""
    logger.info("Поиск основных акций из S&P 500")
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={API_KEY_FOR_STOCK}"
    result = []

    try:
        with open(file_json, encoding="utf-8") as file:
            user_shares = json.load(file)
            user_share = ",".join(user_shares.get("user_stocks", []))
            querystring = {"symbols": user_share}
            response = requests.get(url, params=querystring)
            response.raise_for_status()  # Проверка на ошибки HTTP
            for data in response.json().get("data", []):
                result.append({"stock": data["symbol"], "price": data["close"]})
    except (FileNotFoundError, json.JSONDecodeError) as ex:
        logger.error(f"Ошибка при чтении файла с акциями: {ex}")
    except requests.RequestException as ex:
        logger.error(f"Ошибка при запросе к API: {ex}")

    return result


def convert_timestamps_to_strings(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Преобразует все столбцы с типом "datetime64[ns]" в строки."""
    for col in dataframe.select_dtypes(include=["datetime64[ns]"]).columns:
        dataframe[col] = dataframe[col].dt.strftime("%Y-%m-%d %H:%M:%S")
    return dataframe
