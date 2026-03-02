# PyPong Tests

Набор тестов для проекта PyPong.

## Запуск тестов

### Все тесты
```bash
pytest
```

### С покрытием кода
```bash
pytest --cov=PyPong --cov-report=html
```

### Только unit тесты
```bash
pytest -m unit
```

### Только integration тесты
```bash
pytest -m integration
```

### Исключить медленные тесты
```bash
pytest -m "not slow"
```

### Конкретный файл
```bash
pytest PyPong/tests/test_event_bus.py
```

### Конкретный тест
```bash
pytest PyPong/tests/test_event_bus.py::TestEventBus::test_subscribe_and_publish
```

## Структура тестов

- `test_all_features.py` - Интеграционные тесты всех функций
- `test_content.py` - Тесты игрового контента
- `test_entities.py` - Тесты игровых объектов
- `test_game_state.py` - Тесты состояний игры
- `test_integration.py` - Интеграционные тесты
- `test_event_bus.py` - Тесты системы событий
- `test_config.py` - Тесты конфигурации
- `test_env_config.py` - Тесты переменных окружения
- `test_profiler.py` - Тесты профайлера

## Маркеры

- `@pytest.mark.unit` - Unit тесты
- `@pytest.mark.integration` - Интеграционные тесты
- `@pytest.mark.slow` - Медленные тесты
- `@pytest.mark.performance` - Тесты производительности

## Покрытие кода

Цель: 80%+ покрытие кода

Текущее покрытие можно посмотреть после запуска:
```bash
pytest --cov=PyPong --cov-report=term-missing
```

HTML отчет:
```bash
pytest --cov=PyPong --cov-report=html
open htmlcov/index.html
```

## Fixtures

Общие fixtures находятся в `conftest.py`:
- `mock_pygame` - Мок pygame для тестирования без GUI
- `temp_config` - Временная конфигурация
- `event_bus` - Чистый event bus для каждого теста

## CI/CD

Тесты автоматически запускаются в GitHub Actions при каждом push и pull request.
См. `.github/workflows/test.yml`
