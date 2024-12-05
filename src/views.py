import json

import pandas as pd

from src.utils import (get_data_from_excel, convert_timestamps_to_strings, currency_rates, operations_by_date,
                       user_greeting_by_hours, card_list, stock_prices, top_five_transactions)


transactions = get_data_from_excel("../data/operations.xlsx")
transactions_df = pd.read_excel("../data/operations.xlsx")


def web_main(date: str, file_json: str) -> json:
    """Возвращает результаты внутренних функций для главной Веб-страницы"""
    operations = pd.read_excel("../data/operations.xlsx")
    operations = operations_by_date(operations, date)
    operations = convert_timestamps_to_strings(operations)

    # Передаем file_json в currency_rates
    result = {
        "greeting": user_greeting_by_hours(),
        "cards": card_list(operations),
        "top_transactions": top_five_transactions(operations),
        "currency_rates": currency_rates(file_json),
        "stock_prices": stock_prices(file_json),
    }
    return json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    print("2021-01-10 12:00:00", transactions, transactions_df, "Супермаркеты")
