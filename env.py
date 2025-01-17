import numpy as np
import gymnasium as gym
from gymnasium import spaces
import pygame

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
DINO_WIDTH, DINO_HEIGHT = 40, 40
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 20, 40
GROUND_HEIGHT = 300
FONT_SIZE = 24
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
FPS = 60

class DinoGame(gym.Env):
    def __init__(self):
        super(DinoGame, self).__init__()
        self.state = None
        self.reward = 0
        self.action_space = spaces.Discrete(2)  # 0 = do nothing, 1 = jump
        self.observation_space = spaces.Box(low=0, high=SCREEN_WIDTH, shape=(4,), dtype=np.float32)

        # Pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Google Dino Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', FONT_SIZE)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.dino_y = GROUND_HEIGHT - DINO_HEIGHT
        self.dino_velocity = 0
        self.is_jumping = False
        self.obstacle_x = SCREEN_WIDTH
        self.obstacle_speed = 3.5
        self.reward = 0
        self.state = np.array([self.dino_y, self.dino_velocity, self.obstacle_x, self.obstacle_speed], dtype=np.float32)
        return self.state, {}

    def step(self, action):
        if action == 1 and not self.is_jumping:
            self.is_jumping = True
            self.dino_velocity = -18

        if self.is_jumping:
            self.dino_y += self.dino_velocity
            self.dino_velocity += 1
            if self.dino_y >= GROUND_HEIGHT - DINO_HEIGHT:
                self.dino_y = GROUND_HEIGHT - DINO_HEIGHT
                self.is_jumping = False

        # Update obstacle
        self.obstacle_x -= self.obstacle_speed
        if self.obstacle_x < 0:
            self.obstacle_x = SCREEN_WIDTH
            self.reward += 2

        if self.reward == 4:
            self.obstacle_speed += 0.1
        elif self.reward == 20:
            self.obstacle_speed += 0.11111
        elif self.reward == 36:
            self.obstacle_speed += 0.11111111

        # Check for collisions
        done = False
        if (self.obstacle_x < 50 + DINO_WIDTH and self.obstacle_x + OBSTACLE_WIDTH > 50 and
                self.dino_y + DINO_HEIGHT > GROUND_HEIGHT - OBSTACLE_HEIGHT):
            done = True

        # Update state and reward
        self.state = np.array([self.dino_y, self.dino_velocity, self.obstacle_x, self.obstacle_speed], dtype=np.float32)
        reward = 1 if not done else -100

        return self.state, reward, done, False, {}

    def render(self, mode="human"):
        self.screen.fill(WHITE)
        pygame.draw.line(self.screen, BLACK, (0, GROUND_HEIGHT), (SCREEN_WIDTH, GROUND_HEIGHT), 2)
        pygame.draw.rect(self.screen, BLACK, (50, self.dino_y, DINO_WIDTH, DINO_HEIGHT))
        pygame.draw.rect(self.screen, RED, (self.obstacle_x, GROUND_HEIGHT - OBSTACLE_HEIGHT, OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
        score_text = self.font.render(f"Score: {self.reward}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        pygame.display.flip()
        self.clock.tick(FPS)

        return self.screen

    def close(self):
        pygame.quit()


