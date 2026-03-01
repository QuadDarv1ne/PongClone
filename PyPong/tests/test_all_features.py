"""
Comprehensive test suite for all features
"""
import sys
from pathlib import Path

# Add parent directory (PyPong's parent) to path for PyPong imports
current_dir = Path(__file__).parent.parent  # PyPong directory
parent_dir = current_dir.parent  # Parent of PyPong
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def test_logging():
    """Test logging system"""
    print("\n" + "="*60)
    print("Testing Logging System")
    print("="*60)

    try:
        from PyPong.core.logger import logger

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.log_event("test_event", {"key": "value"})

        print("✓ Logging system works")
        return True
    except Exception as e:
        print(f"✗ Logging test failed: {e}")
        return False


def test_constants():
    """Test constants and enums"""
    print("\n" + "="*60)
    print("Testing Constants and Enums")
    print("="*60)

    try:
        from PyPong.core.constants import (
            PowerUpType, Difficulty, GameMode,
            AchievementType, ArenaType, Colors
        )
        
        print(f"✓ PowerUpType: {len(PowerUpType)} types")
        print(f"✓ Difficulty: {len(Difficulty)} levels")
        print(f"✓ GameMode: {len(GameMode)} modes")
        print(f"✓ AchievementType: {len(AchievementType)} types")
        print(f"✓ ArenaType: {len(ArenaType)} types")
        print(f"✓ Colors defined")
        
        return True
    except Exception as e:
        print(f"✗ Constants test failed: {e}")
        return False


def test_achievements():
    """Test achievement system"""
    print("\n" + "="*60)
    print("Testing Achievement System")
    print("="*60)

    try:
        from PyPong.systems.achievements import AchievementManager
        from PyPong.core.constants import EventType

        mgr = AchievementManager()
        print(f"✓ {len(mgr.achievements)} achievements loaded")

        # Test unlock
        mgr.update_achievement('first_win')
        unlocked = mgr.get_unlocked_achievements()
        print(f"✓ {len(unlocked)} achievements unlocked")

        # Test event
        mgr.check_event(EventType.GAME_END, won=True, perfect=True)
        print("✓ Event checking works")

        return True
    except Exception as e:
        print(f"✗ Achievement test failed: {e}")
        return False


def test_enhanced_powerups():
    """Test enhanced power-ups"""
    print("\n" + "="*60)
    print("Testing Enhanced Power-ups")
    print("="*60)

    try:
        from PyPong.systems.enhanced_powerups import PowerUpRegistry, ComboSystem
        from PyPong.core.constants import PowerUpType
        
        # Test registry
        config = PowerUpRegistry.get_config(PowerUpType.SPEED_BOOST)
        print(f"✓ Power-up config: {config.name}")
        
        # Test combo
        combo = ComboSystem()
        count, mult = combo.register_hit()
        print(f"✓ Combo system: {count}x, {mult}x multiplier")
        
        return True
    except Exception as e:
        print(f"✗ Enhanced power-ups test failed: {e}")
        return False


def test_arenas():
    """Test arena system"""
    print("\n" + "="*60)
    print("Testing Arena System")
    print("="*60)

    try:
        from PyPong.systems.arenas import Arena, ArenaManager
        from PyPong.core.constants import ArenaType
        
        # Test arena creation
        arena = Arena(ArenaType.OBSTACLES)
        print(f"✓ Arena created: {arena.type.value}")
        print(f"✓ Obstacles: {len(arena.obstacles)}")
        
        # Test manager
        mgr = ArenaManager()
        print(f"✓ Unlocked arenas: {len(mgr.unlocked_arenas)}")
        
        return True
    except Exception as e:
        print(f"✗ Arena test failed: {e}")
        return False


def test_enhanced_ai():
    """Test enhanced AI"""
    print("\n" + "="*60)
    print("Testing Enhanced AI")
    print("="*60)

    try:
        from PyPong.systems.enhanced_ai import EnhancedAI, TrajectoryPredictor
        from PyPong.core.constants import Difficulty
        
        # Test predictor
        predictor = TrajectoryPredictor()
        impact = predictor.predict_impact_point((512, 360), (5, 3), 100)
        print(f"✓ Trajectory prediction: {impact}")
        
        # Test AI
        ai = EnhancedAI(Difficulty.HARD)
        print(f"✓ AI initialized: {ai.difficulty.value}")
        
        return True
    except Exception as e:
        print(f"✗ Enhanced AI test failed: {e}")
        return False


def test_replay_system():
    """Test replay system"""
    print("\n" + "="*60)
    print("Testing Replay System")
    print("="*60)

    try:
        from PyPong.systems.replay_system import ReplayManager
        
        mgr = ReplayManager()
        print("✓ Replay manager initialized")
        
        # Test recording
        mgr.recorder.start_recording()
        print("✓ Recording started")
        
        mgr.recorder.stop_recording(1, (5, 3))
        print("✓ Recording stopped")
        
        # Test replay list
        replays = mgr.list_replays()
        print(f"✓ Found {len(replays)} replays")
        
        return True
    except Exception as e:
        print(f"✗ Replay system test failed: {e}")
        return False


def test_sound_themes():
    """Test sound theme system"""
    print("\n" + "="*60)
    print("Testing Sound Theme System")
    print("="*60)

    try:
        from PyPong.ui.sound_themes import SoundThemeManager
        from PyPong.core.constants import SoundTheme
        
        mgr = SoundThemeManager()
        themes = mgr.get_available_themes()
        print(f"✓ {len(themes)} sound themes available")
        
        for theme_type, name in themes.items():
            print(f"  - {name}")
        
        return True
    except Exception as e:
        print(f"✗ Sound themes test failed: {e}")
        return False


def test_localization():
    """Test localization system"""
    print("\n" + "="*60)
    print("Testing Localization System")
    print("="*60)

    try:
        from PyPong.ui.localization import Localization, t

        loc = Localization()
        languages = loc.get_available_languages()
        print(f"✓ {len(languages)} languages supported")

        # Test translation
        text_en = loc.get("menu.title")
        print(f"✓ English: {text_en}")

        loc.set_language('ru')
        text_ru = loc.get("menu.title")
        # Encode/decode to handle Windows console encoding issues
        try:
            print(f"✓ Russian: {text_ru}")
        except UnicodeEncodeError:
            print(f"✓ Russian: {text_ru.encode('utf-8').decode('utf-8')}")

        return True
    except Exception as e:
        print(f"✗ Localization test failed: {e}")
        return False


def test_tutorial():
    """Test tutorial system"""
    print("\n" + "="*60)
    print("Testing Tutorial System")
    print("="*60)

    try:
        import pygame
        pygame.init()  # Initialize pygame for font

        from PyPong.ui.tutorial import TutorialManager
        
        mgr = TutorialManager()
        print(f"✓ {len(mgr.steps)} tutorial steps")
        
        mgr.start_tutorial()
        print("✓ Tutorial started")
        
        mgr.stop_tutorial()
        print("✓ Tutorial stopped")
        
        pygame.quit()
        return True
    except Exception as e:
        print(f"✗ Tutorial test failed: {e}")
        return False


def test_customization():
    """Test customization system"""
    print("\n" + "="*60)
    print("Testing Customization System")
    print("="*60)

    try:
        from PyPong.ui.customization import CustomizationManager
        
        mgr = CustomizationManager()
        print(f"✓ {len(mgr.paddle_skins)} paddle skins")
        print(f"✓ {len(mgr.ball_skins)} ball skins")
        print(f"✓ {len(mgr.court_themes)} court themes")
        
        # Test setting
        mgr.set_paddle_skin(1, "red")
        skin = mgr.get_paddle_skin(1)
        print(f"✓ Paddle skin set: {skin.name}")
        
        return True
    except Exception as e:
        print(f"✗ Customization test failed: {e}")
        return False


def test_enhanced_ui():
    """Test enhanced UI components"""
    print("\n" + "="*60)
    print("Testing Enhanced UI Components")
    print("="*60)

    try:
        import pygame
        pygame.init()  # Initialize pygame for font

        from PyPong.ui.enhanced_ui import (
            Animation, ComboDisplay, ProgressBar,
            NotificationManager
        )
        
        # Test animation
        anim = Animation(0, 1000, 0, 100, "ease_out")
        print("✓ Animation created")
        
        # Test combo display
        combo = ComboDisplay(512, 100)
        print("✓ Combo display created")
        
        # Test progress bar
        bar = ProgressBar(100, 100, 200, 20)
        print("✓ Progress bar created")
        
        # Test notification manager
        notif = NotificationManager()
        print("✓ Notification manager created")
        
        pygame.quit()
        return True
    except Exception as e:
        print(f"✗ Enhanced UI test failed: {e}")
        return False


def test_content_systems():
    """Test original content systems"""
    print("\n" + "="*60)
    print("Testing Content Systems (Campaign, Challenges, etc.)")
    print("="*60)

    try:
        from PyPong.content.campaign import CampaignManager
        from PyPong.content.challenges import ChallengeManager
        from PyPong.content.minigames import MiniGameManager
        from PyPong.content.modifiers import ModifierManager
        
        campaign = CampaignManager()
        print(f"✓ Campaign: {len(campaign.levels)} levels")
        
        challenges = ChallengeManager()
        print("✓ Challenges initialized")
        
        minigames = MiniGameManager()
        print(f"✓ Mini-games: {len(minigames.minigames)} games")
        
        modifiers = ModifierManager()
        print("✓ Modifiers initialized")
        
        return True
    except Exception as e:
        print(f"✗ Content systems test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("COMPREHENSIVE FEATURE TEST SUITE")
    print("="*60)
    
    tests = [
        ("Logging", test_logging),
        ("Constants", test_constants),
        ("Achievements", test_achievements),
        ("Enhanced Power-ups", test_enhanced_powerups),
        ("Arenas", test_arenas),
        ("Enhanced AI", test_enhanced_ai),
        ("Replay System", test_replay_system),
        ("Sound Themes", test_sound_themes),
        ("Localization", test_localization),
        ("Tutorial", test_tutorial),
        ("Customization", test_customization),
        ("Enhanced UI", test_enhanced_ui),
        ("Content Systems", test_content_systems),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
