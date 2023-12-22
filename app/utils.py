import random


def random_password():
    lower = "abcdefghijklmnopqrstuvwxyz"
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    numbers = "0123456789"
    symbols = "@#$&_-()=%*:/!?+."
    string = lower + upper + numbers + symbols
    password = "".join(random.sample(string, 12))
    return password
