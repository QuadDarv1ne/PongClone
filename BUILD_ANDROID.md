# Сборка APK для Android

## Требования

- Linux или WSL (Windows Subsystem for Linux)
- Python 3.8+
- Java JDK 8 или 11
- Android SDK и NDK

## Установка Buildozer

```bash
# Установка зависимостей (Ubuntu/Debian)
sudo apt update
sudo apt install -y git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# Установка Buildozer
pip3 install --user buildozer
pip3 install --user cython
```

## Сборка APK

```bash
# Перейти в корень проекта
cd PongClone

# Первая сборка (долго, скачивает SDK/NDK)
buildozer android debug

# Последующие сборки
buildozer android debug

# Сборка release версии (для публикации)
buildozer android release
```

## Результат

APK файл будет в папке `bin/`:
- `enhancedpong-1.0-arm64-v8a-debug.apk` - для установки на устройство
- `enhancedpong-1.0-armeabi-v7a-debug.apk` - для старых устройств

## Установка на устройство

```bash
# Через ADB
adb install bin/enhancedpong-1.0-arm64-v8a-debug.apk

# Или скопировать APK на устройство и установить вручную
```

## Проблемы

### Ошибка "Command failed"
- Проверьте наличие Java JDK: `java -version`
- Установите правильную версию NDK в buildozer.spec

### Долгая первая сборка
- Нормально, скачивается ~2GB (SDK, NDK, зависимости)
- Последующие сборки быстрее

### Ошибки с правами
- Не запускайте buildozer от root
- Используйте `--user` при установке pip пакетов

## Альтернатива - Pygame-CE

Если buildozer не работает, используйте Pygame-CE:

```bash
pip install pygame-ce
# Pygame-CE имеет лучшую поддержку Android
```

## Тестирование

1. Включите "Отладка по USB" на Android устройстве
2. Подключите устройство к компьютеру
3. Установите APK через ADB
4. Запустите игру на устройстве
5. Включите "Touch Controls" в настройках игры
