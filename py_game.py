import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
GRAVITY = 0.5
FPS = 60

# Colors
SKY_BLUE = (135, 206, 235)
GROUND_COLOR = (139, 69, 19)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)

class HillClimbGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hill Climb Racing Clone")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 36)
        
        self.reset_game()
        
    def reset_game(self):
        self.game_over = False
        self.score = 0
        self.distance = 0
        self.fuel = 100
        self.time = 0
        self.fuel_consumption_rate = 0.05
        
        self.terrain_points = []
        self.generate_terrain()
        
        self.car_pos = [100, 0]
        self.car_angle = 0
        self.car_velocity = [0, 0]
        self.car_power = 1.0
        self.car_suspension = 1.0
        self.car_grip = 1.0
        self.car_fuel_efficiency = 1.0
        
        self.camera_offset = 0
        
        self.coins = []
        self.obstacles = []
        self.fuel_stations = []
        self.generate_game_elements()
        
    def load_images(self):
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background.fill(SKY_BLUE)
        
        for _ in range(15):
            x = random.randint(0, SCREEN_WIDTH * 2)
            y = random.randint(50, 200)
            size = random.randint(50, 150)
            pygame.draw.circle(self.background, WHITE, (x, y), size)
            pygame.draw.circle(self.background, WHITE, (x + size//2, y - size//3), size//2)
            pygame.draw.circle(self.background, WHITE, (x + size, y), size//3)
        
        self.car_img = pygame.Surface((90, 45), pygame.SRCALPHA)
        pygame.draw.rect(self.car_img, (200, 0, 0), (10, 10, 70, 25))
        pygame.draw.rect(self.car_img, (180, 0, 0), (30, 0, 30, 15))
        pygame.draw.rect(self.car_img, (100, 100, 255, 150), (32, 2, 26, 11))
        pygame.draw.circle(self.car_img, BLACK, (20, 38), 12)
        pygame.draw.circle(self.car_img, BLACK, (70, 38), 12)
        pygame.draw.circle(self.car_img, (100, 100, 100), (20, 38), 7)
        pygame.draw.circle(self.car_img, (100, 100, 100), (70, 38), 7)
        
    def generate_terrain(self):
        x = 0
        y = SCREEN_HEIGHT // 2
        self.terrain_points = []
        noise = [random.uniform(-1, 1) for _ in range(200)]
        
        smoothness = 100
        for i in range(SCREEN_WIDTH * 3):
            if i % smoothness == 0:
                target_y = y + noise[(i//smoothness) % len(noise)] * 100
                target_y = max(SCREEN_HEIGHT // 3, min(SCREEN_HEIGHT * 2 // 3, target_y))
            
            if i % smoothness != 0:
                progress = (i % smoothness) / smoothness
                y = y + (target_y - y) * progress * 0.1
            
            self.terrain_points.append((x, y))
            x += 1
    
    def generate_game_elements(self):
        for _ in range(100):
            x = random.randint(500, SCREEN_WIDTH * 3)
            y = self.get_terrain_height(x) - 50
            self.coins.append((x, y))
        
        # 🔥 REDUCED obstacle sizes here
        obstacle_types = [
            lambda x, y: (x, y, 30, 20),  # smaller width and height
            lambda x, y: (x, y-15, 20, 30),
            lambda x, y: (x, y-10, 40, 20)
        ]
        
        for _ in range(30):
            x = random.randint(500, SCREEN_WIDTH * 3)
            y = self.get_terrain_height(x)
            self.obstacles.append(random.choice(obstacle_types)(x, y))
        
        for _ in range(20):
            x = random.randint(500, SCREEN_WIDTH * 3)
            y = self.get_terrain_height(x) - 60
            self.fuel_stations.append((x, y))
    
    def get_terrain_height(self, x):
        if 0 <= x < len(self.terrain_points):
            return self.terrain_points[int(x)][1]
        return SCREEN_HEIGHT // 2
    
    def update_car_physics(self):
        self.car_velocity[1] += GRAVITY
        
        new_x = self.car_pos[0] + self.car_velocity[0]
        new_y = self.car_pos[1] + self.car_velocity[1]
        
        car_rect = pygame.Rect(new_x - 45, new_y - 22, 90, 45)
        for obstacle in self.obstacles:
            obs_rect = pygame.Rect(*obstacle)
            if car_rect.colliderect(obs_rect):
                overlap_x = min(car_rect.right - obs_rect.left, obs_rect.right - car_rect.left)
                overlap_y = min(car_rect.bottom - obs_rect.top, obs_rect.bottom - car_rect.top)
                
                if overlap_x < overlap_y:
                    new_x = obs_rect.left - 45 if self.car_velocity[0] > 0 else obs_rect.right + 45
                    self.car_velocity[0] *= -0.5
                else:
                    new_y = obs_rect.top - 22 if self.car_velocity[1] > 0 else obs_rect.bottom + 22
                    self.car_velocity[1] *= -0.5
                
                self.fuel -= 5
                break
        
        self.car_pos = [new_x, new_y]
        terrain_height = self.get_terrain_height(new_x)
        
        if self.car_pos[1] >= terrain_height - 40:
            self.car_pos[1] = terrain_height - 40
            self.car_velocity[1] = 0
            self.car_velocity[0] *= 0.9 * self.car_grip
            
            x1 = max(0, self.car_pos[0] - 10)
            x2 = min(len(self.terrain_points) - 1, self.car_pos[0] + 10)
            y1 = self.terrain_points[int(x1)][1]
            y2 = self.terrain_points[int(x2)][1]
            self.car_angle = math.atan2(y2 - y1, x2 - x1)
        else:
            self.car_angle += self.car_velocity[0] * 0.01
        
        for coin in self.coins[:]:
            if math.dist(self.car_pos, coin) < 40:
                self.coins.remove(coin)
                self.score += 10
                self.fuel = min(100, self.fuel + 5)
        
        for station in self.fuel_stations[:]:
            if math.dist(self.car_pos, station) < 50:
                self.fuel_stations.remove(station)
                self.score += 20
                self.fuel = min(100, self.fuel + 30)
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        is_moving = False
        
        if keys[pygame.K_LEFT]:
            self.car_velocity[0] -= 0.15 * self.car_power
            is_moving = True
        if keys[pygame.K_RIGHT]:
            self.car_velocity[0] += 0.15 * self.car_power
            is_moving = True
        if keys[pygame.K_UP] and abs(self.car_velocity[1]) < 0.1:
            self.car_velocity[1] = -14 * self.car_suspension
            self.fuel -= 1.2 / self.car_fuel_efficiency
        
        if is_moving and abs(self.car_velocity[1]) < 0.1:
            self.fuel -= self.fuel_consumption_rate / self.car_fuel_efficiency
        
        if keys[pygame.K_p]: self.car_power += 0.1
        if keys[pygame.K_s]: self.car_suspension += 0.1
        if keys[pygame.K_g]: self.car_grip += 0.1
        if keys[pygame.K_f]: self.fuel = min(100, self.fuel + 10)
    
    def update_camera(self):
        target_x = self.car_pos[0] - SCREEN_WIDTH // 3
        self.camera_offset += (target_x - self.camera_offset) * 0.1
        self.distance = max(self.distance, self.car_pos[0] // 10)
        self.time += 1/FPS
        
        if self.fuel <= 0:
            self.game_over = True
            self.fuel = 0
    
    def draw(self):
        bg_offset = -self.camera_offset * 0.3 % SCREEN_WIDTH
        self.screen.blit(self.background, (bg_offset - SCREEN_WIDTH, 0))
        self.screen.blit(self.background, (bg_offset, 0))
        
        for i in range(len(self.terrain_points) - 1):
            x1, y1 = self.terrain_points[i]
            x2, y2 = self.terrain_points[i + 1]
            pygame.draw.line(self.screen, GROUND_COLOR, 
                            (x1 - self.camera_offset, y1), 
                            (x2 - self.camera_offset, y2), 10)
        
        for x, y in self.coins:
            pygame.draw.circle(self.screen, GOLD, (int(x - self.camera_offset), int(y)), 15)
            pygame.draw.circle(self.screen, YELLOW, (int(x - self.camera_offset), int(y)), 10)
        
        for x, y, w, h in self.obstacles:
            pygame.draw.rect(self.screen, (120, 80, 50), (x - self.camera_offset, y, w, h))
        
        for x, y in self.fuel_stations:
            pygame.draw.rect(self.screen, RED, (x - 10 - self.camera_offset, y, 20, 30))
            pygame.draw.rect(self.screen, WHITE, (x - 8 - self.camera_offset, y - 15, 16, 15))
        
        rotated_car = pygame.transform.rotate(self.car_img, -self.car_angle * 180/math.pi)
        car_rect = rotated_car.get_rect(center=(self.car_pos[0] - self.camera_offset, self.car_pos[1]))
        self.screen.blit(rotated_car, car_rect)
        
        pygame.draw.rect(self.screen, (200, 200, 200, 150), (5, 5, 150, 100))
        self.screen.blit(self.font.render(f"Distance: {self.distance}m", True, BLACK), (10, 10))
        self.screen.blit(self.font.render(f"Fuel: {int(self.fuel)}%", True, BLACK), (10, 40))
        self.screen.blit(self.font.render(f"Score: {self.score}", True, BLACK), (10, 70))
        self.screen.blit(self.font.render(f"Time: {int(self.time)}s", True, BLACK), (10, 100))
        
        pygame.draw.rect(self.screen, (150, 150, 150), (10, SCREEN_HEIGHT - 30, 200, 20))
        pygame.draw.rect(self.screen, GREEN if self.fuel > 20 else RED, 
                        (10, SCREEN_HEIGHT - 30, 200 * (self.fuel/100), 20))
        pygame.draw.rect(self.screen, BLACK, (10, SCREEN_HEIGHT - 30, 200, 20), 2)
        
        stats_text = f"Power: {self.car_power:.1f} Susp: {self.car_suspension:.1f} Grip: {self.car_grip:.1f}"
        pygame.draw.rect(self.screen, (200, 200, 200, 150), (SCREEN_WIDTH - 400, 5, 380, 30))
        self.screen.blit(self.font.render(stats_text, True, BLACK), (SCREEN_WIDTH - 395, 10))
        
        if self.game_over:
            pygame.draw.rect(self.screen, (200, 200, 200), (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 - 20, 360, 40))
            self.screen.blit(self.big_font.render("GAME OVER - Press R to Restart", True, BLACK), 
                           (SCREEN_WIDTH//2 - 170, SCREEN_HEIGHT//2 - 10))
    
    def run(self):
        self.load_images()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and self.game_over and event.key == pygame.K_r:
                    self.reset_game()
            
            if not self.game_over:
                self.handle_input()
                self.update_car_physics()
                self.update_camera()
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = HillClimbGame()
    game.run()
