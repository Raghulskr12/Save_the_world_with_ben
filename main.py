import pygame
import random
import cv2
import mediapipe as mp
import math
import time

import sys
import os

# Function to correctly find assets (images, sounds, etc.)
def resource_path(relative_path):
    """ Get the absolute path for bundled files """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Save the World with Ben 10")

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# Load and scale images
def load_and_scale_image(path, size):
    img = pygame.image.load(path)
    return pygame.transform.scale(img, size)

background = load_and_scale_image(resource_path("assets/back.jpg"), (WIDTH, HEIGHT))
alien_img = load_and_scale_image(resource_path("assets/alien.png"), (50, 50))
friend_img = load_and_scale_image(resource_path("assets/friend.png"), (50, 50))
hand_img = load_and_scale_image(resource_path("assets/hand.png"), (80, 80))

# Initialize sound
pygame.mixer.init()
pygame.mixer.music.load(resource_path("sounds/background.mp3"))
pygame.mixer.music.set_volume(0.5)

class Settings:
    def __init__(self):
        self.music_volume = 0.5
        self.sound_effects_volume = 0.7
        self.difficulty = "Normal"
        self.show_hand = True

class GameObject:
    def __init__(self, img, size, speed):
        self.image = img
        self.size = size
        self.speed = speed
        self.respawn()
        self.direction = random.uniform(0, 2 * math.pi)
        
    def respawn(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
    
    def move(self):
        self.x += math.cos(self.direction) * self.speed
        self.y += math.sin(self.direction) * self.speed
        
        if self.x <= 0 or self.x >= WIDTH - self.size[0]:
            self.direction = math.pi - self.direction
        if self.y <= 0 or self.y >= HEIGHT - self.size[1]:
            self.direction = -self.direction
            
        if random.random() < 0.02:
            self.direction = random.uniform(0, 2 * math.pi)
    
    def draw(self):
        screen.blit(self.image, (int(self.x), int(self.y)))
    
    def check_collision(self, hand_pos, hand_closed):
        if not hand_pos:
            return False
        distance = math.sqrt((self.x - hand_pos[0])**2 + (self.y - hand_pos[1])**2)
        return distance < 50 and hand_closed

class GameState:
    def __init__(self):
        self.score = 0
        self.high_score = 0
        self.time_left = 60
        self.game_active = False
        self.paused = False
        self.settings = Settings()
        self.aliens = [GameObject(alien_img, (50, 50), 3) for _ in range(5)]
        self.friends = [GameObject(friend_img, (50, 50), 2) for _ in range(3)]
        self.start_time = time.time()
        self.pause_start = 0
        self.total_pause_time = 0
        
    def reset(self):
        self.score = 0
        self.time_left = 60
        self.game_active = True
        self.paused = False
        self.start_time = time.time()
        self.total_pause_time = 0
        for obj in self.aliens + self.friends:
            obj.respawn()

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.cap = cv2.VideoCapture(0)
        
    def get_hand_position(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, False
        
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if not results.multi_hand_landmarks:
            return None, False
            
        hand_landmarks = results.multi_hand_landmarks[0]
        x = int(hand_landmarks.landmark[8].x * WIDTH)
        y = int(hand_landmarks.landmark[8].y * HEIGHT)
        
        # Check only index finger and thumb distance
        thumb_tip = hand_landmarks.landmark[4]  # Thumb tip
        index_tip = hand_landmarks.landmark[8]  # Index finger tip
        
        # Calculate distance between thumb and index finger
        distance = math.sqrt(
            (thumb_tip.x - index_tip.x)**2 + 
            (thumb_tip.y - index_tip.y)**2
        )
        
        # Adjusted threshold for more precise pinch detection
        pinch_detected = distance < 0.05  # Reduced threshold for pinch gesture
        
        return (x, y), pinch_detected

class Button:
    def __init__(self, text, pos, size=(200, 50)):
        self.text = text
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.font = pygame.font.Font(None, 36)
        
    def draw(self, surface, selected=False):
        color = GREEN if selected else WHITE
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        pygame.draw.rect(surface, color, self.rect, 2)
        surface.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_ui(game_state):
    font = pygame.font.Font(None, 36)
    
    # Create a top bar background
    top_bar = pygame.Surface((WIDTH, 60))
    top_bar.fill(BLACK)
    top_bar.set_alpha(128)
    screen.blit(top_bar, (0, 0))
    
    # Left side: Score
    score_text = font.render(f"Score: {game_state.score}", True, GREEN)
    screen.blit(score_text, (20, 20))
    
    # Center: High Score
    high_score_text = font.render(f"High Score: {game_state.high_score}", True, GREEN)
    high_score_rect = high_score_text.get_rect(midtop=(WIDTH // 2, 20))
    screen.blit(high_score_text, high_score_rect)
    
    # Right side: Time and Pause Button
    time_text = font.render(f"Time: {int(game_state.time_left)}", True, GREEN)
    time_rect = time_text.get_rect(topright=(WIDTH - 100, 20))
    screen.blit(time_text, time_rect)
    
    # Pause button with proper spacing
    pause_button = pygame.Surface((40, 40))
    pause_button.fill(BLACK)
    pause_button.set_alpha(128)
    pause_rect = pause_button.get_rect(topright=(WIDTH - 20, 10))
    
    # Draw pause icon
    pygame.draw.rect(pause_button, GREEN, (12, 8, 6, 24))  # Left bar
    pygame.draw.rect(pause_button, GREEN, (24, 8, 6, 24))  # Right bar
    
    screen.blit(pause_button, pause_rect)
    return pause_rect

class Button:
    def __init__(self, text, pos, size=(200, 50), align="center"):
        self.text = text
        self.align = align
        self.size = size
        
        # Adjust position based on alignment
        if align == "center":
            self.rect = pygame.Rect(pos[0] - size[0]//2, pos[1], size[0], size[1])
        elif align == "left":
            self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        elif align == "right":
            self.rect = pygame.Rect(pos[0] - size[0], pos[1], size[0], size[1])
            
        self.font = pygame.font.Font(None, 36)
        self.hovered = False
        
    def draw(self, surface, selected=False):
        # Background for button
        pygame.draw.rect(surface, BLACK, self.rect)
        pygame.draw.rect(surface, GREEN if self.hovered else WHITE, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, GREEN if selected or self.hovered else WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def pause_menu(game_state):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill(BLACK)
    overlay.set_alpha(180)
    
    title_font = pygame.font.Font(None, 74)
    buttons = [
        Button("Resume", (WIDTH // 2, HEIGHT // 2 - 80)),
        Button("Settings", (WIDTH // 2, HEIGHT // 2)),
        Button("Quit to Menu", (WIDTH // 2, HEIGHT // 2 + 80))
    ]
    
    while game_state.paused:
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw game screen (frozen)
        screen.blit(overlay, (0, 0))
        
        # Draw pause menu title
        title = title_font.render("PAUSED", True, GREEN)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(title, title_rect)
        
        # Draw buttons
        for button in buttons:
            button.update(mouse_pos)
            button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_state.paused = False
                game_state.total_pause_time += time.time() - game_state.pause_start
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, button in enumerate(buttons):
                    if button.is_clicked(mouse_pos):
                        if i == 0:  # Resume
                            game_state.paused = False
                            game_state.total_pause_time += time.time() - game_state.pause_start
                        elif i == 1:  # Settings
                            if not settings_menu(game_state):
                                return False
                        elif i == 2:  # Quit to Menu
                            game_state.game_active = False
                            game_state.paused = False
                            return True
    return True

def settings_menu(game_state):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill(BLACK)
    
    title_font = pygame.font.Font(None, 74)
    buttons = [
        Button(f"Music: {int(game_state.settings.music_volume * 100)}%", 
               (WIDTH // 2, HEIGHT // 2 - 120)),
        Button(f"Sound Effects: {int(game_state.settings.sound_effects_volume * 100)}%",
               (WIDTH // 2, HEIGHT // 2 - 40)),
        Button(f"Show Hand: {game_state.settings.show_hand}",
               (WIDTH // 2, HEIGHT // 2 + 40)),
        Button("Back", (WIDTH // 2, HEIGHT // 2 + 120))
    ]
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(overlay, (0, 0))
        
        # Draw settings title
        title = title_font.render("SETTINGS", True, GREEN)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title, title_rect)
        
        # Draw buttons
        for button in buttons:
            button.update(mouse_pos)
            button.draw(screen)
            
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, button in enumerate(buttons):
                    if button.is_clicked(mouse_pos):
                        if i == 0:  # Music Volume
                            game_state.settings.music_volume = (game_state.settings.music_volume + 0.1) % 1.1
                            pygame.mixer.music.set_volume(game_state.settings.music_volume)
                            buttons[0].text = f"Music: {int(game_state.settings.music_volume * 100)}%"
                        elif i == 1:  # Sound Effects
                            game_state.settings.sound_effects_volume = (game_state.settings.sound_effects_volume + 0.1) % 1.1
                            buttons[1].text = f"Sound Effects: {int(game_state.settings.sound_effects_volume * 100)}%"
                        elif i == 2:  # Show Hand
                            game_state.settings.show_hand = not game_state.settings.show_hand
                            buttons[2].text = f"Show Hand: {game_state.settings.show_hand}"
                        elif i == 3:  # Back
                            return True
                            
def main_menu(screen, game_state):
    title_font = pygame.font.Font(None, 74)
    buttons = [
        Button("Play Game", (WIDTH // 2, HEIGHT // 2 - 40)),
        Button("Settings", (WIDTH // 2, HEIGHT // 2 + 40)),
        Button("Quit", (WIDTH // 2, HEIGHT // 2 + 120))
    ]
    
    while not game_state.game_active:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(BLACK)
        
        # Draw title
        title = title_font.render("Ben 10: Save the World", True, GREEN)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title, title_rect)
        
        # Draw high score
        score_font = pygame.font.Font(None, 50)
        score_text = score_font.render(f"High Score: {game_state.high_score}", True, GREEN)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(score_text, score_rect)
        
        # Draw buttons
        for button in buttons:
            button.update(mouse_pos)
            button.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, button in enumerate(buttons):
                    if button.is_clicked(mouse_pos):
                        if i == 0:  # Play Game
                            game_state.reset()
                            return True
                        elif i == 1:  # Settings
                            if not settings_menu(game_state):
                                return False
                        elif i == 2:  # Quit
                            return False
    return True

def main():
    game_state = GameState()
    hand_tracker = HandTracker()
    clock = pygame.time.Clock()
    running = True
    
    pygame.mixer.music.play(-1)
    
    while running:
        if not game_state.game_active:
            running = main_menu(screen, game_state)
            continue
        
        hand_pos, pinch_detected = hand_tracker.get_hand_position()
        
        # Handle pause
        pause_rect = None
        if not game_state.paused:
            screen.blit(background, (0, 0))
            
            # Update game objects
            for obj in game_state.aliens + game_state.friends:
                obj.move()
                if obj.check_collision(hand_pos, pinch_detected):
                    if obj in game_state.aliens:
                        game_state.score += 10
                    else:
                        game_state.score -= 5
                    obj.respawn()
                obj.draw()
            
            if game_state.settings.show_hand and hand_pos:
                screen.blit(hand_img, (hand_pos[0] - 40, hand_pos[1] - 40))
            
            # Update time considering pause time
            current_time = time.time()
            game_state.time_left = 60 - (current_time - game_state.start_time - game_state.total_pause_time)
            
            if game_state.time_left <= 0:
                game_state.high_score = max(game_state.high_score, game_state.score)
                game_state.game_active = False
                continue
            
            pause_rect = draw_ui(game_state)
            pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_state.paused = not game_state.paused
                if game_state.paused:
                    game_state.pause_start = time.time()
                else:
                    game_state.total_pause_time += time.time() - game_state.pause_start
            elif event.type == pygame.MOUSEBUTTONDOWN and pause_rect and pause_rect.collidepoint(event.pos):
                game_state.paused = not game_state.paused
                if game_state.paused:
                    game_state.pause_start = time.time()
                
        if game_state.paused:
            if not pause_menu(game_state):
                running = False
        
        clock.tick(60)
    
    # Cleanup
    hand_tracker.cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()  