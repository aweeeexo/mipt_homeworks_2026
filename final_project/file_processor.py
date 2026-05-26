import os
import re

MAX_FILE_SIZE = 5 * 1024 * 1024


def inject_files(text: str) -> str:
    pattern = r'@::(.+?)::'
    matches = re.finditer(pattern, text)

    for match in matches:
        filepath = match.group(1)
        if not os.path.exists(filepath):
            text = text.replace(match.group(0), f'\n[Ошибка: Файл {filepath} не найден]\n')
            continue

        if os.path.getsize(filepath) > MAX_FILE_SIZE:
            text = text.replace(match.group(0), f'\n[Ошибка: Файл {filepath} превышает 5МБ]\n')
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            text = text.replace(match.group(0), f'\n{content}\n')

    return text


def chunk_file(filepath: str, mode: str, val: int = 1) -> list[str]:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if mode == 'len':
        return [content[i : i + val] for i in range(0, len(content), val)]

    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    chunks = []
    for i in range(0, len(paragraphs), val):
        chunks.append('\n\n'.join(paragraphs[i : i + val]))
    return chunks
