import random


def random_password():
    return "".join(random.choices("0123456789", k=8))


def format_money(money):
    return f"{money:,.0f}".replace(",", ".")

