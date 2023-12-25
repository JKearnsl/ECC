import logging

from src.core.cyclic import encode as cyclic_encode, calc_syndrome, BinStr

"""

Описание алгоритма БЧХ
Пусть информационный полином P(x) был закодирован образующим полиномом G(x) и была получена кодовая комбинация C(x). 
Если при делении кодовой комбинации на образующий полином получился ненулевой остаток, то значит существует ошибка, 
которую можно исправить следующим алгоритмом:
1. Получить остаток R(x) при делении кодовой комбинации C(x) на образующий полином G(x).
2. Подсчитать количество единиц в остатке.
3. Если количество единиц в остатке больше, чем количество t исправляемых данным образующим многочленом ошибок, 
то произвести циклический сдвиг кодовой комбинации C(x) влево на один бит. Перейти на шаг 1.
4. Прибавить по модулю два к кодовой комбинации C(x) остаток R(x).
5. Выполнить циклический сдвиг кодовой комбинации C(x) вправо на столько же бит, на сколько она перед этим была сдвинута 
влево.
Порождающий полином G(x) = 1011. 
Информационный код P(x) = 1010. 
Параметры порождающего полинома: 
n = 7 - количество бит в кодовой комбинации,
k = 4 - количество бит в информационном коде,
t = 1 - количество исправляемых ошибок.

Построим систематизированный код:
1. Степень G(x) равна 3, поэтому P(x) * 1000 = 1010 * 1000 = 1010000
2. Остаток R(x) = 1010000 mod G(x) = 1010000 mod 1011 = 11
3. Кодовая комбинация C(x) = 1010000 + R(x) = 1010011
Теперь для проверки нахождения и исправления ошибок внесём в кодовую комбинацию ошибку: С(x) = 0010011.
Производим декодирование:
1. R(x) := C(x) mod G(x) = 101
2. Количество единиц в остатке R(x) больше, чем t. Производим циклический сдвиг влево:
3. C(x) := 0100110
4. R(x) := C(x) mod G(x) = 1
5. Количество единиц в остатке R(x) равно t. Произведём сложение по модулю 2:
6. C(x) := C(x) + 1 = 0100111
7. Производим циклический сдвиг C(x) обратно вправо:
8. C(x) := 1010011


"""


def encode(to_encode: BinStr, polynom: BinStr):
    """
    :param to_encode:
    :param polynom:
    :return:
    """
    return cyclic_encode(to_encode, polynom)


def decode(to_decode: BinStr, polynom: BinStr, t: int) -> BinStr:
    assert all(bit in '01' for bit in to_decode), "Неверный вход: строка должна быть двоичной"

    shift_count = 0
    original_message = to_decode
    original_shift = 0  # Сохраняем исходный сдвиг

    while True:
        syndrome = calc_syndrome(to_decode, polynom)
        if syndrome == "0" * (len(polynom) - 1):
            logging.info(f"[Декодирование] Успешно декодировано без ошибок (синдром = {syndrome!r})")
            return to_decode[:-len(polynom) + 1]

        if syndrome.count('1') > t:
            logging.info(
                f"[Декодирование] Кол-во единиц в синдроме больше t ({syndrome.count('1')} > {t}) синдром = {syndrome!r}"
            )
            to_decode = to_decode[1:] + to_decode[0]
            shift_count += 1
            continue

        logging.info(
            f"[Декодирование] Кол-во единиц в синдроме меньше или равно t "
            f"({syndrome.count('1')} <= {t}) синдром = {syndrome!r}"
        )

        syndrome_int = list(map(int, syndrome))
        corrected_to_decode = list(map(int, to_decode))

        # Исправляем ошибки
        for i in range(len(syndrome_int)):
            if syndrome_int[i] == 1:
                error_position = len(to_decode) - i - 1
                corrected_to_decode[error_position] = 1 - corrected_to_decode[error_position]

        to_decode = "".join(map(str, corrected_to_decode))

        # Восстанавливаем сдвиг для исправленного сообщения
        for _ in range(shift_count):
            to_decode = to_decode[-1] + to_decode[:-1]

        logging.info(f"[Декодирование] Исправленная строка = {to_decode!r}")

        # Восстанавливаем исходный сдвиг для сравнения с оригинальным сообщением
        for _ in range(original_shift):
            original_message = original_message[-1] + original_message[:-1]

        return original_message[:-len(polynom) + 1]


def bch_decode(to_decode: str, polynom: str, t: int):
    shifts = 0
    len_message = len(to_decode) - len(polynom) + 1

    while True:
        remainder = calc_syndrome(to_decode, polynom)

        print(f"Кодовое слово: {to_decode}")
        print(f"Остаток: {remainder}")

        if remainder.count('1') > t:
            print("Слишком много единиц! Делаем сдвиг влево:")
            to_decode = to_decode[1:] + to_decode[0]
            shifts += 1
        else:
            print("Получилось! Исправляем многочлен:")
            to_decode = add_polynomials(to_decode, remainder)
            print(to_decode)
            break

    print(f"Теперь сдвигаем его вправо на {shifts}:")
    for _ in range(shifts):
        while len(to_decode) < len_message:
            to_decode = '0' + to_decode

        to_decode = to_decode[len(to_decode) - 1] + to_decode[:len(to_decode) - 1]


    print(to_decode)
    decoded_message = to_decode[:-len(polynom) + 1]
    return decoded_message


def add_polynomials(poly1, poly2):
    s1 = len(poly1)
    s2 = len(poly2)

    if s1 > s2:
        poly2 = ('0' * (s1 - s2)) + poly2
    elif s2 > s1:
        poly1 = ('0' * (s2 - s1)) + poly1

    result = ['0'] * s1

    for i in range(s1):
        result[i] = '1' if poly1[i] != poly2[i] else '0'

    index = 0
    for i in range(s1):
        if result[i] != '0':
            index = i
            break

    return ''.join(result[index:])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    message = '1101010'
    polynom = '111010001'
    t = 2

    # Кодирование сообщения
    encoded_message = encode(message, polynom)
    print(f"Закодированное сообщение: {encoded_message}")

    encoded_message = '000101011110010'

    # Декодирование сообщения
    decoded_message = bch_decode(encoded_message, polynom, t)
    print(f"Декодированное сообщение: {decoded_message}")

    # Проверка, что декодированное сообщение совпадает с исходным
    assert decoded_message == message


"""
Проверь вот у меня кусок кода на c# 
```cs
tbLog.AppendText("Теперь сдвигаем его вправо на "+shifts+":\r\n");
            for (int i = 0; i < shifts; i++)
            {
                string s = p1;
                if (s.Length < n1)
                {
                    while (s.Length < n1)
                    {
                        s = '0' + s;
                    }
                }
                s = s[s.Length-1] + s.Substring(0, s.Length-1);
                p1 = new Polynom(s);
            }
            tbLog.AppendText(p1 + "\r\n");
            tbCoded.Text = p1;
            tbResult.Text = ((string)p1).Substring(0, k);
```

И мой кусок кода на питоне
```python
print(f"Теперь сдвигаем его вправо на {shifts}:")
    for _ in range(shifts):
        to_decode = to_decode[-1] + to_decode[:-1]

    print(to_decode)
    decoded_message = to_decode[:-len(polynom) + 1]
    return decoded_message
```

у меня тут ошибка на питоне и нужно чтобы работало как на шарпах
"""