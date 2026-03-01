# Сборка для Desktop (Windows, Linux, macOS)

## Автоматическая сборка через GitHub Actions

**Самый простой способ** - использовать GitHub Actions. Сборка происходит автоматически.

### Как получить готовые файлы:

1. Открой GitHub репозиторий
2. Перейди в "Actions"
3. Выбери "Build Desktop Releases"
4. Скачай нужную версию из "Artifacts":
   - **EnhancedPong-Windows** - EXE для Windows
   - **EnhancedPong-Linux** - Binary для Linux
   - **EnhancedPong-macOS** - DMG для macOS

### Создание Release:

```bash
git tag v1.0
git push origin v1.0
```

GitHub автоматически создаст Release со всеми файлами.

---

## Ручная сборка (если нужно)

### Windows

```bash
# Установка зависимостей
pip install pygame-ce pyinstaller

# Сборка EXE
cd PyPong
pyinstaller --onefile --windowed --name EnhancedPong pong_v4.py

# Результат в PyPong/dist/EnhancedPong.exe
```

### Linux

```bash
# Установка зависимостей
sudo apt-get install libsdl2-dev libsdl2-mixer-dev
pip install pygame-ce pyinstaller

# Сборка
cd PyPong
pyinstaller --onefile --name EnhancedPong pong_v4.py

# Результат в PyPong/dist/EnhancedPong
```

### macOS

```bash
# Установка зависимостей
pip install pygame-ce pyinstaller

# Сборка
cd PyPong
pyinstaller --onefile --windowed --name EnhancedPong pong_v4.py

# Результат в PyPong/dist/EnhancedPong.app
```

---

## Использование spec файла

Для более тонкой настройки используй `pong.spec`:

```bash
cd PyPong
pyinstaller pong.spec
```

---

## Размер файлов

- Windows EXE: ~30-40 MB
- Linux Binary: ~35-45 MB
- macOS App: ~40-50 MB

---

## Проблемы

### "Failed to execute script"
- Убедись, что все аудио файлы включены
- Проверь пути в spec файле

### Антивирус блокирует EXE
- Нормально для PyInstaller
- Добавь в исключения или используй официальный Release

### Большой размер файла
- Используй `--onefile` для одного файла
- Или `--onedir` для папки с файлами (меньше размер)

---

## Оптимизация

### Уменьшение размера:

```bash
# Используй UPX компрессию
pyinstaller --onefile --upx-dir=/path/to/upx pong_v4.py

# Исключи ненужные модули
pyinstaller --onefile --exclude-module tkinter pong_v4.py
```

### Ускорение запуска:

```bash
# Используй --onedir вместо --onefile
pyinstaller --onedir --windowed pong_v4.py
```

---

## Распространение

### Windows
- Просто отправь EXE файл
- Или создай installer с помощью Inno Setup

### Linux
- Создай .deb или .rpm пакет
- Или используй AppImage

### macOS
- Создай DMG образ
- Или опубликуй в Mac App Store
