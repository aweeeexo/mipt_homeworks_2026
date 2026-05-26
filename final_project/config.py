import os
import sys
import yaml
from dataclasses import dataclass


@dataclass
class AppConfig:
    api_key: str
    api_host: str
    folder_id: str
    limit_message: int | None
    limit_chars: int | None
    temperature: float
    system_prompt: str | None


def load_config() -> AppConfig:
    yaml_data = {}
    if os.path.exists('config.yaml'):
        with open('config.yaml', 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f) or {}

    api_key = os.environ.get('API_KEY') or yaml_data.get('api_key')
    api_host = os.environ.get('API_HOST') or yaml_data.get('api_host')
    folder_id = os.environ.get('FOLDER_ID') or yaml_data.get('folder_id')

    if not api_key or not api_host or not folder_id:
        print('Ошибка: Не заданы API_KEY, API_HOST или FOLDER_ID')
        sys.exit(1)

    return AppConfig(
        api_key=api_key,
        api_host=api_host,
        folder_id=folder_id,
        limit_message=int(os.environ.get('LIMIT_MESSAGE') or yaml_data.get('limit_message') or 0)
        or None,
        limit_chars=int(os.environ.get('LIMIT_CHARS') or yaml_data.get('limit_chars') or 0) or None,
        temperature=float(os.environ.get('TEMPERATURE') or yaml_data.get('temperature') or 0.7),
        system_prompt=yaml_data.get('system_prompt'),
    )
