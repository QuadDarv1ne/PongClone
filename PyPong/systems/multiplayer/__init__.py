"""
Multiplayer system for PyPong
Supports both local PVP and network play
"""
import socket
import struct
import threading
import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from PyPong.core.logger import logger


class ConnectionType(Enum):
    """Type of multiplayer connection"""
    LOCAL_PVP = "local_pvp"      # Two players on same computer
    NETWORK_HOST = "host"        # Hosting a network game
    NETWORK_CLIENT = "client"    # Connecting to host


@dataclass
class GameState:
    """Synchronized game state"""
    paddle1_y: float = 0
    paddle2_y: float = 0
    ball_x: float = 0
    ball_y: float = 0
    ball_vx: float = 0
    ball_vy: float = 0
    player1_score: int = 0
    player2_score: int = 0
    game_over: bool = False
    winner: Optional[int] = None


class NetworkProtocol:
    """Network message protocol"""
    
    # Message types
    MSG_HANDSHAKE = 1
    MSG_GAME_STATE = 2
    MSG_INPUT = 3
    MSG_SCORE = 4
    MSG_GAME_OVER = 5
    MSG_PING = 6
    MSG_CHAT = 7
    
    @staticmethod
    def encode_message(msg_type: int, data: Dict[str, Any]) -> bytes:
        """Encode message to bytes"""
        json_data = json.dumps(data).encode('utf-8')
        header = struct.pack('!BI', msg_type, len(json_data))
        return header + json_data
    
    @staticmethod
    def decode_message(raw: bytes) -> Tuple[int, Dict[str, Any]]:
        """Decode message from bytes"""
        msg_type, length = struct.unpack('!BI', raw[:5])
        data = json.loads(raw[5:5+length].decode('utf-8'))
        return msg_type, data


class MultiplayerBase(ABC):
    """Base class for multiplayer"""
    
    def __init__(self):
        self.connection_type: Optional[ConnectionType] = None
        self.connected: bool = False
        self.player_number: int = 1  # 1 or 2
    
    @abstractmethod
    def connect(self, **kwargs) -> bool:
        """Establish connection"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection"""
        pass
    
    @abstractmethod
    def send_game_state(self, state: GameState) -> None:
        """Send game state to other player"""
        pass
    
    @abstractmethod
    def receive_game_state(self) -> Optional[GameState]:
        """Receive game state from other player"""
        pass
    
    @abstractmethod
    def send_input(self, input_data: Dict[str, bool]) -> None:
        """Send input state"""
        pass
    
    @abstractmethod
    def receive_input(self) -> Optional[Dict[str, bool]]:
        """Receive input state"""
        pass


class LocalPVP(MultiplayerBase):
    """Local two-player mode (same computer)"""
    
    def __init__(self):
        super().__init__()
        self.connection_type = ConnectionType.LOCAL_PVP
        self.connected = True
        self.player_number = 1
    
    def connect(self, **kwargs) -> bool:
        """No connection needed for local"""
        self.connected = True
        return True
    
    def disconnect(self) -> None:
        self.connected = False
    
    def send_game_state(self, state: GameState) -> None:
        # Not needed for local
        pass
    
    def receive_game_state(self) -> Optional[GameState]:
        # Not needed for local
        return None
    
    def send_input(self, input_data: Dict[str, bool]) -> None:
        # Not needed for local
        pass
    
    def receive_input(self) -> Optional[Dict[str, bool]]:
        # Not needed for local
        return None
    
    def set_player_number(self, num: int) -> None:
        """Set which player this is (1 or 2)"""
        self.player_number = num


class NetworkHost(MultiplayerBase):
    """Host a network game"""
    
    def __init__(self, port: int = 9999):
        super().__init__()
        self.connection_type = ConnectionType.NETWORK_HOST
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Buffer for incoming data
        self.input_buffer: Dict[str, bool] = {}
    
    def connect(self, **kwargs) -> bool:
        """Start hosting"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', self.port))
            self.socket.listen(1)
            self.socket.settimeout(1.0)  # Non-blocking with timeout
            
            logger.info(f"Hosting on port {self.port}")
            
            # Wait for client connection
            try:
                self.client_socket, addr = self.socket.accept()
                self.client_socket.settimeout(0.1)
                self.connected = True
                self.player_number = 1
                logger.info(f"Client connected: {addr}")
                
                # Send handshake
                self._send_handshake()
                
                return True
            except socket.timeout:
                logger.warning("No client connected yet")
                return False
                
        except Exception as e:
            logger.error(f"Failed to host: {e}")
            return False
    
    def _send_handshake(self):
        """Send handshake to client"""
        if self.client_socket:
            msg = NetworkProtocol.encode_message(
                NetworkProtocol.MSG_HANDSHAKE,
                {'player_number': 2}  # Client is player 2
            )
            self.client_socket.sendall(msg)
    
    def disconnect(self) -> None:
        """Close connections"""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if self.socket:
            self.socket.close()
        self.connected = False
        logger.info("Host disconnected")
    
    def send_game_state(self, state: GameState) -> None:
        """Send game state to client"""
        if not self.client_socket or not self.connected:
            return
        
        try:
            data = {
                'paddle1_y': state.paddle1_y,
                'paddle2_y': state.paddle2_y,
                'ball_x': state.ball_x,
                'ball_y': state.ball_y,
                'ball_vx': state.ball_vx,
                'ball_vy': state.ball_vy,
                'player1_score': state.player1_score,
                'player2_score': state.player2_score,
                'game_over': state.game_over,
                'winner': state.winner,
            }
            msg = NetworkProtocol.encode_message(NetworkProtocol.MSG_GAME_STATE, data)
            self.client_socket.sendall(msg)
        except Exception as e:
            logger.error(f"Failed to send game state: {e}")
            self.connected = False
    
    def receive_game_state(self) -> Optional[GameState]:
        """For host, this receives client input"""
        return None
    
    def send_input(self, input_data: Dict[str, bool]) -> None:
        """Host doesn't send input (runs the game)"""
        pass
    
    def receive_input(self) -> Optional[Dict[str, bool]]:
        """Receive input from client"""
        if not self.client_socket or not self.connected:
            return None
        
        try:
            # Read available data
            data = self.client_socket.recv(1024)
            if not data:
                return None
            
            msg_type, msg_data = NetworkProtocol.decode_message(data)
            
            if msg_type == NetworkProtocol.MSG_INPUT:
                return msg_data.get('input', {})
            
        except socket.timeout:
            pass
        except Exception as e:
            logger.error(f"Error receiving input: {e}")
            self.connected = False
        
        return None


class NetworkClient(MultiplayerBase):
    """Connect to network host"""
    
    def __init__(self, host: str = "localhost", port: int = 9999):
        super().__init__()
        self.connection_type = ConnectionType.NETWORK_CLIENT
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.running = False
    
    def connect(self, **kwargs) -> bool:
        """Connect to host"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(0.1)
            
            # Receive handshake
            data = self.socket.recv(1024)
            if data:
                msg_type, msg_data = NetworkProtocol.decode_message(data)
                if msg_type == NetworkProtocol.MSG_HANDSHAKE:
                    self.player_number = msg_data.get('player_number', 2)
            
            self.connected = True
            logger.info(f"Connected to {self.host}:{self.port} as player {self.player_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close connection"""
        if self.socket:
            self.socket.close()
        self.connected = False
        logger.info("Client disconnected")
    
    def send_game_state(self, state: GameState) -> None:
        """Client sends input, not game state"""
        pass
    
    def receive_game_state(self) -> Optional[GameState]:
        """Receive game state from host"""
        if not self.socket or not self.connected:
            return None
        
        try:
            data = self.socket.recv(4096)
            if not data:
                return None
            
            msg_type, msg_data = NetworkProtocol.decode_message(data)
            
            if msg_type == NetworkProtocol.MSG_GAME_STATE:
                state = GameState(
                    paddle1_y=msg_data.get('paddle1_y', 0),
                    paddle2_y=msg_data.get('paddle2_y', 0),
                    ball_x=msg_data.get('ball_x', 0),
                    ball_y=msg_data.get('ball_y', 0),
                    ball_vx=msg_data.get('ball_vx', 0),
                    ball_vy=msg_data.get('ball_vy', 0),
                    player1_score=msg_data.get('player1_score', 0),
                    player2_score=msg_data.get('player2_score', 0),
                    game_over=msg_data.get('game_over', False),
                    winner=msg_data.get('winner'),
                )
                return state
            
        except socket.timeout:
            pass
        except Exception as e:
            logger.error(f"Error receiving game state: {e}")
            self.connected = False
        
        return None
    
    def send_input(self, input_data: Dict[str, bool]) -> None:
        """Send player input to host"""
        if not self.socket or not self.connected:
            return
        
        try:
            msg = NetworkProtocol.encode_message(
                NetworkProtocol.MSG_INPUT,
                {'input': input_data}
            )
            self.socket.sendall(msg)
        except Exception as e:
            logger.error(f"Failed to send input: {e}")
            self.connected = False
    
    def receive_input(self) -> Optional[Dict[str, bool]]:
        """Client doesn't receive input"""
        return None


# Factory function
def create_multiplayer(connection_type: str, **kwargs) -> MultiplayerBase:
    """
    Create multiplayer connection
    
    Args:
        connection_type: "local", "host", "client"
        **kwargs: Additional args (host, port for network)
    
    Returns:
        MultiplayerBase instance
    """
    if connection_type == "local":
        return LocalPVP()
    elif connection_type == "host":
        port = kwargs.get('port', 9999)
        return NetworkHost(port)
    elif connection_type == "client":
        host = kwargs.get('host', 'localhost')
        port = kwargs.get('port', 9999)
        return NetworkClient(host, port)
    else:
        raise ValueError(f"Unknown connection type: {connection_type}")
