import json
import logging
import os
from typing import Any

from src.utils import df, format_date

# Получаем абсолютный путь до текущей директории
current_dir = os.path.dirname(os.path.abspath(__file__))

# Создаем путь до файла логов относительно текущей директории
rel_log_file_path = os.path.join(current_dir, "../logs/services.log")
abs_log_file_path = os.path.abspath(rel_log_file_path)

# Создаем путь до файла operations.xlsx относительно текущей директории
rel_xlsx_path = os.path.join(current_dir, "../data/operations.xlsx")
abs_xlsx_path = os.path.abspath(rel_xlsx_path)

# Добавляем логгер, который записывает логи в файл.
logger = logging.getLogger("services")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(abs_log_file_path, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


# Формируем список словарей, содержащий информацию о транзакциях - transactions
logger.info("Cписок словарей, содержащий информацию о транзакциях (transactions) сформирован")
df_draft = df[["Дата платежа", "Сумма платежа"]].copy(deep=True)
df_clean = df_draft.dropna()
df_output = df_clean.to_dict("records")
transactions = []
for i in df_output:
    output_dict = {
        "Дата платежа": format_date(i["Дата платежа"]),
        "Сумма платежа": abs(i["Сумма платежа"])
    }
    transactions.append(output_dict)


def investing(month: str, transactions_list: list[dict[str, Any]], limit: int) -> float | str:
    """Функция принимает на вход анализируемый месяц, список словарей с транзакциями, шаг округления
    и возвращает анализ инвестиционных накоплений в виде json-ответа"""

    result = 0
    for transaction in transactions_list:
        if month in transaction["Дата платежа"]:
            result += limit - (transaction["Сумма платежа"] % limit)
            result = round(result, 2)
    logger.info(
        f"Потенциальная сумма , отложенная в «Инвесткопилку» за {month} с шагом округления {limit} составляет {result}"
    )

    # Формируем список словарей с результатами
    result_list_dicts = {"month": month, "rounding_step": limit, "total_amount": result}

    # Формируем json-ответ
    logger.info('json-ответ с общей суммой, которую удалось отложить в "Инвесткопилку" создан успешно')
    json_output = json.dumps(result_list_dicts, ensure_ascii=False, indent=4)
    return json_output
