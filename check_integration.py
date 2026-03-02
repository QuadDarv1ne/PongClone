#!/usr/bin/env python3
"""
Проверка интеграции новых модулей
"""
import sys
from pathlib import Path

# Добавить PyPong в путь
sys.path.insert(0, str(Path(__file__).parent))

def check_imports():
    """Проверить импорты"""
    print("Проверка импортов...")
    
    try:
        from PyPong.core.config_extended import config
        print("✓ config_extended")
    except ImportError as e:
        print(f"✗ config_extended: {e}")
        return False
    
    try:
        from PyPong.core.event_bus import get_event_bus, GameEvent
        print("✓ event_bus")
    except ImportError as e:
        print(f"✗ event_bus: {e}")
        return False
    
    try:
        from PyPong.core.object_pool import ObjectPool
        print("✓ object_pool")
    except ImportError as e:
        print(f"✗ object_pool: {e}")
        return False
    
    try:
        from PyPong.core.profiler import get_profiler
        print("✓ profiler")
    except ImportError as e:
        print(f"✗ profiler: {e}")
        return False
    
    try:
        from PyPong.ui.effects_optimized import OptimizedParticlePool
        print("✓ effects_optimized")
    except ImportError as e:
        print(f"✗ effects_optimized: {e}")
        return False
    
    try:
        from PyPong.ui.accessibility import get_accessibility_manager
        print("✓ accessibility")
    except ImportError as e:
        print(f"✗ accessibility: {e}")
        return False
    
    try:
        from PyPong.mobile.responsive_ui import ResponsiveLayout
        print("✓ responsive_ui")
    except ImportError as e:
        print(f"✗ responsive_ui: {e}")
        return False
    
    return True

def check_functionality():
    """Проверить базовую функциональность"""
    print("\nПроверка функциональности...")
    
    # Event Bus
    from PyPong.core.event_bus import get_event_bus, GameEvent
    bus = get_event_bus()
    
    called = []
    def callback(data):
        called.append(data)
    
    bus.subscribe(GameEvent.GOAL_SCORED, callback)
    bus.publish(GameEvent.GOAL_SCORED, {'player': 1})
    
    if called and called[0] == {'player': 1}:
        print("✓ Event Bus работает")
    else:
        print("✗ Event Bus не работает")
        return False
    
    # Object Pool
    from PyPong.core.object_pool import ObjectPool
    
    class TestObj:
        def __init__(self):
            self.value = 0
    
    pool = ObjectPool(lambda: TestObj(), initial_size=5)
    obj = pool.acquire()
    
    if obj and isinstance(obj, TestObj):
        print("✓ Object Pool работает")
        pool.release(obj)
    else:
        print("✗ Object Pool не работает")
        return False
    
    # Profiler
    from PyPong.core.profiler import get_profiler
    profiler = get_profiler()
    profiler.enable()
    
    with profiler.profile_section('test'):
        sum(range(1000))
    
    stats = profiler.get_timing_stats('test')
    if stats and 'avg' in stats:
        print("✓ Profiler работает")
    else:
        print("✗ Profiler не работает")
        return False
    
    return True

def main():
    """Главная функция"""
    print("=" * 50)
    print("Проверка интеграции новых модулей")
    print("=" * 50)
    
    if not check_imports():
        print("\n❌ Проверка импортов провалена")
        return 1
    
    if not check_functionality():
        print("\n❌ Проверка функциональности провалена")
        return 1
    
    print("\n" + "=" * 50)
    print("✅ Все проверки пройдены успешно!")
    print("=" * 50)
    return 0

if __name__ == "__main__":
    sys.exit(main())
