import pandas as pd
import re
import os

INPUT_FILE = 'questions_raw.txt'
OUTPUT_FILE = 'exam_questions.csv'


def parse_questions(file_path):
    """Читает сырой текст и надежно извлекает номера, вопросы и полные ответы"""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Разделяем весь текст по маркерам начала вопроса "## "
    blocks = text.split('## ')

    data = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Разделяем блок на заголовок (первая строка) и всё остальное (ответ)
        # maxsplit=1 гарантирует, что мы разрежем только по первому переносу строки
        lines = block.split('\n', 1)
        if len(lines) < 2:
            continue

        header = lines[0].strip()
        answer = lines[1].strip()  # Здесь теперь сохранится ВЕСЬ текст ответа, включая абзацы

        # Извлекаем номер и текст вопроса из заголовка (формат: "1. Текст вопроса")
        match = re.match(r'^(\d+)\.\s*(.*)$', header)
        if match:
            num = int(match.group(1))
            question = match.group(2).strip()

            data.append({
                'Number': num,
                'Question': question,
                'Answer': answer,
                'Score': 0
            })

    # Сортируем по номеру вопроса на всякий случай
    data.sort(key=lambda x: x['Number'])
    return data


if __name__ == "__main__":
    print("🚀 Запуск улучшенного парсера вопросов...")

    if not os.path.exists(INPUT_FILE):
        print(f"❌ Ошибка: Файл '{INPUT_FILE}' не найден в папке!")
        print("Пожалуйста, сохрани текст вопросов в этот файл и запусти скрипт снова.")
    else:
        data = parse_questions(INPUT_FILE)

        if not data:
            print("⚠️ Не удалось распознать вопросы. Проверь, что в файле есть заголовки вида '## 1. Текст'.")
        else:
            df = pd.DataFrame(data)
            # utf-8-sig критически важен для корректного открытия кириллицы и переносов строк в Excel
            df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

            print(f"✅ Успех! Создан файл '{OUTPUT_FILE}' с {len(df)} вопросами.")
            print("🎮 Теперь можешь запускать свою игру (python exam_game.py)!")