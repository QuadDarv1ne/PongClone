# Quick Start Guide

## Установка зависимостей

```bash
# Основные зависимости
pip install -r PyPong/requirements.txt

# Для разработки
pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit install
```

## Запуск игры

```bash
# Простой запуск
python PyPong/pong.py

# Или через модуль
python -c "from PyPong.pong import PongGame; PongGame().run()"
```

## Запуск тестов

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=PyPong --cov-report=html

# Открыть отчёт
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

## Проверка качества кода

```bash
# Форматирование
black PyPong/
isort PyPong/

# Линтинг
flake8 PyPong/

# Проверка типов
mypy PyPong/ --ignore-missing-imports

# Всё сразу (через pre-commit)
pre-commit run --all-files
```

## Конфигурация

Создайте `.env` файл (скопируйте из `.env.example`):

```bash
cp .env.example .env
```

Отредактируйте настройки:
```env
WINDOW_WIDTH=1920
WINDOW_HEIGHT=1080
FPS=60
LANGUAGE=ru
```

## Следующие шаги

1. Прочитайте [README.md](README.md)
2. Изучите [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
3. Посмотрите [CONTRIBUTING.md](CONTRIBUTING.md)
4. Попробуйте разные режимы игры
