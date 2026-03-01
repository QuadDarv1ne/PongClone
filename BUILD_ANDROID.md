# Сборка APK для Android

## Требования

**ВАЖНО:** Buildozer работает только на Linux. На Windows используй WSL 2.

### Для Windows (WSL 2)

1. **Установка WSL 2:**

```powershell
# В PowerShell от администратора
wsl --install

# Или обновление до WSL 2
wsl --set-default-version 2
wsl --install -d Ubuntu-22.04

# Перезагрузи компьютер
```

2. **Проверка версии WSL:**

```powershell
wsl --version
# Должно показать WSL версии 2.x.x
```

3. **Запуск Ubuntu:**
- Открой "Ubuntu" из меню Пуск
- Создай пользователя при первом запуске

### Для Linux

- Ubuntu 20.04+ или Debian 11+
- Python 3.8+
- Java JDK 11 или 17
- Android SDK и NDK (скачаются автоматически)

## Установка зависимостей (в WSL/Linux)

```bash
# Обновление системы
sudo apt update
sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y \
    git zip unzip openjdk-17-jdk \
    python3-pip autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo5 cmake libffi-dev libssl-dev \
    build-essential ccache libsqlite3-dev \
    libffi-dev libssl-dev python3-dev

# Установка Buildozer и Cython
pip3 install --user --upgrade buildozer cython

# Добавление в PATH (добавь в ~/.bashrc)
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

## Копирование проекта в WSL (только для Windows)

```bash
# В WSL терминале
cd ~

# Копирование из Windows в WSL
cp -r /mnt/c/Users/maksi/OneDrive/Documents/GitHub/PongClone .

# Переход в проект
cd PongClone
```

## Сборка APK

```bash
# Первая сборка (долго, ~30-60 минут, скачивает SDK/NDK)
buildozer android debug

# Последующие сборки (быстрее, ~5-10 минут)
buildozer android debug

# Сборка release версии (для публикации в Google Play)
buildozer android release
```

## Результат

APK файл будет в папке `bin/`:
- `enhancedpong-1.0-arm64-v8a-debug.apk` - для современных устройств (64-bit)
- `enhancedpong-1.0-armeabi-v7a-debug.apk` - для старых устройств (32-bit)

## Установка на устройство

### Через ADB (Android Debug Bridge)

```bash
# Установка ADB в WSL/Linux
sudo apt install adb

# Включи "Отладка по USB" на Android устройстве
# Подключи устройство к компьютеру

# Проверка подключения
adb devices

# Установка APK
adb install bin/enhancedpong-1.0-arm64-v8a-debug.apk
```

### Вручную

1. Скопируй APK из WSL в Windows:
```bash
# В WSL
cp bin/*.apk /mnt/c/Users/maksi/Downloads/
```

2. Перенеси APK на Android устройство
3. Открой файл на устройстве и установи

## Проблемы и решения

### Ошибка "FancyURLopener" на Windows
- Buildozer не работает на Windows напрямую
- Используй WSL 2 (инструкция выше)

### Ошибка "Command failed" или "Java not found"
```bash
# Проверь Java
java -version

# Если не установлена
sudo apt install openjdk-17-jdk
```

### Долгая первая сборка
- Нормально, скачивается ~2-3GB (SDK, NDK, зависимости)
- Последующие сборки намного быстрее
- Используй `ccache` для ускорения

### Ошибки с правами
```bash
# Не запускай buildozer от root
# Используй --user при установке pip пакетов
pip3 install --user buildozer
```

### Недостаточно места в WSL
```bash
# Проверка места
df -h

# Очистка кеша buildozer
rm -rf .buildozer
```

## Оптимизация сборки

```bash
# Использование ccache для ускорения
export USE_CCACHE=1
export NDK_CCACHE=ccache

# Сборка только для одной архитектуры (быстрее)
# Отредактируй buildozer.spec:
# android.archs = arm64-v8a
```

## Тестирование

1. Включи "Отладка по USB" на Android устройстве
2. Подключи устройство к компьютеру
3. Установи APK через ADB или вручную
4. Запусти игру на устройстве
5. Touch-управление включится автоматически

## GitHub Actions (автоматическая сборка)

Для автоматической сборки APK при каждом коммите используй GitHub Actions.
Создай файл `.github/workflows/android.yml` (спроси, если нужно).

## Полезные команды

```bash
# Очистка сборки
buildozer android clean

# Просмотр логов
buildozer android debug | tee build.log

# Обновление buildozer
pip3 install --user --upgrade buildozer

# Проверка версии
buildozer --version
```
