"""
Localization system for multi-language support
"""
import json
from pathlib import Path
from typing import Dict, Optional
from PyPong.core.logger import logger, log_exception


class Localization:
    """Manages game localization"""
    
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'ru': 'Русский',
        'es': 'Español',
        'de': 'Deutsch',
        'fr': 'Français',
        'zh': '中文',
        'ja': '日本語'
    }
    
    def __init__(self, default_language: str = 'en'):
        self.current_language = default_language
        self.translations: Dict[str, Dict[str, str]] = {}
        self.fallback_language = 'en'
        
        self._load_translations()
        logger.info(f"Localization initialized: {default_language}")
    
    @log_exception
    def _load_translations(self) -> None:
        """Load all translation files"""
        # Use absolute path relative to this file
        locale_dir = Path(__file__).parent.parent / 'locales'

        if not locale_dir.exists():
            logger.warning("Locales directory not found, creating default translations")
            self._create_default_translations()
            return
        
        for lang_code in self.SUPPORTED_LANGUAGES.keys():
            lang_file = locale_dir / f'{lang_code}.json'
            
            if lang_file.exists():
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                    logger.debug(f"Loaded translations: {lang_code}")
                except Exception as e:
                    logger.error(f"Failed to load {lang_code}: {e}")
    
    def _create_default_translations(self) -> None:
        """Create default English translations"""
        locale_dir = Path(__file__).parent.parent / 'locales'
        locale_dir.mkdir(exist_ok=True)
        
        # English translations
        en_translations = {
            # Menu
            "menu.title": "Enhanced Pong",
            "menu.start": "Press ENTER to Start",
            "menu.campaign": "Press C for Campaign",
            "menu.challenges": "Press H for Challenges",
            "menu.minigames": "Press M for Mini-Games",
            "menu.stats": "Press S for Stats",
            "menu.settings": "Press O for Settings",
            "menu.quit": "Press ESC to Quit",
            
            # Game modes
            "mode.ai": "vs AI",
            "mode.pvp": "Player vs Player",
            "mode.campaign": "Campaign",
            "mode.tournament": "Tournament",
            
            # Difficulty
            "difficulty.easy": "Easy",
            "difficulty.medium": "Medium",
            "difficulty.hard": "Hard",
            "difficulty.expert": "Expert",
            "difficulty.insane": "Insane",
            
            # Game
            "game.paused": "PAUSED",
            "game.resume": "Press ENTER to Resume",
            "game.game_over": "GAME OVER",
            "game.winner": "Player {0} Wins!",
            "game.restart": "Press ENTER to Restart",
            "game.score": "Score",
            "game.combo": "{0}x COMBO!",
            "game.multiplier": "{0}x points",
            
            # Campaign
            "campaign.title": "Campaign",
            "campaign.progress": "Progress: {0}%",
            "campaign.stars": "Stars: {0}/{1}",
            "campaign.level": "Level {0}",
            "campaign.complete": "Level Complete!",
            "campaign.stars_earned": "Stars Earned: {0}/3",
            "campaign.objectives": "Objectives:",
            "campaign.modifiers": "Modifiers:",
            
            # Challenges
            "challenges.title": "Challenges",
            "challenges.daily": "Daily Challenges",
            "challenges.weekly": "Weekly Challenges",
            "challenges.reward": "Reward: {0} pts",
            "challenges.completed": "Completed!",
            
            # Achievements
            "achievement.unlocked": "Achievement Unlocked!",
            "achievement.progress": "Progress: {0}/{1}",
            "achievement.points": "{0} points",
            
            # Mini-games
            "minigame.target_practice": "Target Practice",
            "minigame.breakout": "Breakout",
            "minigame.survival": "Survival",
            "minigame.keep_up": "Keep Up",
            "minigame.precision": "Precision",
            "minigame.score": "Score: {0}",
            "minigame.time": "Time: {0}s",
            "minigame.complete": "Complete!",
            
            # Power-ups
            "powerup.speed_boost": "Speed Boost",
            "powerup.large_paddle": "Large Paddle",
            "powerup.slow_ball": "Slow Ball",
            "powerup.multi_ball": "Multi Ball",
            "powerup.shrink_opponent": "Shrink Opponent",
            "powerup.invisible_ball": "Invisible Ball",
            "powerup.reverse_controls": "Reverse Controls",
            "powerup.shield": "Shield",
            "powerup.freeze": "Freeze",
            "powerup.magnet": "Magnet",
            
            # Settings
            "settings.title": "Settings",
            "settings.music_volume": "Music Volume",
            "settings.sfx_volume": "SFX Volume",
            "settings.show_fps": "Show FPS",
            "settings.fullscreen": "Fullscreen",
            "settings.language": "Language",
            "settings.theme": "Theme",
            "settings.back": "Back to Menu",
            
            # Controls
            "controls.player1": "Player 1: A/Z",
            "controls.player2": "Player 2: Arrows",
            "controls.pause": "Pause: ESC",
            
            # Tutorial
            "tutorial.welcome": "Welcome to Pong!",
            "tutorial.objective": "Hit the ball past your opponent",
            "tutorial.controls": "Use A/Z to move your paddle",
            "tutorial.powerups": "Collect power-ups for advantages",
            "tutorial.combo": "Chain hits for combo bonuses",
            "tutorial.complete": "Tutorial Complete!",
            
            # Misc
            "misc.loading": "Loading...",
            "misc.saving": "Saving...",
            "misc.back": "Back",
            "misc.continue": "Continue",
            "misc.yes": "Yes",
            "misc.no": "No",
            "misc.on": "ON",
            "misc.off": "OFF",
        }
        
        # Russian translations
        ru_translations = {
            "menu.title": "Улучшенный Понг",
            "menu.start": "Нажмите ENTER для начала",
            "menu.campaign": "Нажмите C для Кампании",
            "menu.challenges": "Нажмите H для Челленджей",
            "menu.minigames": "Нажмите M для Мини-игр",
            "menu.stats": "Нажмите S для Статистики",
            "menu.settings": "Нажмите O для Настроек",
            "menu.quit": "Нажмите ESC для выхода",
            
            "mode.ai": "против ИИ",
            "mode.pvp": "Игрок против Игрока",
            "mode.campaign": "Кампания",
            "mode.tournament": "Турнир",
            
            "difficulty.easy": "Легко",
            "difficulty.medium": "Средне",
            "difficulty.hard": "Сложно",
            "difficulty.expert": "Эксперт",
            "difficulty.insane": "Безумие",
            
            "game.paused": "ПАУЗА",
            "game.resume": "Нажмите ENTER для продолжения",
            "game.game_over": "ИГРА ОКОНЧЕНА",
            "game.winner": "Игрок {0} победил!",
            "game.restart": "Нажмите ENTER для перезапуска",
            "game.score": "Счет",
            "game.combo": "{0}x КОМБО!",
            "game.multiplier": "{0}x очков",
            
            "campaign.title": "Кампания",
            "campaign.progress": "Прогресс: {0}%",
            "campaign.stars": "Звезды: {0}/{1}",
            "campaign.level": "Уровень {0}",
            "campaign.complete": "Уровень завершен!",
            "campaign.stars_earned": "Получено звезд: {0}/3",
            "campaign.objectives": "Цели:",
            "campaign.modifiers": "Модификаторы:",
            
            "powerup.speed_boost": "Ускорение",
            "powerup.large_paddle": "Большая ракетка",
            "powerup.slow_ball": "Медленный мяч",
            "powerup.multi_ball": "Мультибол",
            "powerup.shield": "Щит",
            "powerup.freeze": "Заморозка",
            
            "settings.title": "Настройки",
            "settings.language": "Язык",
            "settings.back": "Назад в меню",
            
            "misc.loading": "Загрузка...",
            "misc.saving": "Сохранение...",
            "misc.back": "Назад",
            "misc.continue": "Продолжить",
            "misc.yes": "Да",
            "misc.no": "Нет",
            "misc.on": "ВКЛ",
            "misc.off": "ВЫКЛ",
        }
        
        # Save translations
        self._save_translation('en', en_translations)
        self._save_translation('ru', ru_translations)
        
        self.translations['en'] = en_translations
        self.translations['ru'] = ru_translations
    
    def _save_translation(self, lang_code: str, translations: dict) -> None:
        """Save translation file"""
        locale_dir = Path(__file__).parent.parent / 'locales'
        locale_dir.mkdir(exist_ok=True)
        
        try:
            with open(locale_dir / f'{lang_code}.json', 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            logger.debug(f"Saved translations: {lang_code}")
        except Exception as e:
            logger.error(f"Failed to save {lang_code}: {e}")
    
    def get(self, key: str, *args, **kwargs) -> str:
        """Get translated string"""
        # Try current language
        if self.current_language in self.translations:
            text = self.translations[self.current_language].get(key)
            if text:
                return self._format_text(text, *args, **kwargs)
        
        # Fallback to English
        if self.fallback_language in self.translations:
            text = self.translations[self.fallback_language].get(key)
            if text:
                return self._format_text(text, *args, **kwargs)
        
        # Return key if not found
        logger.warning(f"Translation not found: {key}")
        return key
    
    def _format_text(self, text: str, *args, **kwargs) -> str:
        """Format text with arguments"""
        try:
            if args:
                return text.format(*args)
            if kwargs:
                return text.format(**kwargs)
            return text
        except Exception as e:
            logger.error(f"Failed to format text: {e}")
            return text
    
    def set_language(self, lang_code: str) -> bool:
        """Set current language"""
        if lang_code not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported language: {lang_code}")
            return False
        
        self.current_language = lang_code
        logger.info(f"Language changed to: {self.SUPPORTED_LANGUAGES[lang_code]}")
        return True
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages"""
        return self.SUPPORTED_LANGUAGES.copy()


# Global localization instance
_localization: Optional[Localization] = None


def init_localization(language: str = 'en') -> Localization:
    """Initialize global localization"""
    global _localization
    _localization = Localization(language)
    return _localization


def get_localization() -> Localization:
    """Get global localization instance"""
    global _localization
    if _localization is None:
        _localization = Localization()
    return _localization


def t(key: str, *args, **kwargs) -> str:
    """Shorthand for translation"""
    return get_localization().get(key, *args, **kwargs)
