import string
import random


def random_str(long: int = 10, choice: int = 1) -> str:
    try:
        if choice == 1:
            return "".join(random.choices(string.ascii_uppercase, k=long))
        elif choice == 2:
            return "".join(random.choices(string.ascii_uppercase + string.digits, k=long))
        elif choice == 3:
            return "".join(random.choices(string.digits, k=long))
        elif choice == 4:
            return "".join(
                random.choices(f"{string.ascii_uppercase}{string.ascii_uppercase.lower()}{string.digits}", k=long))
        elif choice == 5:
            return "".join(random.choices(f"{string.ascii_uppercase}{string.ascii_uppercase.lower()}", k=long))
    except Exception as ex:
        print(ex)
        return "".join(random.choices(string.ascii_uppercase, k=long))
