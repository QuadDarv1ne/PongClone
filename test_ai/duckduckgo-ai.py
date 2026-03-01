#!/usr/bin/env python3
"""
DuckDuckGo AI CLI - простой интерфейс для DuckDuckGo AI
"""
import sys
import json

try:
    from duckduckgo_search import DDGS
except ImportError:
    print("Установите: pip install duckduckgo-search")
    sys.exit(1)


def chat(prompt: str, model: str = "gpt-4o-mini") -> str:
    """Отправить запрос к AI"""
    with DDGS() as ddgs:
        response = ddgs.chat(prompt, model=model)
        return response


def main():
    """Основной цикл"""
    print("DuckDuckGo AI CLI (q - выход)")
    print("-" * 40)
    
    while True:
        try:
            user_input = input("\nВы: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ('q', 'quit', 'exit'):
                print("Выход...")
                break
            
            print("\nAI: ", end="", flush=True)
            response = chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\nПрервано")
            break
        except Exception as e:
            print(f"\nОшибка: {e}")


if __name__ == "__main__":
    main()
