"""
Mobile and responsive UI components
"""
from PyPong.mobile.touch_controls import AdaptiveScreen, TouchControls
from PyPong.mobile.responsive_ui import (
    ResponsiveLayout,
    ScreenOrientation,
    DeviceType,
    AdaptiveButton,
    AdaptiveText,
    GridLayout,
)
from PyPong.mobile.android_optimizations import (
    AndroidOptimizer,
    BackButtonHandler,
    ScreenWakeLock,
    HapticFeedback,
    get_android_optimizer,
    get_haptic_feedback,
    get_wake_lock,
)

__all__ = [
    'AdaptiveScreen',
    'TouchControls',
    'ResponsiveLayout',
    'ScreenOrientation',
    'DeviceType',
    'AdaptiveButton',
    'AdaptiveText',
    'GridLayout',
    'AndroidOptimizer',
    'BackButtonHandler',
    'ScreenWakeLock',
    'HapticFeedback',
    'get_android_optimizer',
    'get_haptic_feedback',
    'get_wake_lock',
]
