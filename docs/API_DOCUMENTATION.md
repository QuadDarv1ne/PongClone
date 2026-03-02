# PyPong API Documentation

Полная документация API для разработчиков.

## Содержание

- [Core Modules](#core-modules)
- [Game Systems](#game-systems)
- [UI Components](#ui-components)
- [Mobile Support](#mobile-support)
- [Optimization](#optimization)

## Core Modules

### Config System

#### `PyPong.core.config_extended.Config`

Централизованная система конфигурации с поддержкой переменных окружения.

```python
from PyPong.core.config_extended import config

# Получить значение
width = config.window_width
fps = config.fps

# Установить значение
config.set('window_width', 1920)

# Сохранить конфигурацию
config.save()
```

**Приоритет настроек:**
1. Переменные окружения (.env)
2. Файл config.json
3. Значения по умолчанию

#### `PyPong.core.env_config.EnvConfig`

Загрузка настроек из переменных окружения.

```python
from PyPong.core.env_config import get_env_config

env = get_env_config()

# Получить значения с типизацией
width = env.get_int('WINDOW_WIDTH', 1024)
fullscreen = env.get_bool('FULLSCREEN', False)
volume = env.get_float('MUSIC_VOLUME', 0.5)
```

### Event Bus

#### `PyPong.core.event_bus.EventBus`

Система событий для слабосвязанной коммуникации.

```python
from PyPong.core.event_bus import get_event_bus, GameEvent

bus = get_event_bus()

# Подписаться на событие
def on_goal_scored(data):
    print(f"Goal scored by player {data['player']}")

bus.subscribe(GameEvent.GOAL_SCORED, on_goal_scored)

# Опубликовать событие
bus.publish(GameEvent.GOAL_SCORED, {'player': 1, 'score': 5})

# Отписаться
bus.unsubscribe(GameEvent.GOAL_SCORED, on_goal_scored)
```

**Доступные события:**
- `GAME_START`, `GAME_PAUSE`, `GAME_RESUME`, `GAME_OVER`
- `BALL_HIT_PADDLE`, `BALL_HIT_WALL`, `GOAL_SCORED`
- `POWERUP_SPAWNED`, `POWERUP_COLLECTED`
- `ACHIEVEMENT_UNLOCKED`

### Object Pooling

#### `PyPong.core.object_pool.ObjectPool`

Универсальный пул объектов для оптимизации производительности.

```python
from PyPong.core.object_pool import ObjectPool

# Создать пул
pool = ObjectPool(
    factory=lambda: Ball(),
    initial_size=10,
    max_size=50,
    reset_func=lambda ball: ball.reset()
)

# Получить объект
ball = pool.acquire()

# Использовать объект
ball.update()

# Вернуть в пул
pool.release(ball)

# Статистика
stats = pool.get_stats()
print(f"Reuse rate: {stats['reuse_rate']:.1f}%")
```

### Profiler

#### `PyPong.core.profiler.PerformanceProfiler`

Профилирование производительности.

```python
from PyPong.core.profiler import get_profiler, profile, timeit

profiler = get_profiler()
profiler.enable()

# Профилирование секции кода
with profiler.profile_section('render'):
    render_game()

# Получить статистику
stats = profiler.get_timing_stats('render')
print(f"Avg: {stats['avg']*1000:.2f}ms")

# Декораторы
@profile
def expensive_function():
    pass

@timeit
def timed_function():
    pass
```

## Game Systems

### Replay System

#### `PyPong.systems.replay_enhanced.EnhancedReplayManager`

Расширенная система реплеев с экспортом и шарингом.

```python
from PyPong.systems.replay_enhanced import EnhancedReplayManager

manager = EnhancedReplayManager()

# Экспорт в разные форматы
manager.export_replay('20240302_120000', format='json')
manager.export_replay('20240302_120000', format='csv')
manager.export_replay('20240302_120000', format='video', fps=60)

# Создать shareable package
share_code = manager.share_replay('20240302_120000')
print(f"Share code: {share_code}")

# Анализ реплея
stats = manager.analyze_replay('20240302_120000')
print(f"Average ball speed: {stats['ball_stats']['avg_speed']:.2f}")
```

### Leaderboard

#### `PyPong.systems.leaderboard_online.LeaderboardManager`

Система таблиц лидеров (локальная и онлайн).

```python
from PyPong.systems.leaderboard_online import get_leaderboard_manager

manager = get_leaderboard_manager(enable_online=False)

# Отправить результат
manager.submit_score(
    player_name='Player1',
    score=1000,
    wins=5,
    losses=2,
    highest_combo=10,
    playtime=3600
)

# Получить таблицу лидеров
entries = manager.get_leaderboard(mode='local', limit=10)
for entry in entries:
    print(f"{entry.rank}. {entry.player_name}: {entry.score}")

# Статистика игрока
stats = manager.get_player_stats('Player1')
print(f"Rank: {stats['rank']}, Win rate: {stats['win_rate']:.1f}%")
```

## UI Components

### Responsive UI

#### `PyPong.mobile.responsive_ui.ResponsiveLayout`

Адаптивная система разметки.

```python
from PyPong.mobile.responsive_ui import ResponsiveLayout, AdaptiveButton

layout = ResponsiveLayout(base_width=1024, base_height=720)
layout.update_screen_size(1920, 1080)

# Проверка устройства
if layout.is_mobile:
    print("Mobile device detected")

if layout.is_portrait:
    print("Portrait orientation")

# Масштабирование
scaled_size = layout.scale(100)
scaled_font = layout.scale_font_size(24)

# Безопасная область
safe_area = layout.get_safe_area(padding_percent=0.05)

# Адаптивная кнопка
button = AdaptiveButton(
    text='Play',
    x=100, y=100,
    width=200, height=50,
    callback=lambda: print('Clicked'),
    layout=layout
)
```

### Accessibility

#### `PyPong.ui.accessibility.AccessibilityManager`

Функции доступности.

```python
from PyPong.ui.accessibility import get_accessibility_manager, ColorBlindMode

manager = get_accessibility_manager()

# Режим для дальтоников
manager.set_color_blind_mode(ColorBlindMode.PROTANOPIA)

# Высокая контрастность
manager.enable_high_contrast()

# Крупный UI
manager.enable_large_ui()
scale = manager.get_ui_scale()  # 1.5

# Уменьшенная анимация
manager.enable_reduce_motion()
if manager.should_play_animation():
    play_animation()

# Получить цвет с учётом настроек
color = manager.get_color('player1')  # Адаптированный цвет
```

### Onboarding

#### `PyPong.ui.onboarding.OnboardingManager`

Интерактивная система обучения.

```python
from PyPong.ui.onboarding import get_onboarding_manager

manager = get_onboarding_manager()

# Запустить туториал
manager.start('basic')  # 'basic', 'advanced', 'mobile'

# Отслеживание действий
manager.track_action('paddle_moved')
manager.track_action('ball_hit')

# Обновление и отрисовка
manager.update()
manager.draw(surface)

# Обработка событий
manager.handle_event(event)
```

## Mobile Support

### Android Optimizations

#### `PyPong.mobile.android_optimizations.AndroidOptimizer`

Android-специфичные оптимизации.

```python
from PyPong.mobile.android_optimizations import get_android_optimizer

optimizer = get_android_optimizer()

# Установить профиль производительности
optimizer.set_performance_profile('balanced')  # 'low', 'balanced', 'high'

# Battery saver
optimizer.enable_battery_saver()

# Рекомендуемые настройки
settings = optimizer.get_recommended_settings()
print(f"Recommended profile: {settings['profile']}")
```

#### Haptic Feedback

```python
from PyPong.mobile.android_optimizations import get_haptic_feedback

haptic = get_haptic_feedback()

# Вибрация
haptic.vibrate(duration_ms=50)

# Включить/выключить
haptic.enable()
haptic.disable()
```

#### Wake Lock

```python
from PyPong.mobile.android_optimizations import get_wake_lock

wake_lock = get_wake_lock()

# Предотвратить засыпание экрана
wake_lock.acquire()

# Разрешить засыпание
wake_lock.release()
```

## Optimization

### Dirty Rect Rendering

```python
from PyPong.rendering.optimized_renderer import DirtyRectRenderer

renderer = DirtyRectRenderer(screen, game_surface, theme, settings)

# Отметить область как изменённую
renderer.mark_dirty(pygame.Rect(x, y, width, height))

# Обновить только изменённые области
renderer.update_display_optimized()

# Статистика памяти
memory = renderer.get_memory_usage()
print(f"Cache size: {memory['cache_size_bytes'] / 1024:.1f} KB")
```

### Optimized Effects

```python
from PyPong.ui.effects_optimized import OptimizedParticlePool

pool = OptimizedParticlePool(max_size=100)

# Создать частицы
pool.emit(x=100, y=100, color=(255, 0, 0), count=10)

# Обновить и отрисовать
pool.update()
pool.draw(surface)

# Статистика
stats = pool.get_stats()
print(f"Active particles: {stats['active']}")
print(f"Reuse rate: {stats['pool_stats']['reuse_rate']:.1f}%")
```

## Best Practices

### Performance

1. **Используйте object pooling** для часто создаваемых объектов
2. **Кэшируйте** статичные поверхности
3. **Профилируйте** перед оптимизацией
4. **Используйте dirty rect rendering** для статичных сцен

### Code Quality

1. **Type hints** для всех публичных функций
2. **Docstrings** в формате Google
3. **Логирование** вместо print
4. **Обработка ошибок** с try/except

### Testing

1. **Unit тесты** для каждого модуля
2. **Integration тесты** для игровых режимов
3. **Performance тесты** для критичных секций
4. **Покрытие** 80%+

## Examples

### Полный пример игрового цикла

```python
from PyPong.core.event_bus import get_event_bus, GameEvent
from PyPong.core.profiler import get_profiler
from PyPong.core.object_pool import get_pool_manager

# Инициализация
event_bus = get_event_bus()
profiler = get_profiler()
pool_manager = get_pool_manager()

# Создать пулы
ball_pool = pool_manager.create_pool('balls', lambda: Ball(), initial_size=5)

# Подписаться на события
def on_goal(data):
    print(f"Goal! Player {data['player']}")

event_bus.subscribe(GameEvent.GOAL_SCORED, on_goal)

# Игровой цикл
profiler.enable()
running = True

while running:
    with profiler.profile_section('frame'):
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Обновление
        with profiler.profile_section('update'):
            ball = ball_pool.acquire()
            ball.update()
            
            if ball.scored:
                event_bus.publish(GameEvent.GOAL_SCORED, {'player': 1})
                ball_pool.release(ball)
        
        # Отрисовка
        with profiler.profile_section('render'):
            screen.fill((0, 0, 0))
            ball.draw(screen)
            pygame.display.flip()

# Отчёт
profiler.print_timing_report()
pool_manager.print_stats()
```

## Troubleshooting

### Низкий FPS

1. Проверьте количество активных объектов
2. Включите профилирование
3. Уменьшите MAX_PARTICLES и MAX_TRAILS
4. Используйте dirty rect rendering

### Высокое использование памяти

1. Очистите кэши
2. Проверьте утечки памяти
3. Уменьшите размеры пулов
4. Используйте object pooling

### Проблемы на мобильных

1. Установите профиль 'low' или 'balanced'
2. Включите battery saver
3. Уменьшите разрешение
4. Отключите сложные эффекты

## Contributing

См. [CONTRIBUTING.md](CONTRIBUTING.md) для информации о вкладе в проект.

## License

MIT License - см. [LICENCE](../LICENCE)
