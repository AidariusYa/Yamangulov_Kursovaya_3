import json
import logging
import os
from datetime import datetime as dt
from typing import Any, List

import pandas as pd
import requests
from dotenv import load_dotenv


# Получаем абсолютный путь до текущей директории
current_dir = os.path.dirname(os.path.abspath(__file__))

# Создаем путь до файла логов относительно текущей директории
rel_log_file_path = os.path.join(current_dir, "../logs/utils.log")
abs_log_file_path = os.path.abspath(rel_log_file_path)

# Создаем путь до файла user_settings.json относительно текущей директории.
# В файл храниться словарь с требуемыми валютами и акциями
rel_json_path = os.path.join(current_dir, "../user_settings.json")
abs_json_path = os.path.abspath(rel_json_path)

# Создаем путь до файла operations.xlsx относительно текущей директории
rel_xlsx_path = os.path.join(current_dir, "../data/operations.xlsx")
abs_xlsx_path = os.path.abspath(rel_xlsx_path)

# Добавляем логгер, который записывает логи в файл.
logger = logging.getLogger("utils")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(abs_log_file_path, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

load_dotenv()
API_KEY_FOR_CURRENCY = os.getenv("API_KEY_FOR_CURRENCY")
API_KEY_FOR_STOCK = os.getenv("API_KEY_FOR_STOCK")

# Создаем json-файл со списком акций и валют

currencies_stocks_dict = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}

with open(abs_json_path, "w") as file:
    json.dump(currencies_stocks_dict, file)


def import_from_excel(input_xlsx_file: str) -> pd.DataFrame:
    """Функция принимает на вход путь до файла xlsx и возвращает DataFrame"""

    try:
        input_df = pd.read_excel(input_xlsx_file)
        logger.info("Данные из файла xlsx импортированы")
        return input_df
    except FileNotFoundError:
        logger.warning("Файл не найден: %s", input_xlsx_file)
    except ValueError:
        logger.warning("Импортируемый список пуст или отсутствует.")
    except Exception as e:
        logger.warning("Произошла ошибка при импорте данных: %s", e)


df = import_from_excel(abs_xlsx_path)


def get_currency_rates(json_file: str) -> List[dict[str, Any]]:
    """Функция принимает на вход json-файл и возвращает список словарей с курсами требуемых валют.
    Курс валюты функция импортирует через API"""
    logger.info("Курсы валют получены")

    with open(json_file, "r", encoding="utf-8") as doc_file:
        currencies_stocks_list = json.load(doc_file)
        currency_rates_list_dicts = []

        # Получаем курсы валют относительно USD
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY_FOR_CURRENCY}/latest/USD"
        response = requests.get(url)
        result = response.json()

        for currency in currencies_stocks_list["user_currencies"]:
            currency_rates_dict = {
                "currency": currency,
                "rate": result["conversion_rates"].get(currency)
            }
            currency_rates_list_dicts.append(currency_rates_dict)

        return currency_rates_list_dicts


def get_stock_prices(json_file: str) -> List[dict[str, Any]]:
    """Функция принимает на вход json-файл и возвращает список словарей с курсами требуемых акций.
    Стоимости акций функция импортирует через API"""
    logger.info("Стоимости акций получены")

    with open(json_file, "r", encoding="utf-8") as doc_file:
        currencies_stocks_list = json.load(doc_file)
        stock_prices_list_dicts = []

        for stock in currencies_stocks_list["user_stocks"]:
            url = (f"https://api.marketstack.com/v1/eod?access_key={API_KEY_FOR_STOCK}&symbols={stock}&date="
                   f"{input_datetime}")
            response = requests.get(url)
            result = response.json()

            # Проверяем наличие данных в ответе
            if "data" in result and len(result["data"]) > 0:
                stock_prices_dict = {
                    "stock": stock,
                    "price": result["data"][0].get("close")  # Получаем цену закрытия
                }
                stock_prices_list_dicts.append(stock_prices_dict)
            else:
                logger.warning("Нет данных для акции: %s", stock)

        return stock_prices_list_dicts


input_datetime = "2021-12-29 22:32:24"


def greetings(input_daytime: str) -> str:
    """Функция принимает строку с датой и возвращает требуемое приветствие"""
    date_update = dt.strptime(input_daytime, "%Y-%m-%d %H:%M:%S")
    time = date_update.strftime("%H:%M:%S")

    if "05:00:00" <= time <= "12:00:00":
        return "Доброе утро"
    elif "12:00:00" <= time <= "18:00:00":
        return "Добрый день"
    elif "18:00:00" <= time <= "23:00:00":
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def start_month(input_monthtime: str) -> dt:
    """Функция принимает на вход строку с датой и возвращает начало месяца"""
    date_update = dt.strptime(input_monthtime, "%Y-%m-%d %H:%M:%S")
    start = date_update.replace(day=1, hour=0, minute=0, second=0)
    return start


begin_month = start_month(input_datetime)


def filter_date(df_test: str) -> pd.DataFrame:
    """Функция создает DataFrame по заданному периоду времени"""
    dataframe = pd.read_excel(df_test)
    df_date = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    filtered_df_to_date = dataframe[(begin_month <= df_date) & (df_date <= input_datetime)]
    return filtered_df_to_date


filtered_to_date = filter_date(abs_xlsx_path)


def cards_info(input_df: pd.DataFrame) -> list[dict[str, Any]]:
    """Функция принимает на вход путь до файла xlsx и возвращает DataFrame"""

    df_output = []
    try:
        logger.info("Данные из DataFrame обработаны")

        # Группировка по номеру карты и суммирование
        cards = input_df.groupby("Номер карты")
        cards_prices = cards["Сумма операции с округлением"].sum()
        df_test = cards_prices.to_dict()

        for card, total in df_test.items():
            df_result = {
                "last_digits": card,
                "total_spent": total,
                "cashback": round(total / 100, 2)
            }
            df_output.append(df_result)

        return df_output

    except KeyError as e:
        logger.warning("Ошибка: отсутствует необходимый столбец в DataFrame: %s", e)
    except Exception as e:
        logger.warning("Произошла ошибка при обработке данных: %s", e)

    return [{}]  # Возвращаем список с пустым словарем в случае ошибки


def top_transactions(input_df: pd.DataFrame) -> list[dict[str, Any]] | None:
    """Функция принимает на вход DataFrame и возвращает ТОП-5 транзакций по сумме платежа"""
    df_output_sort = []
    try:
        logger.info("Данные из DataFrame обработаны")

        # Сортировка DataFrame по сумме платежа
        sorted_df = input_df.sort_values("Сумма платежа", ascending=False)
        sort_five = sorted_df.iloc[0:5]

        df_sort_dict = sort_five.to_dict("records")
        for i in df_sort_dict:
            df_sort_result = {
                "date": i["Дата платежа"],
                "amount": i["Сумма платежа"],
                "category": i["Категория"],
                "description": i["Описание"]
            }
            df_output_sort.append(df_sort_result)

        return df_output_sort

    except KeyError as e:
        logger.warning("Ошибка: отсутствует необходимый столбец в DataFrame: %s", e)
    except Exception as e:
        logger.warning("Произошла ошибка при обработке данных: %s", e)

    return None  # Возвращаем None в случае ошибки


def format_date(input_format_date: str) -> str:
    """Функция форматирует дату"""
    date_update = dt.strptime(input_format_date, "%d.%m.%Y")
    return date_update.strftime("%Y-%m-%d")
