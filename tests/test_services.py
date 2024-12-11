import json
import unittest

from src.services import investing


class TestInvestingFunction(unittest.TestCase):

    def setUp(self):
        # Подготовка тестовых данных
        self.transactions = [
            {"Дата платежа": "2023-01-15", "Сумма платежа": 1000},
            {"Дата платежа": "2023-01-20", "Сумма платежа": 500},
            {"Дата платежа": "2023-02-05", "Сумма платежа": 2000},
            {"Дата платежа": "2023-01-25", "Сумма платежа": 1500},
        ]

    def test_investing_january(self):
        month = "2023-01"
        limit = 100
        expected_result = {
            "month": month,
            "rounding_step": limit,
            "total_amount": 300.0  # Ожидаемая сумма, отложенная в "Инвесткопилку"
        }
        result = investing(month, self.transactions, limit)
        self.assertEqual(json.loads(result), expected_result)

    def test_investing_february(self):
        month = "2023-02"
        limit = 200
        expected_result = {
            "month": month,
            "rounding_step": limit,
            "total_amount": 200.0
        }
        result = investing(month, self.transactions, limit)
        self.assertEqual(json.loads(result), expected_result)

    def test_investing_with_different_limit(self):
        month = "2023-01"
        limit = 50
        expected_result = {
            "month": month,
            "rounding_step": limit,
            "total_amount": 150.0  # Ожидаемая сумма, отложенная в "Инвесткопилку"
        }
        result = investing(month, self.transactions, limit)
        self.assertEqual(json.loads(result), expected_result)

    def test_investing_empty_transactions(self):
        month = "2023-01"
        limit = 100
        expected_result = {
            "month": month,
            "rounding_step": limit,
            "total_amount": 0.0  # Нет транзакций
        }
        result = investing(month, [], limit)
        self.assertEqual(json.loads(result), expected_result)


if __name__ == "__main__":
    unittest.main()
