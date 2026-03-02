# 🤖 Мануал по работе с AI CLI инструментами
## Для проекта PongClone на Windows

**Дата обновления:** Март 2026  
**Python версия:** 3.14  
**ОС:** Windows 11

---

## 📋 Содержание

1. [Установленные инструменты](#установленные-инструменты)
2. [Быстрый старт](#быстрый-старт)
3. [Gemini CLI](#gemini-cli)
4. [Kritrima AI CLI](#kritrima-ai-cli)
5. [OpenAI CLI](#openai-cli)
6. [LiteLLM (библиотека)](#litellm-библиотека)
7. [Примеры использования для PongClone](#примеры-использования-для-pongclone)
8. [Сравнение инструментов](#сравнение-инструментов)

---

## 🛠️ Установленные инструменты

| Инструмент | Команда | Статус | API ключ |
|------------|---------|--------|----------|
| **Gemini CLI** | `gemini` | ✅ Работает | Не требуется (бесплатно) |
| **Kritrima AI** | `kritrima-ai` | ✅ Работает | Требуется настройка |
| **OpenAI CLI** | `openai` | ✅ Работает | Требуется |
| **LiteLLM** | `python -c "import litellm"` | ✅ Библиотека | Требуется |

### ❌ Не работают на Python 3.14:
- `ai-shell-agent` — несовместимость transformers/torch
- `whisper` — PyTorch не поддерживает Python 3.14
- `nanobot-ai` — ошибка кодировки emoji

---

## 🚀 Быстрый старт

### 1. Проверка установки

Откройте PowerShell или CMD и выполните:

```bash
# Проверка Gemini CLI
gemini --version

# Проверка Kritrima AI
kritrima-ai --version

# Проверка OpenAI CLI
openai -V
```

### 2. Настройка API ключей

#### Для Gemini CLI (бесплатно):
```bash
# Ключ не требуется для базового использования
# Для повышенных лимитов получите ключ: https://aistudio.google.com/apikey
gemini config
```

#### Для Kritrima AI:
```bash
# Первичная настройка
kritrima-ai --setup

# Или вручную через .env файл
# Создайте файл .env в корне проекта:
echo OPENAI_API_KEY=sk-your-key > .env
echo ANTHROPIC_API_KEY=sk-ant-your-key >> .env
```

#### Для OpenAI CLI:
```bash
# Установка ключа
openai api key sk-your-key

# Или через переменную окружения
set OPENAI_API_KEY=sk-your-key
```

---

## 💎 Gemini CLI

**Самый простой и бесплатный инструмент для начала работы.**

### Основные команды

```bash
# Интерактивный режим (чат)
gemini

# Одноразовый запрос
gemini "напиши функцию для отскока мяча в Pong"

# С указанием модели
gemini -m gemini-2.0-flash "объясни код"

# Режим YOLO (автоподтверждение всех действий)
gemini --yolo "измени файл main.py"

# План-режим (только чтение, без изменений)
gemini --approval-mode plan "проанализируй архитектуру"

# С файлом в контексте
gemini -f PyPong/main.py "найди баги в этом файле"

# Непрерывный режим после выполнения
gemini -i "создай тест для entities.py"
```

### Примеры использования для PongClone

#### 🔧 Генерация кода:
```bash
gemini "создай класс Ball для игры Pong с методами:
- update() - обновление позиции
- draw(screen) - отрисовка на экране
- reset() - сброс в центр
используй pygame и Python"
```

#### 🐛 Поиск багов:
```bash
gemini -f PyPong/pong_enhanced.py "найди потенциальные баги и уязвимости"
```

#### 📝 Документация:
```bash
gemini -f PyPong/entities.py "напиши docstring для всех классов и методов"
```

#### 🎨 Рефакторинг:
```bash
gemini --approval-mode plan -f PyPong/main.py "предложи улучшения архитектуры кода"
```

#### 🧪 Тесты:
```bash
gemini -f PyPong/entities.py -f PyPong/game_state.py "напиши unittest тесты для этих классов"
```

### Конфигурация Gemini CLI

Файлы конфигурации находятся в:
- `%APPDATA%\gemini-cli\config.json` — глобальная конфигурация
- `.gemini-cli\config.json` в проекте — локальная конфигурация

Пример `.gemini-cli/config.json`:
```json
{
  "model": "gemini-2.0-flash",
  "approvalMode": "default",
  "includeDirectories": ["PyPong"],
  "extensions": []
}
```

---

## 🧠 Kritrima AI CLI

**Мультипровайдер с поддержкой OpenAI, Anthropic и других.**

### Основные команды

```bash
# Первичная настройка
kritrima-ai --setup

# Запрос с моделью по умолчанию
kritrima-ai "объясни принцип работы campaign.py"

# С указанием модели и провайдера
kritrima-ai -m gpt-4 -p openai "оптимизируй алгоритм ИИ"

kritrima-ai -m claude-3-sonnet -p anthropic "улучши код"

# Режимы подтверждения
kritrima-ai -a suggest "измени файл"    # спрашивать каждое действие
kritrima-ai -a auto-edit "измени файл"  # авто-редактирование
kritrima-ai -a full-auto "измени файл"  # полная автоматизация

# Тест подключения
kritrima-ai --test-connection

# Список доступных моделей
kritrima-ai --list-models

# Показать конфигурацию
kritrima-ai config
```

### Примеры использования для PongClone

#### Анализ архитектуры:
```bash
kritrima-ai -f PyPong/ARCHITECTURE.md "проанализируй архитектуру и предложи улучшения"
```

#### Генерация контента:
```bash
kritrima-ai -m gpt-4 "создай 10 идей для новых модификаторов игры в PongClone"
```

#### Рефакторинг с Claude:
```bash
kritrima-ai -m claude-3-5-sonnet -p anthropic -f PyPong/enhanced_ai.py "рефактори код для лучшей читаемости"
```

#### Мультифайловый анализ:
```bash
kritrima-ai -f PyPong/entities.py -f PyPong/game_state.py -f PyPong/main.py "найди проблемы с совместимостью между модулями"
```

### Конфигурация Kritrima AI

Глобальная конфигурация: `%APPDATA%\kritrima-ai\config.json`

Пример конфигурации:
```json
{
  "default_model": "gpt-4",
  "default_provider": "openai",
  "approval_mode": "suggest",
  "providers": {
    "openai": {
      "api_key": "sk-...",
      "base_url": "https://api.openai.com/v1"
    },
    "anthropic": {
      "api_key": "sk-ant-..."
    }
  }
}
```

---

## 🔑 OpenAI CLI

**Официальный CLI от OpenAI для работы с API.**

### Основные команды

```bash
# Установка API ключа
openai api key sk-your-key

# Прямой вызов API
openai api chat.completions.create \
  -m gpt-4 \
  -g user "привет" \
  -g assistant "здравствуйте" \
  -g user "напиши функцию для Pong"

# Работа с файлами
openai api files.create -f PyPong/main.py -p fine-tune

# Fine-tuning моделей
openai api fine_tunes.create -t training.json -m davinci
```

### Пример использования:

```bash
# Создание completion через CLI
openai api chat.completions.create \
  -m gpt-3.5-turbo \
  -g system "Ты эксперт по Python и pygame" \
  -g user "Напиши класс PowerUp для игры Pong с методами:
    - apply(player) - применить эффект
    - expire(player) - снять эффект
    - draw(screen) - отрисовка"
```

---

## 📚 LiteLLM (библиотека)

**Универсальный прокси для 100+ LLM провайдеров.**

### Установка дополнительных зависимостей

```bash
pip install 'litellm[proxy]'
```

### Использование в Python-скриптах

Создайте файл `PyPong/ai_helper.py`:

```python
import litellm

# Настройка API ключей
litellm.openai_key = "sk-your-key"
litellm.anthropic_key = "sk-ant-your-key"

# Единый интерфейс для всех провайдеров
def ask_ai(prompt, model="gpt-3.5-turbo"):
    response = litellm.completion(
        model=model,
        messages=[{"content": prompt, "role": "user"}]
    )
    return response.choices[0].message.content

# Примеры использования:
# OpenAI
code = ask_ai("Напиши функцию отскока мяча", "gpt-4")

# Anthropic
code = ask_ai("Оптимизируй код", "anthropic/claude-3-sonnet")

# Google Gemini
code = ask_ai("Объясни код", "gemini/gemini-2.0-flash")

# Локальные модели (через Ollama)
code = ask_ai("Тест", "ollama/llama3")
```

### Запуск LiteLLM Proxy сервера

```bash
# Запуск локального прокси-сервера
litellm --model gpt-3.5-turbo

# Сервер будет доступен по адресу http://0.0.0.0:4000
# Используйте как совместимый с OpenAI API endpoint
```

---

## 🎮 Примеры использования для PongClone

### 1. Генерация нового функционала

```bash
# Создать новый класс для турнирной системы
gemini "создай класс TournamentManager для PyPong с методами:
- create_tournament(players)
- generate_bracket()
- update_score(match_id, winner)
- get_standings()
используй dataclasses для хранения данных"
```

### 2. Анализ и оптимизация

```bash
# Анализ производительности
kritrima-ai -a auto-edit -f PyPong/pong_enhanced.py "найди узкие места производительности и оптимизируй"

# Поиск дублирования кода
gemini -f PyPong/*.py "найди дублирующийся код и предложи рефакторинг"
```

### 3. Создание тестов

```bash
# Unit-тесты для игровой логики
gemini -f PyPong/entities.py -f PyPong/game_state.py "напиши pytest тесты покрывающие 80% кода"
```

### 4. Документация

```bash
# Генерация документации API
kritrima-ai -f PyPong/*.py "создай API документацию в формате Markdown"

# Комментарии для сложных функций
gemini -f PyPong/minigames.py "добавь подробные комментарии к каждой функции"
```

### 5. Локализация

```bash
# Перевод строк интерфейса
gemini -f PyPong/localization.py "добавь поддержку испанского языка (es) для всех строк"
```

### 6. Создание ассетов (описание для генерации)

```bash
# Описание спрайтов для генерации
kritrima-ai "создай подробное описание для генерации спрайтов:
- мяч с эффектом свечения
- ракетка в стиле Tron
- фон с неоновыми элементами"
```

### 7. Автоматизация через скрипт

Создайте `PyPong/ai_tools.py`:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI-инструменты для разработки PongClone
Использование: python ai_tools.py <команда> [файл]
"""

import sys
import subprocess

def run_gemini(prompt, files=None):
    """Выполнить запрос через Gemini CLI"""
    cmd = ["gemini"]
    if files:
        for f in files:
            cmd.extend(["-f", f])
    cmd.append(prompt)
    subprocess.run(cmd)

def main():
    if len(sys.argv) < 2:
        print("Использование: python ai_tools.py <команда> [файлы...]")
        print("Команды:")
        print("  test <file>     - создать тесты")
        print("  doc <file>      - создать документацию")
        print("  refactor <file> - предложить рефакторинг")
        print("  bugs <file>     - найти баги")
        return
    
    command = sys.argv[1]
    files = sys.argv[2:] if len(sys.argv) > 2 else []
    
    prompts = {
        "test": "напиши comprehensive pytest тесты для этого файла",
        "doc": "создай подробную документацию с примерами использования",
        "refactor": "предложи рефакторинг для улучшения читаемости и производительности",
        "bugs": "найди потенциальные баги и уязвимости"
    }
    
    if command in prompts:
        run_gemini(prompts[command], files if files else ["PyPong/main.py"])
    else:
        print(f"Неизвестная команда: {command}")

if __name__ == "__main__":
    main()
```

Использование:
```bash
cd PyPong
python ai_tools.py test entities.py
python ai_tools.py doc main.py
python ai_tools.py bugs pong_enhanced.py
```

---

## 📊 Сравнение инструментов

| Критерий | Gemini CLI | Kritrima AI | OpenAI CLI | LiteLLM |
|----------|------------|-------------|------------|---------|
| **Цена** | Бесплатно | Зависит от провайдера | Платно | Зависит от провайдера |
| **Настройка** | Не требуется | Требуется | Требуется | Требуется |
| **Модели** | Gemini | 10+ провайдеров | OpenAI | 100+ провайдеров |
| **Интерактивный режим** | ✅ | ❌ | ❌ | ❌ |
| **Работа с файлами** | ✅ | ✅ | ❌ | Через код |
| **Авто-редактирование** | ✅ | ✅ | ❌ | ❌ |
| **Python 3.14** | ✅ | ✅ | ✅ | ✅ |

---

## 🔧 Решение проблем

### Ошибка "command not found"

```bash
# Проверка PATH для Python скриптов
python -m site --user-base

# Добавление в PATH (PowerShell)
$env:Path += ";C:\Users\maksi\AppData\Local\Programs\Python\Python314\Scripts"
```

### Ошибка API ключа

```bash
# Проверка ключа
kritrima-ai --test-connection

# Сброс конфигурации
kritrima-ai --reset-config
```

### Проблемы с кодировкой (Windows)

```bash
# Установка UTF-8 для консоли
chcp 65001

# Или в PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### Ошибки совместимости Python 3.14

Некоторые пакеты не работают с Python 3.14:
- ❌ PyTorch (и зависимости: transformers, whisper)
- ❌ ai-shell-agent
- ❌ nanobot-ai (ошибка emoji)

**Решение:** Используйте Gemini CLI или Kritrima AI для задач генерации кода.

---

## 📝 Шпаргалка команд

### Gemini CLI
```bash
gemini "запрос"                    # Быстрый запрос
gemini                             # Интерактивный режим
gemini -f file.py "запрос"         # С файлом
gemini --yolo "запрос"             # Без подтверждений
gemini -m model "запрос"           # С моделью
```

### Kritrima AI
```bash
kritrima-ai --setup                # Настройка
kritrima-ai "запрос"               # Запрос
kritrima-ai -m gpt-4 "запрос"      # С моделью
kritrima-ai -a auto-edit "запрос"  # Авто-редактирование
kritrima-ai --test-connection      # Тест API
```

### OpenAI CLI
```bash
openai api key sk-...              # Установка ключа
openai api chat.completions.create # Вызов API
```

### LiteLLM (Python)
```python
import litellm
response = litellm.completion(model="gpt-4", messages=[...])
```

---

## 🔗 Полезные ссылки

- [Gemini CLI Документация](https://geminicli.com/docs/)
- [Kritrima AI GitHub](https://github.com/kritrima-ai/cli)
- [OpenAI API Документация](https://platform.openai.com/docs/)
- [LiteLLM Документация](https://docs.litellm.ai/)
- [Python 3.14 Совместимость](https://devguide.python.org/versions/)

---

**Автор:** AI Assistant  
**Для проекта:** PongClone  
**GitHub:** https://github.com/QuadDarv1ne/PongClone
