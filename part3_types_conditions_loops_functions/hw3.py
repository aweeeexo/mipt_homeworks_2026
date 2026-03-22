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
    "Other": ("Other",),
}

financial_transactions_storage: list[dict[str, Any]] = []

EXPECTED_PARTS_INCOME = 3
EXPECTED_PARTS_COST_CATEGORIES = 2
EXPECTED_PARTS_COST_FULL = 4
EXPECTED_PARTS_STATS = 2
MONTH_FEBRUARY = 2
MONTH_MAX = 12
DATE_PARTS_COUNT = 3
CATEGORY_PARTS_COUNT = 2


def is_leap_year(year: int) -> bool:
    return (year % 4 == 0) and (year % 100 != 0 or year % 400 == 0)


def get_days_in_month(month: int, year: int) -> int:
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if month == MONTH_FEBRUARY and is_leap_year(year):
        return 29
    return days_in_month[month - 1]


def is_valid_date(day: int, month: int, year: int) -> bool:
    if year < 1 or month < 1 or month > MONTH_MAX or day < 1:
        return False
    return day <= get_days_in_month(month, year)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")
    if len(parts) != DATE_PARTS_COUNT:
        return None
    try:
        day, month, year = map(int, parts)
    except ValueError:
        return None
    if is_valid_date(day, month, year):
        return day, month, year
    return None


def parse_amount(amount_str: str) -> float | None:
    try:
        amount_str = amount_str.replace(",", ".")
        return float(amount_str)
    except ValueError:
        return None


def get_full_categories_list() -> str:
    categories = []
    for common, targets in EXPENSE_CATEGORIES.items():
        categories.extend(f"{common}::{target}" for target in targets)
    return "\n".join(categories)


def is_valid_category(category_name: str) -> bool:
    parts = category_name.split("::")
    if len(parts) != CATEGORY_PARTS_COUNT:
        return False
    common, target = parts
    return common in EXPENSE_CATEGORIES and target in EXPENSE_CATEGORIES[common]


def income_handler(amount: float, income_date: str) -> str:
    date_tuple = extract_date(income_date)
    if date_tuple is None:
        financial_transactions_storage.append({"amount": amount, "date": None})
        return INCORRECT_DATE_MSG
    if amount <= 0:
        financial_transactions_storage.append({"amount": amount, "date": date_tuple})
        return NONPOSITIVE_VALUE_MSG
    financial_transactions_storage.append({"amount": amount, "date": date_tuple})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    date_tuple = extract_date(income_date)
    if date_tuple is None:
        financial_transactions_storage.append({"category": category_name, "amount": amount, "date": None})
        return INCORRECT_DATE_MSG
    if amount <= 0:
        financial_transactions_storage.append({"category": category_name, "amount": amount, "date": date_tuple})
        return NONPOSITIVE_VALUE_MSG
    if not is_valid_category(category_name):
        financial_transactions_storage.append({"category": category_name, "amount": amount, "date": date_tuple})
        return NOT_EXISTS_CATEGORY
    financial_transactions_storage.append({"category": category_name, "amount": amount, "date": date_tuple})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return get_full_categories_list()


def get_month_key(_day: int, month: int, year: int) -> int:
    return year * 100 + month


def stats_handler(report_date: str) -> str:
    parsed = extract_date(report_date)
    if parsed is None:
        return INCORRECT_DATE_MSG

    day, month, year = parsed

    total_capital = 0.0
    month_income = 0.0
    month_expenses = 0.0
    expenses_by_category: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        amount = transaction["amount"]
        t_date = transaction["date"]
        if t_date is None:
            continue
        t_day, t_month, t_year = t_date

        is_before_or_equal = (t_year < year) or (t_year == year and t_month < month) or \
                             (t_year == year and t_month == month and t_day <= day)

        if is_before_or_equal:
            total_capital += amount

        if t_year == year and t_month == month:
            if "category" in transaction:
                month_expenses += amount
                cat = transaction["category"]
                expenses_by_category[cat] = expenses_by_category.get(cat, 0.0) + amount
            else:
                month_income += amount

    result = f"Your statistics as of {report_date}:\n"
    result += f"Total capital: {total_capital:.2f} rubles\n"

    profit_loss = month_income - month_expenses
    if profit_loss >= 0:
        result += f"This month, the profit amounted to {profit_loss:.2f} rubles.\n"
    else:
        result += f"This month, the loss amounted to {abs(profit_loss):.2f} rubles.\n"

    result += f"Income: {month_income:.2f} rubles\n"
    result += f"Expenses: {month_expenses:.2f} rubles\n"

    if expenses_by_category:
        result += "\nDetails (category: amount):\n"
        sorted_categories = sorted(expenses_by_category.keys())
        for i, cat in enumerate(sorted_categories, 1):
            amount = expenses_by_category[cat]
            amount_str = f"{int(amount)}" if amount == int(amount) else f"{amount:.2f}".replace(".", ",")
            result += f"{i}. {cat}: {amount_str}\n"
    else:
        result += "\nDetails (category: amount):\n"

    return result.rstrip("\n")


def process_income(parts: list[str]) -> None:
    if len(parts) != EXPECTED_PARTS_INCOME:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount_str = parts[1]
    date_str = parts[2]

    amount = parse_amount(amount_str)
    if amount is None:
        print(NONPOSITIVE_VALUE_MSG)
        return

    result = income_handler(amount, date_str)
    print(result)


def process_cost(parts: list[str]) -> None:
    if len(parts) == EXPECTED_PARTS_COST_CATEGORIES and parts[1] == "categories":
        print(cost_categories_handler())
        return

    if len(parts) != EXPECTED_PARTS_COST_FULL:
        print(UNKNOWN_COMMAND_MSG)
        return

    category = parts[1]
    amount_str = parts[2]
    date_str = parts[3]

    amount = parse_amount(amount_str)
    if amount is None:
        print(NONPOSITIVE_VALUE_MSG)
        return

    result = cost_handler(category, amount, date_str)
    if result == NOT_EXISTS_CATEGORY:
        print(NOT_EXISTS_CATEGORY)
        print(get_full_categories_list())
    else:
        print(result)


def process_stats(parts: list[str]) -> None:
    if len(parts) != EXPECTED_PARTS_STATS:
        print(UNKNOWN_COMMAND_MSG)
        return

    date_str = parts[1]
    result = stats_handler(date_str)
    print(result)


def main() -> None:
    while True:
        try:
            line = input().strip()
        except EOFError:
            break

        if not line:
            continue

        parts = line.split()
        command = parts[0]

        if command == "income":
            process_income(parts)
        elif command == "cost":
            process_cost(parts)
        elif command == "stats":
            process_stats(parts)
        elif command == "exit":
            break
        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
