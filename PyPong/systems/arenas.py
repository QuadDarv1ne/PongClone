"""
Arena system with obstacles and variations
"""
import pygame
from typing import List, Tuple, Optional
from random import randint, choice
from dataclasses import dataclass
from PyPong.core.constants import ArenaType, Colors
from PyPong.core.logger import logger


@dataclass
class Obstacle:
    """Arena obstacle"""
    rect: pygame.Rect
    color: Tuple[int, int, int]
    destructible: bool = False
    health: int = 1
    moving: bool = False
    velocity: Tuple[float, float] = (0, 0)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw obstacle"""
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, Colors.WHITE.to_tuple(), self.rect, 2)
        
        # Health indicator for destructible obstacles
        if self.destructible and self.health > 1:
            font = pygame.font.SysFont("Helvetica", 16)
            text = font.render(str(self.health), True, Colors.WHITE.to_tuple())
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)
    
    def update(self, arena_bounds: pygame.Rect) -> None:
        """Update obstacle position"""
        if self.moving:
            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]
            
            # Bounce off walls
            if self.rect.left <= arena_bounds.left or self.rect.right >= arena_bounds.right:
                self.velocity = (-self.velocity[0], self.velocity[1])
            if self.rect.top <= arena_bounds.top or self.rect.bottom >= arena_bounds.bottom:
                self.velocity = (self.velocity[0], -self.velocity[1])
    
    def hit(self) -> bool:
        """Hit obstacle, returns True if destroyed"""
        if self.destructible:
            self.health -= 1
            return self.health <= 0
        return False


@dataclass
class Portal:
    """Teleportation portal"""
    entrance: pygame.Rect
    exit: pygame.Rect
    color: Tuple[int, int, int]
    active: bool = True
    cooldown: int = 0
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw portal"""
        # Entrance
        pygame.draw.circle(
            screen, self.color,
            self.entrance.center, self.entrance.width // 2
        )
        pygame.draw.circle(
            screen, Colors.WHITE.to_tuple(),
            self.entrance.center, self.entrance.width // 2, 2
        )
        
        # Exit
        pygame.draw.circle(
            screen, self.color,
            self.exit.center, self.exit.width // 2
        )
        pygame.draw.circle(
            screen, Colors.WHITE.to_tuple(),
            self.exit.center, self.exit.width // 2, 2
        )
    
    def update(self) -> None:
        """Update portal state"""
        if self.cooldown > 0:
            self.cooldown -= 1
            self.active = self.cooldown == 0
    
    def can_teleport(self, ball_rect: pygame.Rect) -> bool:
        """Check if ball can teleport"""
        return self.active and self.entrance.colliderect(ball_rect)
    
    def teleport(self, ball) -> None:
        """Teleport ball to exit"""
        if self.can_teleport(ball.rect):
            ball.rect.center = self.exit.center
            self.cooldown = 30  # 0.5 second cooldown at 60 FPS
            self.active = False
            logger.debug("Ball teleported through portal")


class Arena:
    """Game arena with obstacles"""
    
    def __init__(self, arena_type: ArenaType, width: int = 1024, height: int = 720):
        self.type = arena_type
        self.width = width
        self.height = height
        self.bounds = pygame.Rect(0, 0, width, height)
        self.obstacles: List[Obstacle] = []
        self.portals: List[Portal] = []
        self.shrink_timer = 0
        self.shrink_amount = 0
        
        self._create_arena()
        logger.info(f"Arena created: {arena_type.value}")
    
    def _create_arena(self) -> None:
        """Create arena based on type"""
        if self.type == ArenaType.CLASSIC:
            # Classic arena - no obstacles

            pass

        elif self.type == ArenaType.OBSTACLES:
            self._create_static_obstacles()

        elif self.type == ArenaType.MOVING_WALLS:
            self._create_moving_obstacles()

        elif self.type == ArenaType.PORTALS:
            self._create_portals()

        elif self.type == ArenaType.SHRINKING:
            # Shrinking arena - boundaries reduce over time
            pass
    
    def _create_static_obstacles(self) -> None:
        """Create static obstacles"""
        # Center obstacles
        for i in range(3):
            y = 200 + i * 150
            obstacle = Obstacle(
                pygame.Rect(self.width // 2 - 25, y, 50, 80),
                Colors.GRAY.to_tuple(),
                destructible=False
            )
            self.obstacles.append(obstacle)
        
        # Side obstacles
        for side in [200, self.width - 250]:
            for i in range(2):
                y = 150 + i * 300
                obstacle = Obstacle(
                    pygame.Rect(side, y, 50, 100),
                    Colors.GRAY.to_tuple(),
                    destructible=True,
                    health=3
                )
                self.obstacles.append(obstacle)
    
    def _create_moving_obstacles(self) -> None:
        """Create moving obstacles"""
        for i in range(4):
            x = randint(200, self.width - 200)
            y = randint(100, self.height - 100)
            vx = choice([-2, -1, 1, 2])
            vy = choice([-2, -1, 1, 2])
            
            obstacle = Obstacle(
                pygame.Rect(x, y, 60, 60),
                Colors.ORANGE.to_tuple(),
                destructible=False,
                moving=True,
                velocity=(vx, vy)
            )
            self.obstacles.append(obstacle)
    
    def _create_portals(self) -> None:
        """Create teleportation portals"""
        # Create 2 portal pairs
        colors = [Colors.CYAN.to_tuple(), Colors.PURPLE.to_tuple()]
        
        for color in colors:
            entrance = pygame.Rect(
                randint(150, 300),
                randint(150, self.height - 150),
                40, 40
            )
            exit_portal = pygame.Rect(
                randint(self.width - 300, self.width - 150),
                randint(150, self.height - 150),
                40, 40
            )
            
            portal = Portal(entrance, exit_portal, color)
            self.portals.append(portal)
    
    def update(self) -> None:
        """Update arena state"""
        # Update obstacles
        for obstacle in self.obstacles:
            obstacle.update(self.bounds)
        
        # Update portals
        for portal in self.portals:
            portal.update()
        
        # Shrinking arena
        if self.type == ArenaType.SHRINKING:
            self.shrink_timer += 1
            if self.shrink_timer >= 300:  # Every 5 seconds at 60 FPS
                self.shrink_timer = 0
                self.shrink_amount += 10
                logger.debug(f"Arena shrunk by {self.shrink_amount}")
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw arena"""
        # Draw shrinking boundaries
        if self.type == ArenaType.SHRINKING and self.shrink_amount > 0:
            # Top/bottom danger zones
            pygame.draw.rect(
                screen, Colors.RED.to_tuple(),
                (0, 0, self.width, self.shrink_amount), 0
            )
            pygame.draw.rect(
                screen, Colors.RED.to_tuple(),
                (0, self.height - self.shrink_amount, self.width, self.shrink_amount), 0
            )
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(screen)
        
        # Draw portals
        for portal in self.portals:
            portal.draw(screen)
    
    def check_ball_collision(self, ball) -> bool:
        """Check if ball collides with obstacles"""
        for obstacle in self.obstacles[:]:
            if ball.rect.colliderect(obstacle.rect):
                # Bounce ball
                ball.velocity_x *= -1
                ball.velocity_y *= -1
                
                # Damage obstacle
                if obstacle.hit():
                    self.obstacles.remove(obstacle)
                    logger.debug("Obstacle destroyed")
                
                return True
        
        return False
    
    def check_portal_collision(self, ball) -> bool:
        """Check if ball enters portal"""
        for portal in self.portals:
            if portal.can_teleport(ball.rect):
                portal.teleport(ball)
                return True
        
        return False
    
    def check_shrink_zone(self, ball) -> bool:
        """Check if ball is in shrink zone"""
        if self.type == ArenaType.SHRINKING:
            if (ball.rect.top < self.shrink_amount or 
                ball.rect.bottom > self.height - self.shrink_amount):
                return True
        return False
    
    def get_safe_spawn_position(self) -> Tuple[int, int]:
        """Get safe position for spawning objects"""
        max_attempts = 50
        for _ in range(max_attempts):
            x = randint(150, self.width - 150)
            y = randint(100 + self.shrink_amount, 
                       self.height - 100 - self.shrink_amount)
            
            test_rect = pygame.Rect(x - 20, y - 20, 40, 40)
            
            # Check if position is clear
            clear = True
            for obstacle in self.obstacles:
                if test_rect.colliderect(obstacle.rect):
                    clear = False
                    break
            
            if clear:
                return (x, y)
        
        # Fallback to center
        return (self.width // 2, self.height // 2)


class ArenaManager:
    """Manages arena selection and creation"""
    
    def __init__(self):
        self.current_arena: Optional[Arena] = None
        self.unlocked_arenas = [ArenaType.CLASSIC]
        logger.info("Arena manager initialized")
    
    def create_arena(self, arena_type: ArenaType) -> Arena:
        """Create and set current arena"""
        self.current_arena = Arena(arena_type)
        return self.current_arena
    
    def unlock_arena(self, arena_type: ArenaType) -> None:
        """Unlock arena type"""
        if arena_type not in self.unlocked_arenas:
            self.unlocked_arenas.append(arena_type)
            logger.info(f"Arena unlocked: {arena_type.value}")
    
    def get_unlocked_arenas(self) -> List[ArenaType]:
        """Get list of unlocked arenas"""
        return self.unlocked_arenas.copy()
