import string
import random


def random_str(long: int = 10, choice: int = 1) -> str:
    if choice == 1:
        return "".join(random.choices(string.ascii_uppercase + string.ascii_uppercase, k=long))
    elif choice == 2:
        return "".join(random.choices(string.digits, k=long))
    elif type == 3:
        return "".join(random.choices(string.ascii_uppercase + string.ascii_uppercase + string.digits, k=long))
