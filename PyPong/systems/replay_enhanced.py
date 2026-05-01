"""
Enhanced replay system with video export and sharing
"""
import json
import gzip
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from PyPong.core.logger import logger
from PyPong.systems.replay_system import GameFrame, ReplayMetadata, ReplayRecorder, ReplayPlayer


class ReplayCompressor:
    """Advanced replay compression using delta encoding"""
    
    @staticmethod
    def compress_frames(frames: List[GameFrame]) -> List[Dict[str, Any]]:
        """
        Compress frames using delta encoding.
        Only store changes from previous frame.
        """
        if not frames:
            return []
        
        compressed = []
        prev_frame = None
        
        for frame in frames:
            if prev_frame is None:
                # First frame - store everything
                compressed.append(frame.to_dict())
            else:
                # Store only changes
                delta = {}
                delta['frame_number'] = frame.frame_number
                
                # Only include changed values
                if frame.ball_pos != prev_frame.ball_pos:
                    delta['ball_pos'] = frame.ball_pos
                if frame.ball_velocity != prev_frame.ball_velocity:
                    delta['ball_velocity'] = frame.ball_velocity
                if frame.paddle1_pos != prev_frame.paddle1_pos:
                    delta['paddle1_pos'] = frame.paddle1_pos
                if frame.paddle2_pos != prev_frame.paddle2_pos:
                    delta['paddle2_pos'] = frame.paddle2_pos
                if frame.score1 != prev_frame.score1:
                    delta['score1'] = frame.score1
                if frame.score2 != prev_frame.score2:
                    delta['score2'] = frame.score2
                if frame.events:
                    delta['events'] = frame.events
                
                compressed.append(delta)
            
            prev_frame = frame
        
        return compressed
    
    @staticmethod
    def decompress_frames(compressed: List[Dict[str, Any]]) -> List[GameFrame]:
        """Decompress delta-encoded frames"""
        if not compressed:
            return []
        
        frames = []
        prev_data = None
        
        for data in compressed:
            if prev_data is None:
                # First frame
                frame = GameFrame.from_dict(data)
            else:
                # Merge with previous frame
                merged = prev_data.copy()
                merged.update(data)
                frame = GameFrame.from_dict(merged)
            
            frames.append(frame)
            prev_data = frame.to_dict()
        
        return frames


class ReplayExporter:
    """Export replays to various formats"""
    
    def __init__(self):
        self.export_dir = Path('PyPong/data/exports')
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_json(
        self,
        replay_id: str,
        metadata: ReplayMetadata,
        frames: List[GameFrame],
        compress: bool = True
    ) -> Optional[Path]:
        """Export replay to JSON format"""
        try:
            data = {
                'metadata': metadata.to_dict(),
                'frames': [f.to_dict() for f in frames]
            }
            
            filename = f"replay_{replay_id}.json"
            if compress:
                filename += ".gz"
            
            filepath = self.export_dir / filename
            
            if compress:
                with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                    json.dump(data, f)
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            
            logger.info(f"Exported replay to JSON: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Failed to export to JSON: {e}")
            return None
    
    def export_to_csv(
        self,
        replay_id: str,
        frames: List[GameFrame]
    ) -> Optional[Path]:
        """Export replay to CSV format for analysis"""
        try:
            import csv
            
            filepath = self.export_dir / f"replay_{replay_id}.csv"
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    'frame', 'timestamp', 
                    'ball_x', 'ball_y', 'ball_vx', 'ball_vy',
                    'paddle1_x', 'paddle1_y', 'paddle2_x', 'paddle2_y',
                    'score1', 'score2', 'events'
                ])
                
                # Data
                for frame in frames:
                    writer.writerow([
                        frame.frame_number,
                        frame.timestamp,
                        frame.ball_pos[0], frame.ball_pos[1],
                        frame.ball_velocity[0], frame.ball_velocity[1],
                        frame.paddle1_pos[0], frame.paddle1_pos[1],
                        frame.paddle2_pos[0], frame.paddle2_pos[1],
                        frame.score1, frame.score2,
                        ';'.join(frame.events)
                    ])
            
            logger.info(f"Exported replay to CSV: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            return None
    
    def export_to_video(
        self,
        replay_id: str,
        frames: List[GameFrame],
        fps: int = 60,
        resolution: Tuple[int, int] = (1024, 720)
    ) -> Optional[Path]:
        """
        Export replay to video format (requires opencv-python).
        
        Note: This is a placeholder. Full implementation would require:
        - opencv-python (cv2)
        - Rendering each frame to image
        - Encoding to video
        """
        try:
            # Check if opencv is available
            try:
                import cv2
                import numpy as np
            except ImportError:
                logger.warning("opencv-python not installed, cannot export to video")
                return None
            
            filepath = self.export_dir / f"replay_{replay_id}.mp4"
            
            # Video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(filepath), fourcc, fps, resolution)
            
            # Render each frame
            # Note: This would require access to the game renderer
            # For now, this is a placeholder
            logger.info(f"Video export started: {filepath}")
            
            # TODO: Implement frame rendering
            # for frame in frames:
            #     image = render_frame(frame, resolution)
            #     out.write(image)
            
            out.release()
            
            logger.info(f"Exported replay to video: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Failed to export to video: {e}")
            return None


class ReplaySharing:
    """Share replays with others"""
    
    def __init__(self):
        self.share_dir = Path('PyPong/data/shared')
        self.share_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_share_code(self, replay_id: str) -> str:
        """Generate a short share code for replay"""
        # Create hash of replay_id
        hash_obj = hashlib.sha256(replay_id.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Take first 8 characters
        share_code = hash_hex[:8].upper()
        
        return share_code
    
    def create_shareable_package(
        self,
        replay_id: str,
        metadata: ReplayMetadata,
        frames: List[GameFrame]
    ) -> Optional[Dict[str, Any]]:
        """Create a shareable replay package"""
        try:
            share_code = self.generate_share_code(replay_id)
            
            # Compress frames
            compressed_frames = ReplayCompressor.compress_frames(frames)
            
            package = {
                'share_code': share_code,
                'version': '1.0',
                'metadata': metadata.to_dict(),
                'frames': compressed_frames,
                'checksum': self._calculate_checksum(compressed_frames)
            }
            
            # Save package
            filepath = self.share_dir / f"share_{share_code}.json.gz"
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                json.dump(package, f)
            
            logger.info(f"Created shareable package: {share_code}")
            
            return {
                'share_code': share_code,
                'filepath': str(filepath),
                'size_bytes': filepath.stat().st_size
            }
        
        except Exception as e:
            logger.error(f"Failed to create shareable package: {e}")
            return None
    
    def load_shared_replay(self, share_code: str) -> Optional[Tuple[ReplayMetadata, List[GameFrame]]]:
        """Load a shared replay by share code"""
        try:
            filepath = self.share_dir / f"share_{share_code}.json.gz"
            
            if not filepath.exists():
                logger.error(f"Shared replay not found: {share_code}")
                return None
            
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                package = json.load(f)
            
            # Verify checksum
            if not self._verify_checksum(package['frames'], package['checksum']):
                logger.error("Checksum verification failed")
                return None
            
            # Decompress frames
            frames = ReplayCompressor.decompress_frames(package['frames'])
            metadata = ReplayMetadata.from_dict(package['metadata'])
            
            logger.info(f"Loaded shared replay: {share_code}")
            return metadata, frames
        
        except Exception as e:
            logger.error(f"Failed to load shared replay: {e}")
            return None
    
    def _calculate_checksum(self, data: Any) -> str:
        """Calculate checksum for data integrity"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _verify_checksum(self, data: Any, expected: str) -> bool:
        """Verify data checksum"""
        actual = self._calculate_checksum(data)
        return actual == expected


class ReplayAnalyzer:
    """Analyze replay data for statistics and insights"""
    
    @staticmethod
    def analyze_replay(
        metadata: ReplayMetadata,
        frames: List[GameFrame]
    ) -> Dict[str, Any]:
        """Analyze replay and generate statistics"""
        if not frames:
            return {}
        
        # Ball statistics
        ball_speeds = []
        ball_distances = []
        
        for i, frame in enumerate(frames):
            speed = (frame.ball_velocity[0]**2 + frame.ball_velocity[1]**2)**0.5
            ball_speeds.append(speed)
            
            if i > 0:
                prev = frames[i-1]
                dx = frame.ball_pos[0] - prev.ball_pos[0]
                dy = frame.ball_pos[1] - prev.ball_pos[1]
                distance = (dx**2 + dy**2)**0.5
                ball_distances.append(distance)
        
        # Paddle movement
        paddle1_movements = []
        paddle2_movements = []
        
        for i in range(1, len(frames)):
            dy1 = abs(frames[i].paddle1_pos[1] - frames[i-1].paddle1_pos[1])
            dy2 = abs(frames[i].paddle2_pos[1] - frames[i-1].paddle2_pos[1])
            paddle1_movements.append(dy1)
            paddle2_movements.append(dy2)
        
        # Event analysis
        event_counts = {}
        for frame in frames:
            for event in frame.events:
                event_counts[event] = event_counts.get(event, 0) + 1
        
        return {
            'duration': metadata.duration,
            'total_frames': len(frames),
            'fps': len(frames) / metadata.duration if metadata.duration > 0 else 0,
            'ball_stats': {
                'avg_speed': sum(ball_speeds) / len(ball_speeds) if ball_speeds else 0,
                'max_speed': max(ball_speeds) if ball_speeds else 0,
                'total_distance': sum(ball_distances),
            },
            'paddle1_stats': {
                'total_movement': sum(paddle1_movements),
                'avg_movement': sum(paddle1_movements) / len(paddle1_movements) if paddle1_movements else 0,
            },
            'paddle2_stats': {
                'total_movement': sum(paddle2_movements),
                'avg_movement': sum(paddle2_movements) / len(paddle2_movements) if paddle2_movements else 0,
            },
            'events': event_counts,
            'winner': metadata.winner,
            'final_score': metadata.final_score,
        }


class EnhancedReplayManager:
    """Enhanced replay manager with export and sharing"""
    
    def __init__(self):
        self.recorder = ReplayRecorder()
        self.player = ReplayPlayer()
        self.exporter = ReplayExporter()
        self.sharing = ReplaySharing()
        self.analyzer = ReplayAnalyzer()
        
        logger.info("Enhanced replay manager initialized")
    
    def export_replay(
        self,
        replay_id: str,
        format: str = 'json',
        **kwargs
    ) -> Optional[Path]:
        """
        Export replay to specified format.
        
        Args:
            replay_id: Replay ID
            format: Export format ('json', 'csv', 'video')
            **kwargs: Format-specific options
        
        Returns:
            Path to exported file
        """
        # Load replay
        replay_dir = Path('PyPong/data/replays')
        filepath = replay_dir / f"replay_{replay_id}.json.gz"
        
        if not filepath.exists():
            logger.error(f"Replay not found: {replay_id}")
            return None
        
        try:
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = ReplayMetadata.from_dict(data['metadata'])
            frames = [GameFrame.from_dict(f) for f in data['frames']]
            
            # Export based on format
            if format == 'json':
                return self.exporter.export_to_json(replay_id, metadata, frames, **kwargs)
            elif format == 'csv':
                return self.exporter.export_to_csv(replay_id, frames)
            elif format == 'video':
                return self.exporter.export_to_video(replay_id, frames, **kwargs)
            else:
                logger.error(f"Unknown export format: {format}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to export replay: {e}")
            return None
    
    def share_replay(self, replay_id: str) -> Optional[str]:
        """
        Create shareable package and return share code.
        
        Args:
            replay_id: Replay ID
        
        Returns:
            Share code
        """
        # Load replay
        replay_dir = Path('PyPong/data/replays')
        filepath = replay_dir / f"replay_{replay_id}.json.gz"
        
        if not filepath.exists():
            logger.error(f"Replay not found: {replay_id}")
            return None
        
        try:
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = ReplayMetadata.from_dict(data['metadata'])
            frames = [GameFrame.from_dict(f) for f in data['frames']]
            
            result = self.sharing.create_shareable_package(replay_id, metadata, frames)
            
            if result:
                return result['share_code']
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to share replay: {e}")
            return None
    
    def analyze_replay(self, replay_id: str) -> Optional[Dict[str, Any]]:
        """
        Analyze replay and return statistics.
        
        Args:
            replay_id: Replay ID
        
        Returns:
            Analysis results
        """
        # Load replay
        replay_dir = Path('PyPong/data/replays')
        filepath = replay_dir / f"replay_{replay_id}.json.gz"
        
        if not filepath.exists():
            logger.error(f"Replay not found: {replay_id}")
            return None
        
        try:
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = ReplayMetadata.from_dict(data['metadata'])
            frames = [GameFrame.from_dict(f) for f in data['frames']]
            
            return self.analyzer.analyze_replay(metadata, frames)
        
        except Exception as e:
            logger.error(f"Failed to analyze replay: {e}")
            return None
