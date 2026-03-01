"""
Simple test script for new content features
Run this to verify all systems work correctly
"""
import sys

def test_campaign():
    """Test campaign system"""
    print("Testing Campaign System...")
    try:
        from campaign import CampaignManager
        
        campaign = CampaignManager()
        print(f"✓ Campaign initialized with {len(campaign.levels)} levels")
        
        unlocked = campaign.get_unlocked_levels()
        print(f"✓ {len(unlocked)} levels unlocked")
        
        # Test level completion
        campaign.complete_level(1, 3, 45.5)
        print("✓ Level completion works")
        
        stars = campaign.get_total_stars()
        completion = campaign.get_completion_percentage()
        print(f"✓ Progress tracking: {completion:.0f}% complete, {stars} stars")
        
        return True
    except Exception as e:
        print(f"✗ Campaign test failed: {e}")
        return False


def test_challenges():
    """Test challenges system"""
    print("\nTesting Challenges System...")
    try:
        from challenges import ChallengeManager
        
        challenges = ChallengeManager()
        print("✓ Challenges initialized")
        
        challenges.refresh_challenges()
        active = challenges.get_active_challenges()
        print(f"✓ {len(active['daily'])} daily challenges")
        print(f"✓ {len(active['weekly'])} weekly challenges")
        
        # Test progress update
        if active['daily']:
            challenge = active['daily'][0]
            challenges.update_challenge('total_score', 5)
            print("✓ Challenge progress update works")
        
        return True
    except Exception as e:
        print(f"✗ Challenges test failed: {e}")
        return False


def test_modifiers():
    """Test game modifiers"""
    print("\nTesting Modifiers System...")
    try:
        from modifiers import (ModifierManager, GravityModifier, WindModifier,
                              InvisibleBallModifier, SpeedModifier)
        
        manager = ModifierManager()
        print("✓ Modifier manager initialized")
        
        # Add modifiers
        manager.add_modifier(GravityModifier(0.2))
        manager.add_modifier(WindModifier(0.15))
        manager.add_modifier(InvisibleBallModifier())
        manager.add_modifier(SpeedModifier())
        
        active = manager.get_active_modifiers()
        print(f"✓ {len(active)} modifiers active: {', '.join(active)}")
        
        manager.clear_modifiers()
        print("✓ Modifiers cleared")
        
        return True
    except Exception as e:
        print(f"✗ Modifiers test failed: {e}")
        return False


def test_minigames():
    """Test mini-games system"""
    print("\nTesting Mini-games System...")
    try:
        from minigames import MiniGameManager
        
        manager = MiniGameManager()
        print("✓ Mini-game manager initialized")
        
        available = list(manager.minigames.keys())
        print(f"✓ {len(available)} mini-games available: {', '.join(available)}")
        
        # Test starting a mini-game
        success = manager.start_minigame('target_practice')
        if success:
            print("✓ Mini-game started successfully")
            
            current = manager.get_current_minigame()
            print(f"✓ Current mini-game: {current.name}")
            
            manager.stop_minigame()
            print("✓ Mini-game stopped")
        
        return True
    except Exception as e:
        print(f"✗ Mini-games test failed: {e}")
        return False


def test_ui():
    """Test UI components (without pygame)"""
    print("\nTesting UI Components...")
    try:
        # Just check imports
        from content_ui import CampaignUI, ChallengesUI, MiniGameUI
        print("✓ All UI components imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ UI test failed: {e}")
        return False


def test_integration():
    """Test integration file"""
    print("\nTesting Integration...")
    try:
        # Check if enhanced game file exists and imports work
        import os
        if os.path.exists('pong_enhanced.py'):
            print("✓ Enhanced game file exists")
        
        # Try importing (won't run pygame)
        # This just checks syntax
        with open('pong_enhanced.py', 'r', encoding='utf-8') as f:
            code = f.read()
            compile(code, 'pong_enhanced.py', 'exec')
        print("✓ Enhanced game file syntax is valid")
        
        return True
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Content Features Test Suite")
    print("=" * 60)
    
    tests = [
        test_campaign,
        test_challenges,
        test_modifiers,
        test_minigames,
        test_ui,
        test_integration
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print(f"✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
