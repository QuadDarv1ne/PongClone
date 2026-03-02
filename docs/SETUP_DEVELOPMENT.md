# Настройка окружения для разработки

Руководство по настройке окружения разработки для PyPong.

## Требования

- Python 3.10 или выше
- pip (менеджер пакетов Python)
- Git

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/QuadDarv1ne/PongClone.git
cd PongClone
```

### 2. Создание виртуального окружения (рекомендуется)

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

#### Основные зависимости
```bash
pip install -r PyPong/requirements.txt
```

Или вручную:
```bash
pip install pygame-ce>=2.4.0
```

#### Зависимости для разработки
```bash
pip install -r requirements-dev.txt
```

Или вручную:
```bash
pip install pytest>=7.0.0 pytest-cov>=4.0.0 pytest-mock>=3.10.0
pip install black>=23.0.0 isort>=5.12.0 flake8>=6.0.0 mypy>=1.0.0
pip install pre-commit>=3.0.0
```

### 4. Настройка pre-commit hooks

```bash
pre-commit install
```

Это автоматически запустит проверки кода перед каждым коммитом.

### 5. Создание .env файла

```bash
cp .env.example .env
```

Отредактируйте `.env` под ваши нужды:

```env
# Производительность
PERFORMANCE_PROFILE=medium
DEBUG=True
ENABLE_PROFILING=True

# Язык
LANGUAGE=ru

# Логирование
LOG_LEVEL=DEBUG
SHOW_FPS=True
```

## Проверка установки

### Запуск игры

```bash
python PyPong/pong.py
```

Или:
```bash
python -c "from PyPong.pong import PongGame; PongGame().run()"
```

### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием кода
pytest --cov=PyPong --cov-report=html

# Только быстрые тесты
pytest -m "not slow"

# Конкретный файл
pytest PyPong/tests/test_entities_extended.py -v
```

### Проверка стиля кода

```bash
# Форматирование
black PyPong/
isort PyPong/

# Линтинг
flake8 PyPong/

# Проверка типов
mypy PyPong/
```

## Структура проекта

```
PongClone/
├── PyPong/                 # Основной код игры
│   ├── core/              # Ядро (entities, config, pools)
│   ├── systems/           # Игровые системы (AI, audio, stats)
│   ├── ui/                # Пользовательский интерфейс
│   ├── game/              # Игровая логика
│   ├── content/           # Игровой контент
│   ├── rendering/         # Рендеринг
│   ├── mobile/            # Мобильная поддержка
│   ├── tests/             # Тесты
│   └── pong.py            # Главный файл игры
├── docs/                  # Документация
├── .env.example           # Пример конфигурации
├── requirements-dev.txt   # Зависимости для разработки
└── pyproject.toml         # Конфигурация проекта
```

## Разработка

### Создание новой функции

1. Создайте ветку:
```bash
git checkout -b feature/my-feature
```

2. Внесите изменения

3. Добавьте тесты:
```bash
# Создайте файл PyPong/tests/test_my_feature.py
```

4. Запустите тесты:
```bash
pytest PyPong/tests/test_my_feature.py -v
```

5. Проверьте стиль:
```bash
pre-commit run --all-files
```

6. Закоммитьте:
```bash
git add .
git commit -m "feat: add my feature"
```

7. Отправьте в репозиторий:
```bash
git push origin feature/my-feature
```

8. Создайте Pull Request на GitHub

### Отладка

#### Включить debug режим

В `.env`:
```env
DEBUG=True
LOG_LEVEL=DEBUG
SHOW_FPS=True
ENABLE_PROFILING=True
```

#### Просмотр логов

Логи сохраняются в `logs/pong_YYYYMMDD.log`

```bash
# Просмотр последних логов
tail -f logs/pong_$(date +%Y%m%d).log
```

#### Профилирование

```python
from PyPong.core.profiler import get_profiler

profiler = get_profiler()
profiler.enable()

# Ваш код
with profiler.profile_section('my_section'):
    # Код для профилирования
    pass

# В конце
profiler.print_timing_report()
```

#### Статистика пулов объектов

```python
from PyPong.core.entity_pools import print_all_pool_stats

# В конце игры
print_all_pool_stats()
```

## Решение проблем

### Проблема: pygame не установлен

```bash
pip install pygame-ce>=2.4.0
```

### Проблема: pytest не найден

```bash
pip install pytest pytest-cov
```

### Проблема: pre-commit не работает

```bash
pip install pre-commit
pre-commit install
```

### Проблема: Ошибка импорта модулей

Убедитесь, что вы запускаете из корня проекта:
```bash
cd /path/to/PongClone
python PyPong/pong.py
```

Или добавьте путь в PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/PongClone"
```

### Проблема: Низкий FPS

1. Снизьте профиль производительности в `.env`:
```env
PERFORMANCE_PROFILE=low
```

2. Отключите эффекты:
```env
ENABLE_EFFECTS=False
ENABLE_SCREEN_SHAKE=False
```

3. Уменьшите количество частиц:
```env
MAX_PARTICLES=20
MAX_TRAILS=10
```

## Полезные команды

### Запуск конкретных тестов

```bash
# Unit тесты
pytest -m unit

# Integration тесты
pytest -m integration

# Performance тесты
pytest -m performance

# Исключить медленные тесты
pytest -m "not slow"
```

### Генерация отчета о покрытии

```bash
pytest --cov=PyPong --cov-report=html
# Откройте htmlcov/index.html в браузере
```

### Форматирование всего кода

```bash
black PyPong/
isort PyPong/
```

### Проверка всего кода

```bash
flake8 PyPong/
mypy PyPong/
```

## Дополнительные ресурсы

- [Документация pygame-ce](https://pyga.me/docs/)
- [Документация pytest](https://docs.pytest.org/)
- [Руководство по вкладу](../CONTRIBUTING.md)
- [API документация](API_DOCUMENTATION.md)

## Поддержка

Если у вас возникли проблемы:

1. Проверьте [Issues](https://github.com/QuadDarv1ne/PongClone/issues)
2. Создайте новую Issue с описанием проблемы
3. Присоединяйтесь к [Discussions](https://github.com/QuadDarv1ne/PongClone/discussions)

---

**Happy coding!** 🚀
