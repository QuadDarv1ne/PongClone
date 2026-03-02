"""
Android-specific optimizations and features
"""
import pygame
from typing import Optional, Dict, Any
from PyPong.core.logger import logger


class AndroidOptimizer:
    """
    Android-specific optimizations:
    - Battery saving mode
    - Performance profiles
    - Memory management
    - Touch optimization
    """
    
    def __init__(self):
        self.is_android = self._detect_android()
        self.battery_saver = False
        self.performance_profile = 'balanced'  # low, balanced, high
        
        if self.is_android:
            logger.info("Android platform detected, applying optimizations")
            self._apply_android_settings()
    
    def _detect_android(self) -> bool:
        """Detect if running on Android"""
        try:
            import platform
            import os
            
            # Check for Android in /proc/version
            try:
                with open('/proc/version', 'r') as f:
                    if 'android' in f.read().lower():
                        return True
            except (IOError, OSError):
                pass
            
            # Check for Android environment variables
            if os.environ.get('ANDROID_ROOT') or os.environ.get('ANDROID_DATA'):
                return True
            
            return False
        except Exception as e:
            logger.warning(f"Android detection failed: {e}")
            return False
    
    def _apply_android_settings(self) -> None:
        """Apply Android-specific settings"""
        # Reduce particle count
        from PyPong.core import config
        if hasattr(config, 'MAX_PARTICLES'):
            config.MAX_PARTICLES = min(config.MAX_PARTICLES, 30)
        
        # Enable battery saver by default on Android
        self.battery_saver = True
    
    def set_performance_profile(self, profile: str) -> None:
        """
        Set performance profile.
        
        Args:
            profile: 'low', 'balanced', or 'high'
        """
        if profile not in ('low', 'balanced', 'high'):
            logger.warning(f"Invalid profile: {profile}")
            return
        
        self.performance_profile = profile
        logger.info(f"Performance profile set to: {profile}")
        
        # Apply profile settings
        if profile == 'low':
            self._apply_low_performance()
        elif profile == 'balanced':
            self._apply_balanced_performance()
        elif profile == 'high':
            self._apply_high_performance()
    
    def _apply_low_performance(self) -> None:
        """Apply low performance settings (battery saver)"""
        from PyPong.core import config
        
        # Reduce effects
        if hasattr(config, 'MAX_PARTICLES'):
            config.MAX_PARTICLES = 20
        if hasattr(config, 'MAX_TRAILS'):
            config.MAX_TRAILS = 10
        
        # Lower FPS target
        if hasattr(config, 'FPS'):
            config.FPS = 30
        
        self.battery_saver = True
        logger.info("Low performance mode activated")
    
    def _apply_balanced_performance(self) -> None:
        """Apply balanced performance settings"""
        from PyPong.core import config
        
        if hasattr(config, 'MAX_PARTICLES'):
            config.MAX_PARTICLES = 30
        if hasattr(config, 'MAX_TRAILS'):
            config.MAX_TRAILS = 15
        if hasattr(config, 'FPS'):
            config.FPS = 60
        
        self.battery_saver = False
        logger.info("Balanced performance mode activated")
    
    def _apply_high_performance(self) -> None:
        """Apply high performance settings"""
        from PyPong.core import config
        
        if hasattr(config, 'MAX_PARTICLES'):
            config.MAX_PARTICLES = 50
        if hasattr(config, 'MAX_TRAILS'):
            config.MAX_TRAILS = 20
        if hasattr(config, 'FPS'):
            config.FPS = 60
        
        self.battery_saver = False
        logger.info("High performance mode activated")
    
    def enable_battery_saver(self) -> None:
        """Enable battery saver mode"""
        self.battery_saver = True
        self._apply_low_performance()
    
    def disable_battery_saver(self) -> None:
        """Disable battery saver mode"""
        self.battery_saver = False
        self._apply_balanced_performance()
    
    def get_recommended_settings(self) -> Dict[str, Any]:
        """Get recommended settings for current device"""
        if not self.is_android:
            return {}
        
        # Try to detect device capabilities
        try:
            import psutil
            
            # Check available memory
            memory = psutil.virtual_memory()
            available_mb = memory.available / (1024 * 1024)
            
            # Check CPU count
            cpu_count = psutil.cpu_count()
            
            # Recommend profile based on resources
            if available_mb < 512 or cpu_count <= 2:
                profile = 'low'
            elif available_mb < 1024 or cpu_count <= 4:
                profile = 'balanced'
            else:
                profile = 'high'
            
            return {
                'profile': profile,
                'available_memory_mb': available_mb,
                'cpu_count': cpu_count,
            }
        except ImportError:
            # psutil not available, use conservative defaults
            return {'profile': 'balanced'}
    
    def optimize_touch_input(self) -> Dict[str, Any]:
        """Get optimized touch input settings"""
        return {
            'touch_zone_size': 'large' if self.is_android else 'medium',
            'haptic_feedback': self.is_android,
            'gesture_sensitivity': 'high' if self.is_android else 'medium',
        }


class BackButtonHandler:
    """Handle Android back button"""
    
    def __init__(self):
        self.back_pressed = False
        self.back_callback = None
    
    def set_callback(self, callback) -> None:
        """Set callback for back button press"""
        self.back_callback = callback
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle back button event.
        
        Returns:
            True if back button was pressed
        """
        # Android back button is typically mapped to ESCAPE
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.back_pressed = True
            if self.back_callback:
                self.back_callback()
            return True
        
        return False


class ScreenWakeLock:
    """Prevent screen from sleeping during gameplay"""
    
    def __init__(self):
        self.is_locked = False
        self.is_android = self._detect_android()
    
    def _detect_android(self) -> bool:
        """Detect Android platform"""
        try:
            import os
            return bool(os.environ.get('ANDROID_ROOT'))
        except Exception:
            return False
    
    def acquire(self) -> None:
        """Acquire wake lock to prevent screen sleep"""
        if not self.is_android or self.is_locked:
            return
        
        try:
            # Try to use Android wake lock via jnius
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            View = autoclass('android.view.View')
            
            activity = PythonActivity.mActivity
            activity.getWindow().addFlags(View.KEEP_SCREEN_ON)
            
            self.is_locked = True
            logger.info("Screen wake lock acquired")
        except Exception as e:
            logger.warning(f"Failed to acquire wake lock: {e}")
    
    def release(self) -> None:
        """Release wake lock"""
        if not self.is_android or not self.is_locked:
            return
        
        try:
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            View = autoclass('android.view.View')
            
            activity = PythonActivity.mActivity
            activity.getWindow().clearFlags(View.KEEP_SCREEN_ON)
            
            self.is_locked = False
            logger.info("Screen wake lock released")
        except Exception as e:
            logger.warning(f"Failed to release wake lock: {e}")


class HapticFeedback:
    """Haptic feedback for touch events"""
    
    def __init__(self):
        self.enabled = True
        self.is_android = self._detect_android()
    
    def _detect_android(self) -> bool:
        """Detect Android platform"""
        try:
            import os
            return bool(os.environ.get('ANDROID_ROOT'))
        except Exception:
            return False
    
    def vibrate(self, duration_ms: int = 50) -> None:
        """
        Trigger haptic feedback.
        
        Args:
            duration_ms: Vibration duration in milliseconds
        """
        if not self.enabled or not self.is_android:
            return
        
        try:
            from jnius import autoclass
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            Vibrator = autoclass('android.os.Vibrator')
            
            activity = PythonActivity.mActivity
            vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
            
            if vibrator and vibrator.hasVibrator():
                vibrator.vibrate(duration_ms)
        except Exception as e:
            logger.debug(f"Haptic feedback failed: {e}")
    
    def enable(self) -> None:
        """Enable haptic feedback"""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable haptic feedback"""
        self.enabled = False


# Global instances
_android_optimizer: Optional[AndroidOptimizer] = None
_haptic_feedback: Optional[HapticFeedback] = None
_wake_lock: Optional[ScreenWakeLock] = None


def get_android_optimizer() -> AndroidOptimizer:
    """Get global Android optimizer instance"""
    global _android_optimizer
    if _android_optimizer is None:
        _android_optimizer = AndroidOptimizer()
    return _android_optimizer


def get_haptic_feedback() -> HapticFeedback:
    """Get global haptic feedback instance"""
    global _haptic_feedback
    if _haptic_feedback is None:
        _haptic_feedback = HapticFeedback()
    return _haptic_feedback


def get_wake_lock() -> ScreenWakeLock:
    """Get global wake lock instance"""
    global _wake_lock
    if _wake_lock is None:
        _wake_lock = ScreenWakeLock()
    return _wake_lock
