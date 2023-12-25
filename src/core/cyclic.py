"""
    Циклические коды


"""
import logging

from src.core.utils import build_syndrome_cyclic_matrix

BinStr = str


def encode(to_encode: BinStr, polynom: BinStr) -> BinStr:
    """
    :param to_encode: Строка для кодирования
    :param polynom: Порождающий полином

    :return: Закодированная строка
    """

    source = to_encode
    to_encode = to_encode + "0" * (len(polynom) - 1)
    check_bits = calc_syndrome(to_encode, polynom)
    return source + check_bits


def decode(to_decode: BinStr, polynom: BinStr, max_req: int = 10) -> BinStr:
    """
    :param to_decode: Строка для декодирования
    :param polynom: Порождающий полином
    :param max_req: Максимальное количество запросов на декодирование

    :return: Декодированная строка
    """

    syndrome = calc_syndrome(to_decode, polynom)
    if syndrome == "0" * (len(polynom) - 1):
        logging.info(f"Успешно декодировано без ошибок синдром ошибки = {syndrome!r}")
        return to_decode[:-len(polynom) + 1]
    else:
        logging.info(f"[Осталось попыток: {max_req - 1}] Декодирование с ошибкой, синдром ошибки = {syndrome!r}")
        syndrome_matrix = build_syndrome_cyclic_matrix(calc_syndrome, polynom)
        error_index = syndrome_matrix.index(list(map(int, syndrome)))
        logging.info(f"Индекс ошибки = {error_index!r}")

        to_decode = list(to_decode)
        to_decode[-(error_index + 1)] = str(int(not int(to_decode[-(error_index + 1)])))
        to_decode = "".join(to_decode)

        logging.info(f"Исправленная строка = {to_decode!r}")
        if max_req == 0:
            logging.info("Достигнуто максимальное количество попыток декодирования")
            logging.info("Декодирование > 1 ошибки негарантированно")
            return to_decode[:-len(polynom) + 1]

        return decode(to_decode, polynom, max_req - 1)


def calc_syndrome(value: BinStr, polynom: BinStr) -> BinStr:
    """
        Расчет синдрома

        :param value: бинарная строка
        :param polynom: Порождающий полином
        :return: Синдром
    """

    value = list(map(int, value))
    polynom = list(map(int, polynom))
    for i in range(len(value) - len(polynom) + 1):
        if value[i] == 1:
            for j in range(len(polynom)):
                value[i + j] = (value[i + j] + polynom[j]) % 2

    return "".join(map(str, value[-len(polynom) + 1:]))


if __name__ == "__main__":
    encoded = encode("01101011011", "10011")
    print(encoded)
    decoded = decode("011010110011110", "10011")
    print(decoded)
    print(encoded == decoded)
