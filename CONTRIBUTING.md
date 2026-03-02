# Contributing to PyPong

Спасибо за интерес к проекту! Мы рады любому вкладу.

## Как внести вклад

### 1. Сообщить о проблеме

Если вы нашли баг или хотите предложить улучшение:

1. Проверьте, нет ли уже похожей [issue](https://github.com/QuadDarv1ne/PongClone/issues)
2. Создайте новую issue с подробным описанием
3. Используйте шаблоны для bug reports и feature requests

### 2. Исправить баг или добавить функцию

1. **Fork** репозиторий
2. **Clone** ваш fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/PongClone.git
   cd PongClone
   ```

3. **Создайте ветку** для ваших изменений:
   ```bash
   git checkout -b feature/amazing-feature
   # или
   git checkout -b fix/bug-description
   ```

4. **Установите зависимости**:
   ```bash
   pip install -r requirements-dev.txt
   ```

5. **Настройте pre-commit hooks**:
   ```bash
   pre-commit install
   ```

6. **Внесите изменения** и убедитесь, что:
   - Код соответствует стилю проекта (black, isort, flake8)
   - Добавлены тесты для новой функциональности
   - Все тесты проходят
   - Документация обновлена

7. **Запустите тесты**:
   ```bash
   pytest
   pytest --cov=PyPong --cov-report=html
   ```

8. **Commit** изменения:
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

9. **Push** в ваш fork:
   ```bash
   git push origin feature/amazing-feature
   ```

10. **Создайте Pull Request** на GitHub

## Стандарты кода

### Стиль кода

Мы используем:
- **Black** для форматирования (line length: 120)
- **isort** для сортировки импортов
- **flake8** для линтинга
- **mypy** для проверки типов

Запустите перед commit:
```bash
black PyPong/
isort PyPong/
flake8 PyPong/
mypy PyPong/
```

Или используйте pre-commit hooks (автоматически):
```bash
pre-commit run --all-files
```

### Commit Messages

Используйте [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: Новая функция
- `fix`: Исправление бага
- `docs`: Изменения в документации
- `style`: Форматирование кода
- `refactor`: Рефакторинг
- `test`: Добавление тестов
- `chore`: Обновление зависимостей, конфигурации

**Примеры:**
```
feat(ui): add color blind mode support
fix(collision): correct ball-paddle collision detection
docs(api): update event bus documentation
test(replay): add tests for replay compression
```

### Type Hints

Используйте type hints для всех публичных функций:

```python
def calculate_score(player: int, combo: int) -> int:
    """Calculate score with combo multiplier."""
    return player * combo
```

### Docstrings

Используйте Google style docstrings:

```python
def process_data(data: List[int], threshold: int = 10) -> Dict[str, Any]:
    """Process data and return statistics.
    
    Args:
        data: List of integers to process
        threshold: Minimum value threshold
    
    Returns:
        Dictionary with statistics:
            - 'mean': Average value
            - 'max': Maximum value
            - 'count': Number of values above threshold
    
    Raises:
        ValueError: If data is empty
    
    Example:
        >>> process_data([1, 2, 3, 4, 5], threshold=3)
        {'mean': 3.0, 'max': 5, 'count': 2}
    """
    if not data:
        raise ValueError("Data cannot be empty")
    
    # Implementation
    pass
```

### Тестирование

#### Структура тестов

```
PyPong/tests/
├── test_core.py          # Core functionality
├── test_systems.py       # Game systems
├── test_ui.py            # UI components
├── test_integration.py   # Integration tests
└── conftest.py           # Fixtures
```

#### Написание тестов

```python
import pytest
from PyPong.core.event_bus import EventBus, GameEvent


class TestEventBus:
    """Test suite for EventBus"""
    
    def setup_method(self):
        """Setup for each test"""
        self.event_bus = EventBus()
    
    def test_subscribe_and_publish(self):
        """Test basic subscribe and publish"""
        callback_called = False
        
        def callback(data):
            nonlocal callback_called
            callback_called = True
        
        self.event_bus.subscribe(GameEvent.GOAL_SCORED, callback)
        self.event_bus.publish(GameEvent.GOAL_SCORED)
        
        assert callback_called
    
    @pytest.mark.slow
    def test_performance(self):
        """Test event bus performance"""
        # Performance test
        pass
```

#### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=PyPong --cov-report=html

# Только unit тесты
pytest -m unit

# Исключить медленные тесты
pytest -m "not slow"

# Конкретный файл
pytest PyPong/tests/test_event_bus.py

# Конкретный тест
pytest PyPong/tests/test_event_bus.py::TestEventBus::test_subscribe_and_publish
```

### Документация

#### Обновление документации

При добавлении новой функциональности:

1. Обновите `README.md` если нужно
2. Добавьте примеры в `docs/API_DOCUMENTATION.md`
3. Обновите docstrings в коде
4. Добавьте комментарии для сложной логики

#### Генерация документации

```bash
# Установите Sphinx
pip install sphinx sphinx-rtd-theme

# Генерация
cd docs
sphinx-quickstart
sphinx-apidoc -o source/ ../PyPong
make html
```

## Процесс Review

### Что проверяется

1. **Функциональность**: Работает ли код как ожидается?
2. **Тесты**: Есть ли тесты? Проходят ли они?
3. **Стиль**: Соответствует ли код стандартам?
4. **Документация**: Обновлена ли документация?
5. **Производительность**: Нет ли проблем с производительностью?
6. **Безопасность**: Нет ли уязвимостей?

### Checklist для PR

- [ ] Код соответствует стилю проекта
- [ ] Все тесты проходят
- [ ] Добавлены тесты для новой функциональности
- [ ] Документация обновлена
- [ ] Commit messages следуют конвенции
- [ ] Нет конфликтов с main веткой
- [ ] Pre-commit hooks проходят

## Архитектура проекта

### Структура

```
PyPong/
├── core/           # Ядро: конфигурация, события, пулы
├── systems/        # Игровые системы: AI, аудио, реплеи
├── ui/             # UI компоненты: меню, эффекты, темы
├── mobile/         # Мобильная поддержка
├── rendering/      # Рендеринг и оптимизация
├── game/           # Игровая логика
├── content/        # Игровой контент
└── tests/          # Тесты
```

### Принципы

1. **Модульность**: Каждый модуль независим
2. **Слабая связанность**: Используйте Event Bus
3. **Высокая связность**: Группируйте связанную функциональность
4. **DRY**: Не повторяйте код
5. **SOLID**: Следуйте принципам SOLID
6. **Performance**: Оптимизируйте критичные секции

### Паттерны

- **Singleton**: Для глобальных менеджеров
- **Object Pool**: Для часто создаваемых объектов
- **Observer**: Event Bus для событий
- **Strategy**: Для разных AI стратегий
- **Factory**: Для создания игровых объектов

## Вопросы?

- Создайте [issue](https://github.com/QuadDarv1ne/PongClone/issues)
- Напишите в [discussions](https://github.com/QuadDarv1ne/PongClone/discussions)
- Свяжитесь с мейнтейнерами

## Лицензия

Внося вклад, вы соглашаетесь, что ваш код будет лицензирован под MIT License.

## Благодарности

Спасибо всем контрибьюторам! 🎉

---

**Happy coding!** 🚀
