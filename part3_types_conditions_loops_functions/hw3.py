#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"


EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": (),
}


financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    if year % 4 == 0:
        return True
    return False


def get_days_in_month(month: int, year: int) -> int:
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if month == 2 and is_leap_year(year):
        return 29
    return days_in_month[month - 1]


def is_valid_date(day: int, month: int, year: int) -> bool:
    if year < 1 or month < 1 or month > 12 or day < 1:
        return False
    return day <= get_days_in_month(month, year)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    parts = maybe_dt.split('-')
    if len(parts) != 3:
        return None

    try:
        day = int(parts[0])
        month = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return None

    if is_valid_date(day, month, year):
        return (day, month, year)
    return None


def parse_amount(amount_str: str) -> float | None:
    try:
        amount_str = amount_str.replace(',', '.')
        return float(amount_str)
    except ValueError:
        return None


def validate_date(date_str: str) -> tuple[int, int, int] | None:
    return extract_date(date_str)


def get_common_categories() -> str:
    categories = []
    for common, targets in EXPENSE_CATEGORIES.items():
        for target in targets:
            categories.append(f"{common}::{target}")
    return "\n".join(sorted(categories))


def is_valid_category(category_name: str) -> bool:
    parts = category_name.split('::')
    if len(parts) != 2:
        return False

    common, target = parts
    if common not in EXPENSE_CATEGORIES:
        return False

    if target not in EXPENSE_CATEGORIES[common]:
        return False

    return True


def income_handler(amount: float, income_date: str) -> str:
    financial_transactions_storage.append({
        "type": "income",
        "amount": amount,
        "date": income_date
    })
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    financial_transactions_storage.append({
        "type": "cost",
        "category": category_name,
        "amount": amount,
        "date": income_date
    })
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return get_common_categories()


def get_date_key(day: int, month: int, year: int) -> int:
    return year * 10000 + month * 100 + day


def get_month_key(day: int, month: int, year: int) -> int:
    return year * 100 + month


def stats_handler(report_date: str) -> str:
    date_tuple = extract_date(report_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG

    report_day, report_month, report_year = date_tuple
    report_date_key = get_date_key(report_day, report_month, report_year)
    report_month_key = get_month_key(report_day, report_month, report_year)

    total_capital = 0.0
    monthly_income = 0.0
    monthly_expenses = 0.0
    category_expenses = {}

    for transaction in financial_transactions_storage:
        trans_date = transaction["date"]
        trans_date_tuple = extract_date(trans_date)
        if trans_date_tuple is None:
            continue

        trans_day, trans_month, trans_year = trans_date_tuple
        trans_date_key = get_date_key(trans_day, trans_month, trans_year)

        if trans_date_key > report_date_key:
            continue

        amount = transaction["amount"]
        total_capital += amount if transaction["type"] == "income" else -amount

        trans_month_key = get_month_key(trans_day, trans_month, trans_year)
        if trans_month_key == report_month_key:
            if transaction["type"] == "income":
                monthly_income += amount
            else:
                monthly_expenses += amount
                category = transaction.get("category", "")
                category_expenses[category] = category_expenses.get(category, 0) + amount

    result = f"Your statistics as of {report_date}:\n"
    result += f"Total capital: {total_capital:.2f} rubles\n"

    monthly_result = monthly_income - monthly_expenses

    if monthly_result >= 0:
        result += f"This month, the profit amounted to {monthly_result:.2f} rubles.\n"
    else:
        result += f"This month, the loss amounted to {abs(monthly_result):.2f} rubles.\n"

    result += f"Income: {monthly_income:.2f} rubles\n"
    result += f"Expenses: {monthly_expenses:.2f} rubles\n"

    if category_expenses:
        result += "\nDetails (category: amount):\n"
        sorted_categories = sorted(category_expenses.keys())
        for i, category in enumerate(sorted_categories, 1):
            amount = category_expenses[category]
            amount_str = f"{amount:,.2f}".replace('.', ',').replace(',', '.', 1) if '.' in f"{amount:.2f}" else f"{amount:.2f}".replace('.', ',')
            result += f"{i}. {category}: {amount_str}\n"
    else:
        result += "\nDetails (category: amount):\n"

    return result.rstrip()


def main() -> None:
    while True:
        try:
            user_input = input().strip()
            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0].lower()

            if command == "income":
                if len(parts) != 3:
                    print(UNKNOWN_COMMAND_MSG)
                    continue

                amount_str = parts[1]
                date_str = parts[2]

                amount = parse_amount(amount_str)
                if amount is None or amount <= 0:
                    print(NONPOSITIVE_VALUE_MSG)
                    continue

                if validate_date(date_str) is None:
                    print(INCORRECT_DATE_MSG)
                    continue

                result = income_handler(amount, date_str)
                print(result)

            elif command == "cost":
                if len(parts) == 2 and parts[1] == "categories":
                    result = cost_categories_handler()
                    print(result)
                elif len(parts) == 4:
                    category_name = parts[1]
                    amount_str = parts[2]
                    date_str = parts[3]

                    if not is_valid_category(category_name):
                        print(NOT_EXISTS_CATEGORY)
                        print(get_common_categories())
                        continue

                    amount = parse_amount(amount_str)
                    if amount is None or amount <= 0:
                        print(NONPOSITIVE_VALUE_MSG)
                        continue

                    if validate_date(date_str) is None:
                        print(INCORRECT_DATE_MSG)
                        continue

                    result = cost_handler(category_name, amount, date_str)
                    print(result)
                else:
                    print(UNKNOWN_COMMAND_MSG)

            elif command == "stats":
                if len(parts) != 2:
                    print(UNKNOWN_COMMAND_MSG)
                    continue

                date_str = parts[1]
                if validate_date(date_str) is None:
                    print(INCORRECT_DATE_MSG)
                    continue

                result = stats_handler(date_str)
                print(result)

            else:
                print(UNKNOWN_COMMAND_MSG)

        except EOFError:
            break


if __name__ == "__main__":
    main()