import random


def random_password():
    return "".join(random.choices("0123456789", k=8))


def format_money(money):
    return f"{money:,.0f}".replace(",", ".")


# def get_client_ip(request):
#     x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(",")[0]
#     else:
#         ip = request.META.get("REMOTE_ADDR")
#     return ip
