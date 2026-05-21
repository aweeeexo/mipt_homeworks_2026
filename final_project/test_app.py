from config import AppConfig
from llm_client import ChatSession
from file_processor import chunk_file


def test_config_init():
    config = AppConfig(
        api_key='test_key',
        api_host='test_host',
        folder_id='test_folder',
        limit_message=2,
        limit_chars=100,
        temperature=0.5,
        system_prompt='sys',
    )
    assert config.api_key == 'test_key'
    assert config.limit_message == 2


def test_trim_context_by_message():
    config = AppConfig('k', 'h', 'f', limit_message=2, limit_chars=None,
                       temperature=0.5, system_prompt='sys')
    session = ChatSession(config)
    session.history = [
        {'role': 'system', 'content': 'sys'},
        {'role': 'user', 'content': 'msg1'},
        {'role': 'assistant', 'content': 'msg2'},
        {'role': 'user', 'content': 'msg3'}
    ]
    session._trim_context(10)

    assert len(session.history) == 2
    assert session.history[1]['content'] == 'msg3'


def test_chunk_file_len(tmp_path):
    test_file = tmp_path / 'test.txt'
    test_file.write_text('1234567890', encoding='utf-8')
    chunks = chunk_file(str(test_file), mode='len', val=4)
    assert chunks == ['1234', '5678', '90']
