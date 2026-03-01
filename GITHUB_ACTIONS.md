# GitHub Actions - Автоматическая сборка APK

## Что это?

GitHub Actions автоматически собирает APK при каждом коммите в репозиторий. Не нужно устанавливать WSL или Linux.

## Как работает?

1. Пушишь код в GitHub
2. GitHub Actions автоматически запускает сборку
3. Через 20-30 минут APK готов
4. Скачиваешь APK из раздела "Actions"

## Настройка (уже сделано)

В проекте созданы 2 workflow:

### 1. `.github/workflows/test.yml` - Тестирование
- Запускается при каждом push/PR
- Проверяет код на Windows, Linux, macOS
- Проверяет синтаксис Python
- Тестирует импорты модулей

### 2. `.github/workflows/android.yml` - Сборка APK
- Запускается при push в master/dev
- Собирает APK для Android
- Кеширует зависимости (ускоряет сборку)
- Загружает APK как артефакты
- При создании тега (v1.0, v1.1) создает Release

## Как использовать?

### Автоматическая сборка при коммите

```bash
# Просто пуш в master или dev
git add .
git commit -m "Update game"
git push origin master
```

### Ручной запуск сборки

1. Открой GitHub репозиторий
2. Перейди в "Actions"
3. Выбери "Build Android APK"
4. Нажми "Run workflow"
5. Выбери ветку (master/dev)
6. Нажми "Run workflow"

### Скачивание APK

1. Открой GitHub репозиторий
2. Перейди в "Actions"
3. Выбери последний успешный workflow (зеленая галочка)
4. Прокрути вниз до "Artifacts"
5. Скачай:
   - `enhancedpong-arm64-v8a-debug` - для современных устройств
   - `enhancedpong-armeabi-v7a-debug` - для старых устройств

### Создание Release с APK

```bash
# Создай тег версии
git tag v1.0
git push origin v1.0

# GitHub Actions автоматически:
# 1. Соберет APK
# 2. Создаст Release
# 3. Прикрепит APK к Release
```

## Преимущества

✅ Не нужно устанавливать WSL/Linux
✅ Не нужно устанавливать Android SDK/NDK
✅ Сборка на мощных серверах GitHub (быстрее)
✅ Автоматическое кеширование (последующие сборки быстрее)
✅ Сборка для нескольких архитектур одновременно
✅ Автоматические Release при создании тегов
✅ Бесплатно для публичных репозиториев

## Время сборки

- Первая сборка: ~30-40 минут (скачивает SDK/NDK)
- Последующие сборки: ~15-20 минут (использует кеш)

## Лимиты GitHub Actions

- Публичные репозитории: **Безлимитно**
- Приватные репозитории: 2000 минут/месяц (бесплатно)

## Просмотр логов сборки

1. Открой "Actions"
2. Выбери workflow
3. Нажми на job "build"
4. Смотри логи каждого шага

## Проблемы

### Сборка не запускается
- Проверь, что файлы в `.github/workflows/` закоммичены
- Проверь, что Actions включены в настройках репозитория

### Сборка падает с ошибкой
- Открой логи в Actions
- Проверь последний шаг с ошибкой
- Обычно проблема в buildozer.spec или зависимостях

### APK не появляется в Artifacts
- Проверь, что сборка завершилась успешно (зеленая галочка)
- Artifacts доступны только 90 дней

## Отключение автосборки

Если не нужна автосборка при каждом коммите:

```yaml
# В .github/workflows/android.yml измени:
on:
  workflow_dispatch:  # Только ручной запуск
```

## Кастомизация

### Изменить версию Python

```yaml
# В android.yml
python-version: '3.12'  # Вместо 3.11
```

### Собирать только для одной архитектуры

```yaml
# В buildozer.spec
android.archs = arm64-v8a  # Только 64-bit
```

### Добавить уведомления

```yaml
# В конец android.yml
- name: Notify on success
  if: success()
  run: echo "Build successful!"
```

## Полезные ссылки

- [GitHub Actions документация](https://docs.github.com/en/actions)
- [Buildozer документация](https://buildozer.readthedocs.io/)
- [Pygame для Android](https://pygame.org/wiki/Android)
