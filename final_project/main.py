import os
from config import load_config
from llm_client import ChatSession
from file_processor import inject_files, chunk_file


def handle_file_chunk(session: ChatSession, command: str):
    print('>>> Введите путь до файла')
    filepath = input('>>> ').strip()
    if not os.path.exists(filepath):
        print('Файл не найден.')
        return

    print('>>> Принято. Что нужно сделать для каждого фрагмента (User Prompt)?')
    prompt = input('>>> ').strip()

    auto_yes = '-y' in command
    mode = 'paragraph'
    val = 1

    if 'paragraph=' in command:
        val = int(command.split('paragraph=')[1].split()[0])
    elif 'len=' in command:
        mode = 'len'
        val = int(command.split('len=')[1].split()[0])

    chunks = chunk_file(filepath, mode, val)
    print('>>> Принято. Начинаю обработку:')

    for i, chunk in enumerate(chunks):
        text_to_send = f'{prompt}\n\nТекст:\n{chunk}'
        print(f'\n--- Чанк {i + 1}/{len(chunks)} ---')
        session.ask(text_to_send)

        if not auto_yes and i < len(chunks) - 1:
            input('\n<нажмите enter для следующего чанка или Ctrl+C для отмены>')

    print('\n>>> Обработка файла завершена.')


def main():
    config = load_config()
    session = ChatSession(config)
    print('ИИ-ассистент запущен. Введите \\q для выхода, /reset для сброса.')

    while True:
        try:
            user_input = input('\n>>> ').strip()

            if user_input == '\\q':
                break
            elif user_input == '/reset':
                session.reset()
                os.system('cls' if os.name == 'nt' else 'clear')
                print('История очищена.')
                continue
            elif user_input.startswith('/filechunk'):
                handle_file_chunk(session, user_input)
                continue
            elif not user_input:
                continue

            processed_input = inject_files(user_input)

            print('>>> ', end='')
            session.ask(processed_input)

        except EOFError:
            break
        except Exception as e:
            print(f'Непредвиденная ошибка: {e}')


if __name__ == '__main__':
    main()
