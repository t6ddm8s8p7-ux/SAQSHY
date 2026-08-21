# -*- coding: utf-8 -*-
"""Умное сравнение ФИО: устойчиво к обрезанным отчествам, регистру, порядку слов."""
import re


def tokens(name):
    if not name:
        return []
    n = str(name).lower().replace("ё", "е")
    return [t for t in re.split(r"[\s,.]+", n) if t]


def _tok_ok(x, y):
    if x == y:
        return True
    if len(x) == 1 and y.startswith(x):   # «к» == «коржавовна»
        return True
    if len(y) == 1 and x.startswith(y):
        return True
    return False


def _align(short, long):
    """Все токены короткого имени должны совпасть (или по первой букве)."""
    if len(short) < 2:
        return False
    for i in range(len(short)):
        if not _tok_ok(short[i], long[i]):
            return False
    return True


def names_match(n1, n2):
    a, b = tokens(n1), tokens(n2)
    if not a or not b:
        return False
    if len(a) > len(b):
        a, b = b, a
    if _align(a, b):                      # тот же порядок слов
        return True
    if _align(a[::-1], b[::-1]):          # обратный порядок (имя перед фамилией)
        return True
    if _align(a, b[::-1]):                # один список перевёрнут
        return True
    return False


def norm_key(name):
    """Ключ для группировки: фамилия+имя (без отчества)."""
    t = tokens(name)
    return " ".join(t[:2]) if t else ""