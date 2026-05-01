#!/usr/bin/env python3
"""
Platform detection and compatibility test
Run this to check if the game will work on your platform
"""
import sys
import platform
import os

def test_platform():
    """Test platform detection and compatibility"""
    print("=" * 60)
    print("PyPong Platform Compatibility Test")
    print("=" * 60)
    
    # Basic platform info
    print(f"\nPython version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"System: {platform.system()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    
    # Check for mobile
    is_mobile = False
    mobile_type = "Desktop"
    
    system = platform.system().lower()
    
    if system == 'linux':
        # Check for Android
        try:
            with open('/proc/version', 'r') as f:
                if 'android' in f.read().lower():
                    is_mobile = True
                    mobile_type = "Android"
        except (IOError, OSError):
            pass
        
        if os.environ.get('ANDROID_ROOT') or os.environ.get('ANDROID_DATA'):
            is_mobile = True
            mobile_type = "Android"
    
    elif system == 'darwin':
        # Check for iOS
        machine = platform.machine().lower()
        if 'iphone' in machine or 'ipad' in machine:
            is_mobile = True
            mobile_type = "iOS"
    
    print(f"\nDevice Type: {mobile_type}")
    print(f"Is Mobile: {is_mobile}")
    
    # Check pygame
    print("\n" + "-" * 60)
    print("Checking dependencies...")
    print("-" * 60)
    
    try:
        import pygame
        print(f"✓ pygame version: {pygame.version.ver}")
        print(f"  SDL version: {'.'.join(map(str, pygame.get_sdl_version()))}")
        
        # Check for touch support
        pygame.init()
        has_touch = hasattr(pygame, 'FINGERDOWN')
        print(f"  Touch events support: {'✓' if has_touch else '✗'}")
        pygame.quit()
        
    except ImportError as e:
        print(f"✗ pygame not found: {e}")
        print("  Install: pip install pygame-ce")
        return False
    
    # Check other dependencies
    modules = {
        'typing': 'Built-in',
        'json': 'Built-in',
        'os': 'Built-in',
        'sys': 'Built-in',
    }
    
    for module, source in modules.items():
        try:
            __import__(module)
            print(f"✓ {module}: {source}")
        except ImportError:
            print(f"✗ {module}: Not found")
    
    # Display info
    print("\n" + "-" * 60)
    print("Display capabilities...")
    print("-" * 60)
    
    try:
        pygame.init()
        info = pygame.display.Info()
        print(f"Screen size: {info.current_w}x{info.current_h}")
        print(f"Hardware acceleration: {info.hw}")
        print(f"Window manager: {info.wm}")
        pygame.quit()
    except Exception as e:
        print(f"Could not get display info: {e}")
    
    # Recommendations
    print("\n" + "=" * 60)
    print("Recommendations:")
    print("=" * 60)
    
    if is_mobile:
        print("✓ Mobile device detected")
        print("  - Touch controls will be enabled automatically")
        print("  - Fullscreen mode recommended")
        print("  - Landscape orientation recommended")
    else:
        print("✓ Desktop device detected")
        print("  - Keyboard controls available")
        print("  - Gamepad support available")
        print("  - Window can be resized")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_platform()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
