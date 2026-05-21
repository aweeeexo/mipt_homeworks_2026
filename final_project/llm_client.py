from openai import OpenAI
from config import AppConfig


class ChatSession:
    def __init__(self, config: AppConfig):
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key, base_url=config.api_host, project=config.folder_id
        )
        self.history: list[dict] = []

        if self.config.system_prompt:
            self.history.append({'role': 'system', 'content': self.config.system_prompt})

    def reset(self):
        self.history.clear()
        if self.config.system_prompt:
            self.history.append({'role': 'system', 'content': self.config.system_prompt})

    def _trim_context(self, new_msg_len: int):
        system_msg = [m for m in self.history if m['role'] == 'system']
        user_msgs = [m for m in self.history if m['role'] != 'system']

        if self.config.limit_message:
            while len(user_msgs) + 1 > self.config.limit_message and user_msgs:
                user_msgs.pop(0)

        if self.config.limit_chars:
            while user_msgs:
                current_chars = sum(len(m['content']) for m in user_msgs) + new_msg_len
                if current_chars <= self.config.limit_chars:
                    break
                user_msgs.pop(0)

        self.history = system_msg + user_msgs

    def ask(self, user_text: str):
        self._trim_context(len(user_text))

        if self.config.limit_chars and len(user_text) > self.config.limit_chars:
            user_text = user_text[-self.config.limit_chars :]

        self.history.append({'role': 'user', 'content': user_text})

        full_answer = ''
        try:
            stream = self.client.chat.completions.create(
                model=f'gpt://{self.config.folder_id}/yandexgpt-lite/latest',
                messages=self.history,
                temperature=self.config.temperature,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    if chunk.choices[0].delta.content is not None:
                        word = chunk.choices[0].delta.content
                        print(word, end='', flush=True)
                        full_answer += word
            print()
        except KeyboardInterrupt:
            print('\n[Запрос прерван пользователем]')
        except Exception as e:
            print(f'\n[Ошибка API: {e}]')

        if full_answer:
            self.history.append({'role': 'assistant', 'content': full_answer})
