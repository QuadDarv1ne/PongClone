#!/usr/bin/env python3
"""
GigaChat CLI - простой интерфейс для GigaChat AI
"""
import sys
import os

try:
    from gigachat import GigaChat
except ImportError:
    print("Установите: pip install gigachat")
    sys.exit(1)


def get_client() -> GigaChat:
    """Создать клиент GigaChat"""
    # Авторизация через переменные окружения
    credentials = os.getenv("GIGACHAT_CREDENTIALS")
    
    if not credentials:
        # Пробуем без авторизации (ограниченный режим)
        return GigaChat(verify_ssl_certs=False)
    
    return GigaChat(credentials=credentials, verify_ssl_certs=False)


def chat(client: GigaChat, prompt: str) -> str:
    """Отправить запрос к AI"""
    response = client.chat(prompt)
    return response.choices[0].message.content


def main():
    """Основной цикл"""
    print("GigaChat CLI (q - выход)")
    print("-" * 40)
    
    client = get_client()
    
    while True:
        try:
            user_input = input("\nВы: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ('q', 'quit', 'exit'):
                print("Выход...")
                break
            
            print("\nAI: ", end="", flush=True)
            response = chat(client, user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\nПрервано")
            break
        except Exception as e:
            print(f"\nОшибка: {e}")


if __name__ == "__main__":
    main()
