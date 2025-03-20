import math

def power_alphabet(password: str) -> int:
    uppercase = any(c.isupper() for c in password)  # заглавные
    lowercase = any(c.islower() for c in password)  # строчные
    numbers = any(c.isdigit() for c in password)    # цифры
    special = any(c in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for c in password)  # спец символы

    if special:
        return 95  # Включает все символы
    if uppercase and lowercase:
        return 52  # Заглавные и строчные буквы
    if (uppercase or lowercase) and numbers:
        return 36  # Буквы (один регистр) и цифры
    if uppercase or lowercase:
        return 26  # Только заглавные или только строчные буквы
    if numbers and not (uppercase or lowercase or special):  # только цифры
        return 10  # Алфавит из 10 цифр (0-9)
    return 0       # Если пароль пустой или нет подходящих символов

# мощность пространства паролей
def calculate_combinations(password: str) -> int:
    N = power_alphabet(password)    # мощность алфавита
    L = len(password)               # длина пароля
    return N ** L       # возвращает M=N^L


# время перебора
def calculate_time(combinations: int, s: int, m: int, v: int) -> int:
    time_without_delay = combinations / s  # время перебора без задержек

    # Проверяем, есть ли лишняя задержка
    if combinations % m == 0:
        delay_time = (combinations // m - 1) * v  # если делится без остатка уменьшаем число задержек на 1
    else:
        delay_time = (combinations // m) * v

    return math.ceil(time_without_delay + delay_time)  # возвращаем общее время, округляем до целого


def output_responses(seconds: int) -> str:
    years, seconds = divmod(seconds, 365 * 24 * 3600)   # года и остаток секунд
    months, seconds = divmod(seconds, 30 * 24 * 3600)   # месяца и остаток секунд
    days, seconds = divmod(seconds, 24 * 3600)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{years} лет {months} месяцев {days} дней {hours} часов {minutes} минут {seconds} секунд"


def main():
    password = input("Введите пароль: ")
    s = int(input("Введите s - скорость перебора паролей в секунду: "))
    m = int(input("Введите m - количество неправильных попыток перед паузой: "))
    v = int(input("Введите v - задержку в секундах после m неудачных попыток: "))

    combinations = calculate_combinations(password)
    time_to_crack = calculate_time(combinations, s, m, v)
    formatted_time = output_responses(time_to_crack)

    print(f"Мощность алфавита: {power_alphabet(password)}")
    print(f"Количество возможных комбинаций: {combinations}")
    print(f"Время полного перебора: {formatted_time}")


if __name__ == "__main__":
    main()
