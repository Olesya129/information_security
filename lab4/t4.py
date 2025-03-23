import random
import string


# шифрование методом Цезаря
def caesar_cipher(text, shift):
    result = ""  # переменная для хранения зашифрованного текста

    for char in text:
        is_upper = char.isupper()   # определяем является ли символ заглавной буквой
        char = char.lower()         # преобразуем символ в нижний регистр

        # сдвигаем символ на указанное кол-во позиций
        shifted_char = chr(((ord(char) - ord('a') + shift) % 26) + ord('a'))

        if is_upper:    # преобразуем символ обратно в верхний регистр
            shifted_char = shifted_char.upper()
        result += shifted_char

    return result


# шифрование методом Виженера
def vigenere_cipher(text, key, alphabet, mode="encrypt"):
    result = ""             # переменная для хранения
    key_length = len(key)   # длина ключа

    for i, char in enumerate(text):
        is_upper = char.isupper()   # определяем является ли символ заглавной буквой
        char = char.upper()         # преобразуем символ в верхний регистр

        key_char = key[i % key_length].upper()  # повторяем ключ если он короче текста
        row_index = alphabet.index(key_char)    # находим строку соответствующую символу ключа
        col_index = alphabet.index(char)        # находим столбец соответствующий символу текста

        if mode == "encrypt":
            shifted_char = alphabet[(row_index + col_index) % 26]   # индекс зашифрованного символа
        else:
            shifted_char = alphabet[(col_index - row_index) % 26]   # индекс первоначального символа

        # переводим обратно в нижний регистр
        if not is_upper:
            shifted_char = shifted_char.lower()
        result += shifted_char

    return result


# построение квадрата Виженера
def build_vigenere(alphabet):
    square = []
    for i in range(len(alphabet)): # сдвигаем на i позиций
        shifted_alphabet = alphabet[i:] + alphabet[:i]
        square.append(list(shifted_alphabet))
    return square


# читаем текст из файла
def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


# записываем зашифрованный текст в файл
def write_file(filename, text):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)


# генерация случайных символов
def generate_random_letters(length):
    letters = string.ascii_letters  # 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choice(letters) for _ in range(length))


if __name__ == "__main__":
    input_filename = "random_text.txt"

    # создаем файл random_text.txt, заполняем его
    random_text = generate_random_letters(2000)
    write_file(input_filename, random_text)

    # читаем текст из файла random_text.txt
    text = read_file(input_filename)
    if text is None:
        exit()

    method = input("Выберите метод шифрования:\n1 - Цезарь, 2 - Виженер: ")
    if method == "1":
        try:
            shift = int(input("Введите ключ N для шифрования: "))
        except ValueError:
            exit()

        encrypted_text = caesar_cipher(text, shift)     # шифруем
        encrypted_filename = "encC_Caesar.txt"
        decrypted_text = caesar_cipher(encrypted_text, -shift)  # расшифровываем
        decrypted_filename = "decC_Caesar.txt"

    elif method == "2":
        key = input("Введите ключевое слово: ")
        alphabet_option = input("Выберите алфавит замены:\n1 - по порядку, 2 - случайный: ")

        # генерация алфавита
        if alphabet_option == "1":
            alphabet = string.ascii_uppercase  # стандартный алфавит
        else:
            alphabet = list(string.ascii_uppercase)
            random.shuffle(alphabet)
            alphabet = "".join(alphabet)

        # строим квадрат Виженера
        vigenere_square = build_vigenere(alphabet)
        print("\nКвадрат Виженера:")
        for row in vigenere_square:
            print(" ".join(row))

        encrypted_text = vigenere_cipher(text, key, alphabet, mode="encrypt")   # шифруем
        encrypted_filename = "encV_Vigenere.txt"
        decrypted_text = vigenere_cipher(encrypted_text, key, alphabet, mode="decrypt")     # расшифровываем
        decrypted_filename = "decV_Vigenere.txt"

    else:
        print("Ошибка: выбран неверный метод")
        exit()

    # сохраняем зашифрованный текст
    write_file(encrypted_filename, encrypted_text)
    # сохраняем расшифрованный текст
    write_file(decrypted_filename, decrypted_text)

    print("\nПервые 20 символов для проверки:")
    print(f"random_text.txt: {text[:20]}")
    print(f"{encrypted_filename}: {encrypted_text[:20]}")
    print(f"{decrypted_filename}: {decrypted_text[:20]}")