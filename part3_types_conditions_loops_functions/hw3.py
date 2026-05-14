#!/usr/bin/env python

import sys
from collections.abc import Generator

Transaction = dict[str, str | float | tuple[int, int, int]]
CostDict = dict[str, float]

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

DATE_PARTS = 3
MONTH_MAX = 12
CATEGORY_PARTS = 2
FEBRUARY = 2
FEB_LEAP_DAYS = 29

KEY_TYPE = "type"
KEY_AMOUNT = "amount"
KEY_DATE = "date"
KEY_CATEGORY = "category"

VALUE_INCOME = "income"
VALUE_COST = "cost"

INCOME_ARGS = 3
COST_ARGS = 4
COST_CATEGORIES_ARGS = 2
STATS_ARGS = 2

DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}

financial_transactions_storage: list[Transaction] = []


def _is_leap_year(year: int) -> bool:
    if year % 4 != 0:
        return False
    if year % 100 == 0:
        return year % 400 == 0
    return True


def _extract_date(maybe_date: str) -> tuple[int, int, int] | None:
    parts = maybe_date.split("-")
    if len(parts) != DATE_PARTS:
        return None

    for part in parts:
        if not part.isdigit():
            return None

    day_str, month_str, year_str = parts
    day = int(day_str)
    month = int(month_str)
    year = int(year_str)

    if not (1 <= month <= MONTH_MAX):
        return None

    if month == FEBRUARY and _is_leap_year(year):
        max_days = FEB_LEAP_DAYS
    else:
        max_days = DAYS_IN_MONTH[month - 1]

    if 1 <= day <= max_days:
        return (day, month, year)
    return None


def _is_valid_category(category_name: str) -> bool:
    parts = category_name.split("::")
    if len(parts) != CATEGORY_PARTS:
        return False
    common, target = parts
    return common in EXPENSE_CATEGORIES and target in EXPENSE_CATEGORIES[common]


def _add_income(amount: float, date_tuple: tuple[int, int, int]) -> str:
    financial_transactions_storage.append(
        {
            KEY_TYPE: VALUE_INCOME,
            KEY_AMOUNT: amount,
            KEY_DATE: date_tuple,
        }
    )
    return OP_SUCCESS_MSG


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    date_tuple = _extract_date(income_date)
    if date_tuple is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    return _add_income(amount, date_tuple)


def _add_cost(category_name: str, amount: float, date_tuple: tuple[int, int, int]) -> str:
    financial_transactions_storage.append(
        {
            KEY_TYPE: VALUE_COST,
            KEY_AMOUNT: amount,
            KEY_DATE: date_tuple,
            KEY_CATEGORY: category_name,
        }
    )
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    date_tuple = _extract_date(income_date)
    if date_tuple is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    if not _is_valid_category(category_name):
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY

    return _add_cost(category_name, amount, date_tuple)


def cost_categories_handler() -> str:
    lines = [
        f"{common}::{target}"
        for common, targets in EXPENSE_CATEGORIES.items()
        for target in targets
    ]
    return "\n".join(lines)


def _transaction_date_le(transaction: Transaction, target_date: tuple[int, int, int]) -> bool:
    transaction_date = transaction[KEY_DATE]
    if isinstance(transaction_date, tuple):
        t_day, t_month, t_year = transaction_date
        target_day, target_month, target_year = target_date
        return (t_year, t_month, t_day) <= (target_year, target_month, target_day)
    return False


def _filter_transactions_until(date_tuple: tuple[int, int, int]) -> list[Transaction]:
    return [
        transaction
        for transaction in financial_transactions_storage
        if transaction and _transaction_date_le(transaction, date_tuple)
    ]


def _same_month_year(transaction: Transaction, target_year: int, target_month: int) -> bool:
    transaction_date = transaction[KEY_DATE]
    if isinstance(transaction_date, tuple):
        _, t_month, t_year = transaction_date
        return t_year == target_year and t_month == target_month
    return False


def _is_income(transaction: Transaction) -> bool:
    return transaction.get(KEY_TYPE) == VALUE_INCOME


def _is_cost(transaction: Transaction) -> bool:
    return transaction.get(KEY_TYPE) == VALUE_COST


def _calculate_totals(transactions: list[Transaction]) -> tuple[float, float]:
    total_expense = 0
    total_income = 0
    for transaction in transactions:
        val = transaction.get(KEY_AMOUNT, 0)
        if isinstance(val, (int, float, str)):
            amount = float(val)
        else:
            amount = 0

        if _is_income(transaction):
            total_income += amount
        elif _is_cost(transaction):
            total_expense += amount
    return total_expense, total_income


def _aggregate_costs(transactions: list[Transaction], target_year: int, target_month: int) -> CostDict:
    result: dict[str, float] = {}
    for transaction in transactions:
        if not _is_cost(transaction) or not _same_month_year(transaction, target_year, target_month):
            continue

        category = str(transaction[KEY_CATEGORY])
        val = transaction[KEY_AMOUNT]
        if isinstance(val, (int, float, str)):
            amount = float(val)
        else:
            amount = 0

        current = result.get(category, 0)
        result[category] = current + amount

    return {key: round(value, 2) for key, value in result.items()}


def _format_stats_lines(
    report_date: str,
    total_expense_all: float,
    total_income_all: float,
    category_expenses_month: CostDict,
) -> list[str]:
    capital = total_income_all - total_expense_all
    profit_word = "profit" if capital >= 0 else "loss"

    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {capital:.2f} rubles",
        f"This month, the {profit_word} amounted to {capital:.2f} rubles.",
        f"Income: {total_income_all:.2f} rubles",
        f"Expenses: {total_expense_all:.2f} rubles",
        "",
        "Details (category: amount):",
    ]

    for index, (category, amount) in enumerate(category_expenses_month.items()):
        lines.append(f"{index}. {category}: {amount:.2f}")

    return lines


def _format_stats(
    report_date: str,
    total_expense_all: float,
    total_income_all: float,
    category_expenses_month: CostDict,
) -> str:
    stats_lines = _format_stats_lines(
        report_date,
        total_expense_all,
        total_income_all,
        category_expenses_month,
    )
    return "\n".join([*stats_lines, ""])


def stats_handler(report_date: str) -> str:
    date_tuple = _extract_date(report_date)
    if date_tuple is None:
        return INCORRECT_DATE_MSG

    relevant_transactions = _filter_transactions_until(date_tuple)
    total_expense_all, total_income_all = _calculate_totals(relevant_transactions)

    _, target_month, target_year = date_tuple
    category_expenses_month = _aggregate_costs(relevant_transactions, target_year, target_month)

    return _format_stats(report_date, total_expense_all, total_income_all, category_expenses_month)


def _parse_amount(amount_str: str) -> float | None:
    clean_string = amount_str.replace(",", ".")
    check_string = clean_string.replace(".", "", 1).lstrip("-")
    if check_string.isdigit():
        return float(clean_string)
    return None


def _handle_income(parts: list[str]) -> None:
    if len(parts) != INCOME_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = _parse_amount(parts[1])
    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    print(income_handler(amount, parts[2]))


def _handle_cost(parts: list[str]) -> None:
    if len(parts) > 1 and parts[1] == "categories":
        if len(parts) == COST_CATEGORIES_ARGS:
            print(cost_categories_handler())
        else:
            print(UNKNOWN_COMMAND_MSG)
        return

    if len(parts) != COST_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount = _parse_amount(parts[2])
    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return

    print(cost_handler(parts[1], amount, parts[3]))


def _handle_stats_command(parts: list[str]) -> None:
    if len(parts) != STATS_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return
    print(stats_handler(parts[1]))


def _read_lines() -> Generator[str]:
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if line:
            yield line


COMMAND_HANDLERS = {
    "income": _handle_income,
    "cost": _handle_cost,
    "stats": _handle_stats_command,
}


def main() -> None:
    for line in _read_lines():
        parts = line.split()
        if not parts:
            continue
        handler = COMMAND_HANDLERS.get(parts[0])
        if handler:
            handler(parts)
        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
