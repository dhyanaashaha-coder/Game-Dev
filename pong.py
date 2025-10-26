"""
PONG (single-file) - pygame

Features:
- Main game loop
- Drawing (rects) and simple sprite art support
- Animations & movement
- Input detection (W/S and Up/Down)
- Collisions (ball <-> paddles, ball <-> walls)
- Simple enemy AI (toggleable)
- Two-player mode (toggleable)
- Game over screen + restart
- Optional: music (commented lines show how to add)

Run: python pong_pygame.py
Requires: pygame (pip install pygame)

Controls:
- Player 1: W (up), S (down)
- Player 2 / AI: Up / Down
- TAB: toggle AI on/of
- SPACE: pause
- R: restart after game over
- ESC or window close: quit
"""

import pygame
import sys
import random

# ===================== Config =====================
WIDTH, HEIGHT = 900, 600
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 14, 100
BALL_SIZE = 16
PADDLE_SPEED = 6
AI_SPEED = 5
WINNING_SCORE = 10

# Colors
WHITE = (245, 245, 245)
BLACK = (12, 12, 12)
ACCENT = (40, 200, 255)

# ===================== Game Objects =====================
class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = 0

    def move(self, dy):
        self.rect.y += dy
        # keep on screen
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def update(self):
        if self.speed != 0:
            self.move(self.speed)

    def draw(self, surf):
        pygame.draw.rect(surf, WHITE, self.rect, border_radius=6)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect((WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2), (BALL_SIZE, BALL_SIZE))
        self.reset()

    def reset(self, direction=None):
        self.rect.center = (WIDTH//2, HEIGHT//2)
        angle = random.uniform(-0.4, 0.4)  # radians-ish for slope
        speed = 6
        # choose left or right
        if direction is None:
            direction = random.choice([-1, 1])
        self.vel = [direction * speed, speed * angle]

    def update(self):
        self.rect.x += int(self.vel[0])
        self.rect.y += int(self.vel[1])
        # top/bottom bounce
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vel[1] = -self.vel[1]
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel[1] = -self.vel[1]

    def draw(self, surf):
        pygame.draw.ellipse(surf, ACCENT, self.rect)

# ===================== Utility =====================

def clamp(v, a, b):
    return max(a, min(b, v))

# ===================== Main =====================

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Pong - Python / Pygame')
    clock = pygame.time.Clock()

    # Fonts
    font = pygame.font.SysFont('Consolas', 30)
    big_font = pygame.font.SysFont('Consolas', 64)

    # Sound (optional) - put 'bounce.wav' and 'score.wav' in same folder
    # pygame.mixer.init()
    # bounce_sfx = pygame.mixer.Sound('bounce.wav')
    # score_sfx = pygame.mixer.Sound('score.wav')
    # pygame.mixer.music.load('background.mp3')
    # pygame.mixer.music.play(-1)

    # Game state
    left = Paddle(30, HEIGHT//2 - PADDLE_HEIGHT//2)
    right = Paddle(WIDTH - 30 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2)
    ball = Ball()

    score_left = 0
    score_right = 0

    is_paused = False
    ai_enabled = True
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_w:
                    left.speed = -PADDLE_SPEED
                if event.key == pygame.K_s:
                    left.speed = PADDLE_SPEED
                if event.key == pygame.K_UP:
                    right.speed = -PADDLE_SPEED
                if event.key == pygame.K_DOWN:
                    right.speed = PADDLE_SPEED
                if event.key == pygame.K_TAB:
                    ai_enabled = not ai_enabled
                if event.key == pygame.K_SPACE:
                    is_paused = not is_paused
                if event.key == pygame.K_r and game_over:
                    # restart
                    score_left = 0
                    score_right = 0
                    ball.reset()
                    game_over = False
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_w, pygame.K_s):
                    left.speed = 0
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    right.speed = 0

        if not is_paused and not game_over:
            # Update paddles
            left.update()

            # AI movement for right paddle
            if ai_enabled:
                # naive AI: move towards ball center
                # add deadzone so it's not perfect
                target_y = ball.rect.centery
                if right.rect.centery < target_y - 10:
                    right.move(AI_SPEED)
                elif right.rect.centery > target_y + 10:
                    right.move(-AI_SPEED)
            else:
                right.update()

            # Update ball
            ball.update()

            # Collisions with paddles
            if ball.rect.colliderect(left.rect):
                # push ball to the right, slightly increase speed depending on hit position
                offset = (ball.rect.centery - left.rect.centery) / (PADDLE_HEIGHT / 2)
                speed = abs(ball.vel[0]) + 0.5
                ball.vel[0] = speed
                ball.vel[1] = speed * offset
                ball.rect.left = left.rect.right + 1
                # bounce_sfx.play()

            if ball.rect.colliderect(right.rect):
                offset = (ball.rect.centery - right.rect.centery) / (PADDLE_HEIGHT / 2)
                speed = abs(ball.vel[0]) + 0.5
                ball.vel[0] = -speed
                ball.vel[1] = speed * offset
                ball.rect.right = right.rect.left - 1
                # bounce_sfx.play()

            # Score check
            if ball.rect.left <= 0:
                score_right += 1
                # score_sfx.play()
                if score_right >= WINNING_SCORE:
                    game_over = True
                    winner = 'Right Player'
                ball.reset(direction=1)

            if ball.rect.right >= WIDTH:
                score_left += 1
                # score_sfx.play()
                if score_left >= WINNING_SCORE:
                    game_over = True
                    winner = 'Left Player'
                ball.reset(direction=-1)

        # ========== Draw ==========
        screen.fill(BLACK)

        # center dashed line
        dash_h = 20
        for y in range(0, HEIGHT, dash_h*2):
            pygame.draw.rect(screen, (40,40,40), (WIDTH//2 - 2, y, 4, dash_h))

        # draw paddles & ball
        left.draw(screen)
        right.draw(screen)
        ball.draw(screen)

        # HUD: scores & hints
        score_text = font.render(f"{score_left}", True, WHITE)
        screen.blit(score_text, (WIDTH//4 - score_text.get_width()//2, 20))
        score_text_r = font.render(f"{score_right}", True, WHITE)
        screen.blit(score_text_r, (WIDTH*3//4 - score_text_r.get_width()//2, 20))

        hint = font.render("W/S: Left  |  Up/Down: Right  |  TAB: Toggle AI  |  SPACE: Pause", True, (120,120,120))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 40))

        if is_paused and not game_over:
            ptxt = big_font.render('PAUSED', True, (200,200,200))
            screen.blit(ptxt, (WIDTH//2 - ptxt.get_width()//2, HEIGHT//2 - ptxt.get_height()//2))

        if game_over:
            # overlay dark
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            screen.blit(overlay, (0,0))
            go = big_font.render('GAME OVER', True, ACCENT)
            screen.blit(go, (WIDTH//2 - go.get_width()//2, HEIGHT//2 - 100))
            w = font.render(f'Winner: {winner}', True, WHITE)
            screen.blit(w, (WIDTH//2 - w.get_width()//2, HEIGHT//2 - 20))
            r = font.render('Press R to restart', True, (200,200,200))
            screen.blit(r, (WIDTH//2 - r.get_width()//2, HEIGHT//2 + 40))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
