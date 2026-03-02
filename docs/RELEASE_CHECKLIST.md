# Release Checklist

## Pre-Release

### Code Quality
- [ ] Все тесты проходят (`pytest`)
- [ ] Покрытие кода 80%+ (`pytest --cov`)
- [ ] Нет критических ошибок линтера (`flake8`)
- [ ] Код отформатирован (`black`, `isort`)
- [ ] Type hints проверены (`mypy`)
- [ ] Pre-commit hooks проходят

### Функциональность
- [ ] Все игровые режимы работают
- [ ] Меню навигация работает
- [ ] Настройки сохраняются
- [ ] Звук работает корректно
- [ ] Локализация работает
- [ ] Мобильные контролы работают (если применимо)

### Производительность
- [ ] 60 FPS на desktop
- [ ] 30 FPS на mobile
- [ ] Нет утечек памяти
- [ ] Загрузка < 5 секунд

### Документация
- [ ] README.md обновлён
- [ ] CHANGELOG.md обновлён
- [ ] API_DOCUMENTATION.md актуален
- [ ] Все примеры работают
- [ ] Скриншоты актуальны

### Безопасность
- [ ] Нет уязвимостей (`bandit`)
- [ ] Нет секретов в коде
- [ ] Зависимости обновлены
- [ ] Нет известных CVE

## Release Process

### 1. Версия
```bash
# Обновите версию в pyproject.toml
version = "2.1.0"

# Создайте git tag
git tag -a v2.1.0 -m "Release v2.1.0"
git push origin v2.1.0
```

### 2. Changelog
```bash
# Обновите CHANGELOG.md
# Переместите [Unreleased] в [2.1.0] - 2026-03-XX
```

### 3. Build
```bash
# Desktop
python -m PyInstaller PyPong/pong.spec

# Android
buildozer android debug
```

### 4. Test Build
- [ ] Запустите собранную версию
- [ ] Проверьте все функции
- [ ] Проверьте на чистой системе

### 5. GitHub Release
- [ ] Создайте release на GitHub
- [ ] Загрузите бинарники
- [ ] Добавьте release notes из CHANGELOG
- [ ] Добавьте скриншоты/видео

### 6. Distribution
- [ ] PyPI (если применимо)
- [ ] Google Play (Android)
- [ ] Itch.io
- [ ] Steam (если применимо)

## Post-Release

### Мониторинг
- [ ] Проверьте issue tracker
- [ ] Мониторьте crash reports
- [ ] Собирайте feedback
- [ ] Отвечайте на вопросы

### Маркетинг
- [ ] Пост в социальных сетях
- [ ] Статья на dev.to / habr.com
- [ ] Видео на YouTube
- [ ] Reddit post (r/pygame, r/gamedev)

### Метрики
- [ ] Количество скачиваний
- [ ] GitHub stars
- [ ] Отзывы пользователей
- [ ] Crash rate

## Hotfix Process

Если найден критический баг:

1. Создайте hotfix ветку
```bash
git checkout -b hotfix/critical-bug
```

2. Исправьте баг

3. Обновите версию (patch)
```bash
# 2.1.0 -> 2.1.1
```

4. Быстрый релиз
```bash
git tag -a v2.1.1 -m "Hotfix: critical bug"
git push origin v2.1.1
```

5. Merge в main и develop
```bash
git checkout main
git merge hotfix/critical-bug
git checkout develop
git merge hotfix/critical-bug
```

## Version Numbering

Используйте [Semantic Versioning](https://semver.org/):

- **MAJOR** (2.x.x): Breaking changes
- **MINOR** (x.1.x): New features (backward compatible)
- **PATCH** (x.x.1): Bug fixes

Примеры:
- `2.0.0` -> `2.1.0`: Добавлены новые функции
- `2.1.0` -> `2.1.1`: Исправлены баги
- `2.1.1` -> `3.0.0`: Breaking changes в API
