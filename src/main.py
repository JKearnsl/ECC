import logging

from src.core.utils import syndrome_table, DICT_POLYNOM, polynom_table
from src.core.cyclic import encode, decode, calc_syndrome
from src.core.bch import encode_bch, decode_bch


def encode_dialog():
    print("Выберите порождающий полином:")
    print(polynom_table())
    index = int(input("Введите номер полинома: "))
    polynom = DICT_POLYNOM[index]
    print(f"Порождающий полином: {polynom[1]} / {polynom[2]}")
    to_encode = input(f"\nВведите bin строку для кодирования({polynom[3][1]} символов): ")
    assert len(to_encode) == polynom[3][1], "Неверная длина строки"
    print(f"Результат кодирования: {encode(to_encode, polynom[2])}\n")


def decode_dialog():
    print("Выберите порождающий полином:")
    print(polynom_table())
    index = int(input("Введите номер полинома: "))
    polynom = DICT_POLYNOM[index]
    to_decode = input(f"\nВведите bin строку для декодирования({polynom[3][0]} символов): ")
    assert len(to_decode) == polynom[3][0], "Неверная длина строки"
    print(f"Порождающий полином: {polynom[1]} / {polynom[2]}")
    print(f"Результат декодирования: {decode(to_decode, polynom[2])}\n")


def print_syndrome_matrix():
    print("Выберите порождающий полином:")
    print(polynom_table())
    index = int(input("Введите номер полинома: "))
    polynom = DICT_POLYNOM[index]
    print(f"Порождающий полином: {polynom[1]} / {polynom[2]}")
    print("Таблица синдромов:")
    print(syndrome_table(calc_syndrome, polynom[2]))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    print("Что вы хотите сделать?")
    while True:
        print("1. Закодировать")
        print("2. Декодировать")
        print("3. Вывести матрицу синдромов (поиск индекса ошибки)")
        print("4. Выйти")
        choice = input("Выберите действие: ")
        if choice == "1":
            encode_dialog()
        elif choice == "2":
            decode_dialog()
        elif choice == "3":
            print_syndrome_matrix()
        elif choice == "4":
            break
        else:
            print("Неверный ввод")
        print()
