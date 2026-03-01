PongClone
=========

[![DOI](https://zenodo.org/badge/592707498.svg)](https://doi.org/10.5281/zenodo.17264332)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0007--7605--539X-green?logo=orcid&logoColor=white)](https://orcid.org/0009-0007-7605-539X)
[![Tests](https://img.shields.io/badge/tests-13%2F13%20passed-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.10+-blue)]()
[![Pygame](https://img.shields.io/badge/pygame--ce-2.4.0+-green)]()

![image](https://github.com/user-attachments/assets/d5811b5e-5f69-4ef3-a8bd-6deb3c9b703b)
![image](https://github.com/user-attachments/assets/19a99456-3950-4b1e-a7ff-e1cfd1d320bc)

**Pong Clone** — это современная версия классической аркадной игры Pong (Atari, 1972) на Python с pygame-ce.

## 🎯 Быстрый старт

### Установка

```bash
# Клонируйте репозиторий
git clone https://github.com/QuadDarv1ne/PongClone.git
cd PongClone

# Установите зависимости
pip install pygame-ce>=2.4.0
```

### Запуск игры

```bash
# Из корня проекта
python -c "from PyPong.pong_v4 import PongGame; PongGame().run()"

# Или из папки PyPong
cd PyPong
python pong_v4.py
```

### Тестирование

```bash
# Запуск всех тестов
cd PyPong
python tests/test_all_features.py
```

## 🎮 Управление

### Игрок 1 (левая ракетка)
| Клавиша | Действие |
|---------|----------|
| `W` | Вверх |
| `S` | Вниз |

### Игрок 2 (правая ракетка, если 2 игрока)
| Клавиша | Действие |
|---------|----------|
| `↑` | Вверх |
| `↓` | Вниз |

### Общее
| Клавиша | Действие |
|---------|----------|
| `Enter` | Старт / Подтвердить |
| `Escape` | Пауза / Назад |
| `S` | Статистика (в меню) |
| `O` | Настройки (в меню) |
| `1/2/3` | Выбор сложности |

### Геймпад
- Поддерживается через `PyPong.gamepad`
- Автоматическое определение при подключении

## 📦 Структура проекта

```
PongClone/
├── PyPong/
│   ├── core/               # Ядро игры
│   │   ├── config.py       # Конфигурация и константы
│   │   ├── entities.py     # Игровые объекты (Paddle, Ball, PowerUp)
│   │   ├── game_state.py   # Управление состояниями
│   │   ├── constants.py    # Enum константы
│   │   └── logger.py       # Система логирования
│   │
│   ├── systems/            # Игровые системы
│   │   ├── audio.py        # Аудио менеджер
│   │   ├── stats.py        # Статистика игр
│   │   ├── settings.py     # Настройки игры
│   │   ├── achievements.py # Достижения (21 шт)
│   │   ├── arenas.py       # Арены с препятствиями (5 типов)
│   │   ├── enhanced_ai.py  # AI с предсказанием траектории
│   │   ├── enhanced_powerups.py # Power-up'ы (10 типов)
│   │   └── replay_system.py # Запись и воспроизведение
│   │
│   ├── ui/                 # Пользовательский интерфейс
│   │   ├── ui.py           # Базовые UI элементы
│   │   ├── enhanced_ui.py  # Продвинутые компоненты
│   │   ├── effects.py      # Визуальные эффекты
│   │   ├── themes.py       # Темы оформления
│   │   ├── sound_themes.py # Звуковые темы (4 шт)
│   │   ├── localization.py # Локализация (7 языков)
│   │   ├── customization.py # Кастомизация (скины, темы)
│   │   └── tutorial.py     # Интерактивное обучение
│   │
│   ├── content/            # Игровой контент
│   │   ├── campaign.py     # Кампания (10 уровней)
│   │   ├── challenges.py   # Ежедневные/еженедельные челленджи
│   │   ├── minigames.py    # Мини-игры (5 вариаций)
│   │   ├── modifiers.py    # Модификаторы физики (10 типов)
│   │   └── tournament.py   # Турнирный режим
│   │
│   ├── data/               # Сохранения (генерируется)
│   ├── locales/            # Локализация (en.json, ru.json)
│   ├── assets/             # Ресурсы (спрайты, звуки)
│   ├── tests/              # Тесты
│   │
│   ├── pong.py             # Базовая версия (2 игрока)
│   ├── pong_v2.py          # AI + power-ups
│   ├── pong_v3.py          # Сложность + очки
│   ├── pong_v4.py          # Полная версия ⭐
│   ├── main.py             # Android entry point
│   └── requirements.txt    # Зависимости
│
├── buildozer.spec          # Android сборка
├── BUILD_ANDROID.md        # Инструкция по сборке APK
├── BUILD_DESKTOP.md        # Инструкция для Desktop
└── README.md               # Этот файл
```

## 🎮 Режимы игры

| Режим | Описание |
|-------|----------|
| **Одиночная** | Игра против AI с выбором сложности |
| **2 игрока** | Локальный мультиплеер |
| **Кампания** | 10 уникальных уровней с боссами |
| **Челленджи** | Ежедневные и еженедельные задания |
| **Мини-игры** | 5 вариаций Pong |
| **Турнир** | Соревнование на выбывание |

## 🎯 Функции

### 🏗️ Архитектура
- ✅ Type hints — полная типизация кода
- ✅ Логирование — централизованная система
- ✅ Обработка ошибок — graceful error handling
- ✅ Enum константы — type-safe константы
- ✅ Модульная архитектура

### 📦 Контент
- ✅ **Кампания** — 10 уровней с уникальными механиками
- ✅ **Челленджи** — ежедневные/еженедельные задания
- ✅ **Модификаторы** — гравитация, ветер, замедление и др.
- ✅ **Мини-игры** — Target Practice, Survival, Time Attack и др.

### 🎯 Геймплей
- ✅ **Достижения** — 21 ачивка с наградами
- ✅ **Power-up'ы** — 10 типов (speed, shield, multi-ball...)
- ✅ **Арены** — 5 типов с препятствиями
- ✅ **Replay** — запись и воспроизведение матчей
- ✅ **AI** — предсказание траектории мяча
- ✅ **Комбо** — бонусы за серию успешных ударов

### 🎨 UI/UX
- ✅ **Анимации** — плавные переходы UI
- ✅ **Particle effects** — частицы при ударах и голах
- ✅ **Звуковые темы** — Classic, Retro, Futuristic, Minimal
- ✅ **Кастомизация** — 11 скинов ракеток, 7 мячей, 4 темы корта
- ✅ **Туториал** — интерактивное обучение
- ✅ **Локализация** — 🇬🇧 🇷🇺 🇪🇸 🇩🇪 🇫🇷 🇨🇳 🇯🇵

## 📊 Статистика проекта

| Метрика | Значение |
|---------|----------|
| **Версия** | 2.0 |
| **Модулей** | 18+ |
| **Строк кода** | ~4000 |
| **Классов** | 50+ |
| **Функций** | 200+ |
| **Тестов** | 13/13 ✅ |
| **Языков** | 7 |
| **Достижений** | 21 |
| **Power-up'ов** | 10 |
| **Арен** | 5 |
| **Уровней кампании** | 10 |
| **Мини-игр** | 5 |

## 🖥️ Платформы

| Платформа | Статус | Инструкция |
|-----------|--------|------------|
| **Windows** | ✅ Готово | `python pong_v4.py` |
| **Linux** | ✅ Готово | `python pong_v4.py` |
| **macOS** | ✅ Готово | `python pong_v4.py` |
| **Android** | 🟡 Требуется сборка | [BUILD_ANDROID.md](BUILD_ANDROID.md) |

## 🛠️ Разработка

### Требования
- Python 3.10+
- pygame-ce 2.4.0+

### Запуск тестов
```bash
cd PyPong
python tests/test_all_features.py
```

### Добавление локализации
1. Откройте `PyPong/locales/en.json` или `ru.json`
2. Добавьте перевод в формате `"ключ": "значение"`
3. Используйте в коде: `from PyPong.ui.localization import t; t("ключ")`

### Сборка для Android
См. [BUILD_ANDROID.md](BUILD_ANDROID.md)

## 📖 Документация

| Файл | Описание |
|------|----------|
| [NOTES.md](PyPong/NOTES.md) | Заметки разработчика, архитектура |
| [BUILD_ANDROID.md](BUILD_ANDROID.md) | Сборка APK для Android |
| [BUILD_DESKTOP.md](BUILD_DESKTOP.md) | Сборка для Desktop |
| [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md) | CI/CD настройка |
| [AI_CLI_MANUAL.md](AI_CLI_MANUAL.md) | AI CLI руководство |

## 🤝 Вклад

1. Fork репозиторий
2. Создайте ветку (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

См. файл [LICENCE](LICENCE)

## 👨‍🏫 Авторы

**Преподаватель:** Dupley Maxim Igorevich

**Разработчик:** QuadDarv1ne

**Дата создания:** 18/07/2024

**Последнее обновление:** 01/03/2026

## 🙏 Благодарности

- [pygame-ce](https://github.com/pygame-community/pygame-ce) — игровой движок
- [Atari](https://www.atari.com/) — создатели оригинального Pong (1972)

---

[![Star History Chart](https://api.star-history.com/svg?repos=QuadDarv1ne/PongClone&type=Date)](https://star-history.com/#QuadDarv1ne/PongClone&Date)
