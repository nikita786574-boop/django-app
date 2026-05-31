"""Утилиты для генерации slug из кириллических названий (транслитерация)."""

from django.utils.text import slugify

# Карта транслитерации кириллицы в латиницу (ГОСТ-подобная схема).
_TRANSLIT_MAP = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def transliterate(text):
    """Преобразует кириллицу в латиницу посимвольно."""
    result = []
    for char in text or '':
        lower = char.lower()
        mapped = _TRANSLIT_MAP.get(lower)
        if mapped is None:
            result.append(char)
        elif char.isupper():
            result.append(mapped.capitalize())
        else:
            result.append(mapped)
    return ''.join(result)


def slugify_ru(text):
    """Транслитерирует кириллицу и приводит к корректному slug."""
    return slugify(transliterate(text))


def unique_slug(model, base, *, exclude_pk=None):
    """Возвращает уникальный slug для модели на основе base.

    Если base уже занят, добавляет числовой суффикс: base-2, base-3, ...
    """
    base = base or model._meta.model_name
    slug = base
    counter = 2
    qs = model._default_manager.all()
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    while qs.filter(slug=slug).exists():
        slug = f"{base}-{counter}"
        counter += 1
    return slug
