"""
Replay system for recording and playing back games
"""
import json
import gzip
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from PyPong.core.logger import logger, log_exception


@dataclass
class GameFrame:
    """Single frame of game state"""
    frame_number: int
    timestamp: float
    ball_pos: tuple[float, float]
    ball_velocity: tuple[float, float]
    paddle1_pos: tuple[float, float]
    paddle2_pos: tuple[float, float]
    score1: int
    score2: int
    events: List[str]  # Events that occurred this frame
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict) -> 'GameFrame':
        return GameFrame(**data)


@dataclass
class ReplayMetadata:
    """Replay metadata"""
    replay_id: str
    recorded_at: str
    duration: float
    player1_name: str
    player2_name: str
    final_score: tuple[int, int]
    winner: int
    game_mode: str
    difficulty: Optional[str] = None
    total_frames: int = 0
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict) -> 'ReplayMetadata':
        return ReplayMetadata(**data)


class ReplayRecorder:
    """Records game replays"""
    
    def __init__(self):
        self.recording = False
        self.frames: List[GameFrame] = []
        self.metadata: Optional[ReplayMetadata] = None
        self.start_time = 0
        self.frame_count = 0
        
        logger.debug("Replay recorder initialized")
    
    def start_recording(
        self,
        player1_name: str = "Player 1",
        player2_name: str = "Player 2",
        game_mode: str = "pvp",
        difficulty: Optional[str] = None
    ) -> None:
        """Start recording"""
        self.recording = True
        self.frames = []
        self.frame_count = 0
        self.start_time = datetime.now().timestamp()
        
        replay_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.metadata = ReplayMetadata(
            replay_id=replay_id,
            recorded_at=datetime.now().isoformat(),
            duration=0,
            player1_name=player1_name,
            player2_name=player2_name,
            final_score=(0, 0),
            winner=0,
            game_mode=game_mode,
            difficulty=difficulty
        )
        
        logger.info(f"Started recording replay: {replay_id}")
    
    def record_frame(
        self,
        ball,
        paddle1,
        paddle2,
        score1: int,
        score2: int,
        events: Optional[List[str]] = None
    ) -> None:
        """Record a single frame"""
        if not self.recording:
            return
        
        frame = GameFrame(
            frame_number=self.frame_count,
            timestamp=datetime.now().timestamp() - self.start_time,
            ball_pos=(ball.rect.centerx, ball.rect.centery),
            ball_velocity=(ball.velocity_x, ball.velocity_y),
            paddle1_pos=(paddle1.rect.centerx, paddle1.rect.centery),
            paddle2_pos=(paddle2.rect.centerx, paddle2.rect.centery),
            score1=score1,
            score2=score2,
            events=events or []
        )
        
        self.frames.append(frame)
        self.frame_count += 1
    
    def stop_recording(self, winner: int, final_score: tuple[int, int]) -> str:
        """Stop recording and return replay ID"""
        if not self.recording or not self.metadata:
            return ""
        
        self.recording = False
        
        # Update metadata
        self.metadata.duration = datetime.now().timestamp() - self.start_time
        self.metadata.winner = winner
        self.metadata.final_score = final_score
        self.metadata.total_frames = len(self.frames)
        
        logger.info(
            f"Stopped recording replay: {self.metadata.replay_id} "
            f"({self.metadata.total_frames} frames, {self.metadata.duration:.1f}s)"
        )
        
        return self.metadata.replay_id
    
    @log_exception
    def save_replay(self, filename: Optional[str] = None) -> bool:
        """Save replay to file"""
        if not self.metadata or not self.frames:
            logger.warning("No replay data to save")
            return False

        # Create replays directory
        replay_dir = Path(__file__).parent.parent / 'data' / 'replays'
        replay_dir.mkdir(exist_ok=True)
        
        # Generate filename
        if filename is None:
            filename = f"replay_{self.metadata.replay_id}.json.gz"
        
        filepath = replay_dir / filename
        
        try:
            # Prepare data
            data = {
                'metadata': self.metadata.to_dict(),
                'frames': [frame.to_dict() for frame in self.frames]
            }
            
            # Compress and save
            json_str = json.dumps(data)
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                f.write(json_str)
            
            logger.info(f"Replay saved: {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save replay: {e}", exc_info=True)
            return False


class ReplayPlayer:
    """Plays back recorded replays"""
    
    def __init__(self):
        self.playing = False
        self.frames: List[GameFrame] = []
        self.metadata: Optional[ReplayMetadata] = None
        self.current_frame = 0
        self.playback_speed = 1.0
        self.paused = False
        
        logger.debug("Replay player initialized")
    
    @log_exception
    def load_replay(self, filepath: str) -> bool:
        """Load replay from file"""
        try:
            path = Path(filepath)
            if not path.exists():
                logger.error(f"Replay file not found: {filepath}")
                return False
            
            # Load and decompress
            with gzip.open(path, 'rt', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parse data
            self.metadata = ReplayMetadata.from_dict(data['metadata'])
            self.frames = [GameFrame.from_dict(f) for f in data['frames']]
            self.current_frame = 0
            
            logger.info(
                f"Replay loaded: {self.metadata.replay_id} "
                f"({len(self.frames)} frames)"
            )
            return True
        
        except Exception as e:
            logger.error(f"Failed to load replay: {e}", exc_info=True)
            return False
    
    def start_playback(self) -> bool:
        """Start replay playback"""
        if not self.frames:
            logger.warning("No replay loaded")
            return False
        
        self.playing = True
        self.current_frame = 0
        self.paused = False
        
        logger.info("Started replay playback")
        return True
    
    def stop_playback(self) -> None:
        """Stop replay playback"""
        self.playing = False
        self.current_frame = 0
        logger.info("Stopped replay playback")
    
    def pause(self) -> None:
        """Pause playback"""
        self.paused = True
    
    def resume(self) -> None:
        """Resume playback"""
        self.paused = False
    
    def get_current_frame(self) -> Optional[GameFrame]:
        """Get current frame"""
        if not self.playing or self.paused:
            return None
        
        if self.current_frame >= len(self.frames):
            self.stop_playback()
            return None
        
        frame = self.frames[self.current_frame]
        self.current_frame += int(self.playback_speed)
        
        return frame
    
    def seek(self, frame_number: int) -> None:
        """Seek to specific frame"""
        self.current_frame = max(0, min(frame_number, len(self.frames) - 1))
    
    def set_speed(self, speed: float) -> None:
        """Set playback speed (1.0 = normal)"""
        self.playback_speed = max(0.25, min(4.0, speed))
        logger.debug(f"Playback speed set to {self.playback_speed}x")
    
    def get_progress(self) -> float:
        """Get playback progress (0-1)"""
        if not self.frames:
            return 0
        return self.current_frame / len(self.frames)


class ReplayManager:
    """Manages replay recording and playback"""
    
    def __init__(self):
        self.recorder = ReplayRecorder()
        self.player = ReplayPlayer()
        self.auto_save = True
        
        logger.info("Replay manager initialized")
    
    def list_replays(self) -> List[Dict[str, Any]]:
        """List all saved replays"""
        replay_dir = Path(__file__).parent.parent / 'data' / 'replays'
        if not replay_dir.exists():
            return []
        
        replays = []
        for filepath in replay_dir.glob("replay_*.json.gz"):
            try:
                # Load metadata only
                with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                    data = json.load(f)
                
                metadata = data['metadata']
                metadata['filepath'] = str(filepath)
                replays.append(metadata)
            
            except Exception as e:
                logger.error(f"Failed to read replay {filepath}: {e}")
        
        # Sort by date (newest first)
        replays.sort(key=lambda x: x['recorded_at'], reverse=True)
        
        return replays
    
    def delete_replay(self, replay_id: str) -> bool:
        """Delete a replay"""
        replay_dir = Path(__file__).parent.parent / 'data' / 'replays'
        filepath = replay_dir / f"replay_{replay_id}.json.gz"
        
        try:
            if filepath.exists():
                filepath.unlink()
                logger.info(f"Deleted replay: {replay_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete replay: {e}")
        
        return False
    
    def get_replay_stats(self) -> Dict[str, Any]:
        """Get replay statistics"""
        replays = self.list_replays()
        
        if not replays:
            return {
                'total_replays': 0,
                'total_duration': 0,
                'total_size_mb': 0
            }
        
        total_duration = sum(r['duration'] for r in replays)
        
        # Calculate total size
        replay_dir = Path(__file__).parent.parent / 'data' / 'replays'
        total_size = sum(
            f.stat().st_size
            for f in replay_dir.glob("replay_*.json.gz")
        )
        
        return {
            'total_replays': len(replays),
            'total_duration': total_duration,
            'total_size_mb': total_size / (1024 * 1024)
        }
