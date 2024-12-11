import os

from src.reports import spending_by_category
from src.services import investing, transactions
from src.utils import df
from src.views import web_main

# Получаем абсолютный путь до текущей директории
current_dir = os.path.dirname(os.path.abspath(__file__))

# Создаем путь до файла логов относительно текущей директории
rel_log_file_path = os.path.join(current_dir, "../logs/views.log")
abs_log_file_path = os.path.abspath(rel_log_file_path)

# Создаем путь до файла user_settings.json относительно текущей директории.
rel_json_path = os.path.join(current_dir, "../user_settings.json")
abs_json_path = os.path.abspath(rel_json_path)

# Создаем путь до файла operations.xlsx относительно текущей директории
rel_xlsx_path = os.path.join(current_dir, "../data/operations.xlsx")
abs_xlsx_path = os.path.abspath(rel_xlsx_path)

if __name__ == "__main__":
    print(web_main(abs_xlsx_path))
    print(investing("2021-12", transactions, 10))
    print(spending_by_category(df, "Транспорт"))
