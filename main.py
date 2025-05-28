from service_request.avito_token import avito_token
import requests
import json
from typing import Any, Dict, Optional

# Проверка работоспособности токенов сервисов
if avito_token:  # Авито
    print('Ура! Токен получен.')
else:
    print("Ошибка: токен Avito отсутствует.")


def load_config(path: str = 'config.json') -> Dict[str, Any]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Содержимое файла {path}:\n{content}")  # Вывод содержимого
            return json.loads(content)
    except FileNotFoundError:
        print(f"Файл {path} не найден.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Файл {path} содержит некорректный JSON: {e}")
        return {}



def search_resumes(config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    url = 'https://api.avito.ru/job/v1/resumes/'
    headers = {
        'Authorization': f"Bearer {avito_token}",
        'Content-Type': 'application/json'
    }
    params: Dict[str, Any] = {}

    # Учитываем только параметры с непустыми значениями
    for key, value in config.items():
        if value not in (None, [], {}):  # Игнорируем null, пустые массивы и словари
            if isinstance(value, list):
                params[key] = ','.join(map(str, value))  # Преобразуем массив в строку
            else:
                params[key] = value

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка {response.status_code}: {response.text}")
        return None


if __name__ == '__main__':
    config = load_config('config.json')
    result = search_resumes(config)
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
