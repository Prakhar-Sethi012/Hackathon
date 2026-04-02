"""
entities.py – Player, Obstacle, PowerUp, Professor, ClassroomDoor
All sprites are drawn procedurally with pygame.draw calls.
"""

import pygame
import math
import random

# ── Colour palette ────────────────────────────────────────────────────────────
WHITE   = (255, 255, 255)
BLACK   = (0, 0, 0)
SKIN    = (255, 200, 140)
BLUE    = (50, 100, 200)
RED     = (220, 60, 60)
YELLOW  = (255, 215, 0)
GREEN   = (60, 200, 80)
ORANGE  = (255, 140, 0)
PURPLE  = (140, 60, 200)
GREY    = (150, 150, 160)
DARK    = (40, 40, 60)
BROWN   = (120, 80, 40)


# ══════════════════════════════════════════════════════════════════════════════
# Player
# ══════════════════════════════════════════════════════════════════════════════
class Player:
    W, H       = 40, 64
    JUMP_VEL   = -15
    GRAVITY    = 0.7

    def __init__(self, x, y):
        self.x   = float(x)
        self.y   = float(y)
        self.vy  = 0.0
        self.on_ground = True
        self.anim_t    = 0.0   # walk cycle
        self.rect      = pygame.Rect(int(self.x), int(self.y), self.W, self.H)
        self.is_ducking = False
        self.normal_height = self.rect.height
        self.duck_height = self.rect.height // 2

    def duck(self):
        if self.on_ground and not self.is_ducking:
            self.is_ducking = True
            self.rect.y += (self.normal_height - self.duck_height)
            self.rect.height = self.duck_height

    def stand(self):
        if self.is_ducking:
            self.rect.y -= (self.normal_height - self.duck_height)
            self.rect.height = self.normal_height
            self.is_ducking = False


    def jump(self):
        if self.on_ground and not self.is_ducking:
            self.vy = self.JUMP_VEL
            self.on_ground = False

    def update(self, dt, ground_y):
        self.anim_t += dt * 8
        self.vy += self.GRAVITY
        self.y  += self.vy
        if self.y >= ground_y:
            self.y  = ground_y
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        self.rect.x = int(self.x)

        if not self.is_ducking:
            self.rect.y = int(self.y)

    def draw(self, screen, invincible=False):
        x, y = int(self.x), int(self.y)
        t = self.anim_t

        # ─── DUCK OFFSET ───
        # If ducking, we shift the drawing down so the head lowers 
        # but the feet stay on the ground.
        draw_y = y + 25 if self.is_ducking else y

        # ── Body (white shirt, dark pants) ───────────────────────────────────
        # Pants
        leg_swing = math.sin(t) * 8 if (self.on_ground and not self.is_ducking) else 0
        pygame.draw.rect(screen, DARK, (x + 8,  draw_y + 36, 12, 28))   # left leg
        pygame.draw.rect(screen, DARK, (x + 20, draw_y + 36, 12, 28))   # right leg
        
        # Shoe
        pygame.draw.rect(screen, BLACK, (x + 6 + int(leg_swing),  draw_y + 60, 14, 6))
        pygame.draw.rect(screen, BLACK, (x + 18 - int(leg_swing), draw_y + 60, 14, 6))

        # Shirt
        shirt_col = (100, 150, 255) if not invincible else YELLOW
        # Squash the shirt height if ducking
        shirt_h = 15 if self.is_ducking else 24
        pygame.draw.rect(screen, shirt_col, (x + 5, draw_y + 16, 30, shirt_h))
        
        # Backpack (Hide or move backpack if ducking)
        if not self.is_ducking:
            pygame.draw.rect(screen, BROWN, (x + 30, draw_y + 18, 10, 18))

        # Arms (Keep them static if ducking)
        arm_swing = math.sin(t + math.pi) * 10 if (self.on_ground and not self.is_ducking) else 0
        pygame.draw.line(screen, SKIN, (x + 8, draw_y + 20),  (x + 2,  draw_y + 32 + int(arm_swing)), 4)
        pygame.draw.line(screen, SKIN, (x + 32, draw_y + 20), (x + 38, draw_y + 32 - int(arm_swing)), 4)

        # Head
        pygame.draw.circle(screen, SKIN, (x + 20, draw_y + 12), 13)
        # Hair
        pygame.draw.arc(screen, DARK, (x + 7, draw_y + 1, 26, 18), 0, math.pi, 5)
        # Eyes
        pygame.draw.circle(screen, BLACK, (x + 15, draw_y + 11), 2)
        pygame.draw.circle(screen, BLACK, (x + 25, draw_y + 11), 2)
        
        # Mouth
        if self.on_ground:
            pygame.draw.arc(screen, BLACK, (x + 14, draw_y + 14, 12, 6), math.pi, 2 * math.pi, 2)
        else:
            pygame.draw.arc(screen, BLACK, (x + 14, draw_y + 14, 12, 6), 0, math.pi, 2)

# ══════════════════════════════════════════════════════════════════════════════
# Obstacle  (image-based: shuttle, warden, red_tag)
# ══════════════════════════════════════════════════════════════════════════════
# Sizes must match what main.py passes to load_sprite
OBSTACLE_SIZES = {
    "shuttle": (85, 90),
    "warden":  (85, 90),
    "red_tag": (85, 90),
    "player1": (85, 90),
    "player2": (85, 90),
    "player3": (85, 90),
    "player4": (85, 90),
    "player5": (85, 90),
    "player6": (85, 90),
    "player7": (85, 90)
}

# Hitbox offsets relative to the draw rect: (x_offset, y_offset, width, height)
OBSTACLE_HITBOX = {
    #            x_off  y_off   w    h
    "shuttle": (  10,    8,    40,  88),  # skip empty left space; van body only
    "warden":  (  10,    8,    40,  88),  # trim sides a little
    "red_tag": (  10,    8,    40,  88),  # tight box around the tag
    "player1": (  10,    8,    40,  88),  # slim vertical hitbox
    "player2": (  10,    8,    40,  88),  # slim vertical hitbox
    "player3": (  10,    8,    40,  88),  # slim vertical hitbox
    "player4": (  10,    8,    40,  88),  # slim vertical hitbox
    "player5": (  10,    8,    40,  88),  # slim vertical hitbox
    "player6": (  10,    8,    40,  88),  # slim vertical hitbox
    "player7": (  10,    8,    40,  88),  # slim vertical hitbox
}

class Obstacle:
    def __init__(self, x, y, kind, assets=None):
        self.kind  = kind
        w, h       = OBSTACLE_SIZES[kind]
        # draw_rect: full image position (used only for blitting)
        self.draw_rect = pygame.Rect(x, y + 30 - h, w, h)
        # rect: the actual collision hitbox (smaller, offset into the real sprite)
        ox, oy, hw, hh = OBSTACLE_HITBOX[kind]
        self.rect  = pygame.Rect(
            self.draw_rect.x + ox,
            self.draw_rect.y + oy,
            hw, hh
        )
        self._img  = assets.get(f"img_{kind}") if assets else None

    def update(self, dx):
        self.draw_rect.x -= int(dx)
        self.rect.x       = self.draw_rect.x + OBSTACLE_HITBOX[self.kind][0]

    def draw(self, screen, assets=None):
        img = self._img or (assets.get(f"img_{self.kind}") if assets else None)
        if img:
            screen.blit(img, self.draw_rect.topleft)
        else:
            pygame.draw.rect(screen, ORANGE, self.draw_rect)
            pygame.draw.rect(screen, WHITE,  self.draw_rect, 2)
        # ── Debug: uncomment the line below to see the hitbox in red ──────────
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)


# ══════════════════════════════════════════════════════════════════════════════
# Power-Up
# ══════════════════════════════════════════════════════════════════════════════
PU_COLORS = {
    "od":         (60,  220,  80),
    "invincible": (255, 215,   0),
    "panic":      (220,  50,  50),
}
PU_LABELS = {
    "od":         "OD",
    "invincible": "⚡",
    "panic":      "!",
}

class PowerUp:
    R = 22

    def __init__(self, x, y, kind):
        self.kind  = kind
        self.rect  = pygame.Rect(x - self.R, y - self.R, self.R * 2, self.R * 2)
        self.anim  = random.uniform(0, math.pi * 2)
        self._x    = float(x)
        self._y    = float(y)

    def update(self, dx):
        self._x -= dx
        self.anim += 0.08
        self.rect.centerx = int(self._x)
        self.rect.centery  = int(self._y + math.sin(self.anim) * 6)

    def draw(self, screen):
        col   = PU_COLORS[self.kind]
        label = PU_LABELS[self.kind]
        cx, cy = self.rect.center

        # Glow
        glow_surf = pygame.Surface((self.R * 4, self.R * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*col, 60), (self.R * 2, self.R * 2), self.R * 2)
        screen.blit(glow_surf, (cx - self.R * 2, cy - self.R * 2))

        pygame.draw.circle(screen, col, (cx, cy), self.R)
        pygame.draw.circle(screen, WHITE, (cx, cy), self.R, 2)

        font = pygame.font.SysFont("monospace", 14, bold=True)
        txt  = font.render(label, True, BLACK)
        screen.blit(txt, txt.get_rect(center=(cx, cy)))


# ══════════════════════════════════════════════════════════════════════════════
# Professor
# ══════════════════════════════════════════════════════════════════════════════
class Professor:
    W, H   = 44, 80
    SPEED  = 0   # stationary; scrolls with world

    def __init__(self, x, y):
        self.rect   = pygame.Rect(x, y, self.W, self.H)
        self.active = True
        self.anim   = 0.0

    def update(self, dx):
        self.rect.x -= int(dx)
        self.anim += 0.05

    def draw(self, screen):
        r = self.rect
        x, y = r.x, r.y

        # Robe / gown
        pygame.draw.rect(screen, (20, 20, 80), (x + 5, y + 22, 34, 52))
        # Collar / shirt
        pygame.draw.rect(screen, WHITE, (x + 13, y + 22, 18, 12))
        # Arms
        pygame.draw.rect(screen, (20, 20, 80), (x,      y + 24, 8,  30))
        pygame.draw.rect(screen, (20, 20, 80), (x + 36, y + 24, 8,  30))
        # Hand – pointing
        pygame.draw.circle(screen, SKIN, (x + 2, y + 56), 5)
        # Head
        pygame.draw.circle(screen, SKIN, (x + 22, y + 14), 14)
        # Glasses
        pygame.draw.circle(screen, BLACK, (x + 16, y + 13), 5, 2)
        pygame.draw.circle(screen, BLACK, (x + 28, y + 13), 5, 2)
        pygame.draw.line(screen, BLACK, (x + 21, y + 13), (x + 23, y + 13), 2)
        # Moustache
        pygame.draw.arc(screen, BLACK,
                        pygame.Rect(x + 13, y + 18, 10, 6), 0, math.pi, 2)
        pygame.draw.arc(screen, BLACK,
                        pygame.Rect(x + 23, y + 18, 10, 6), 0, math.pi, 2)
        # Mortarboard hat
        pygame.draw.rect(screen, DARK, (x + 8, y + 2, 28, 6))
        pygame.draw.rect(screen, DARK, (x + 12, y - 12, 20, 14))
        pygame.draw.line(screen, YELLOW, (x + 36, y + 2), (x + 40, y + 14), 2)

        # Speech bubble
        wave = int(math.sin(self.anim * 4) * 3)
        bx, by = x - 80, y - 20 + wave
        pygame.draw.rect(screen, WHITE, (bx, by, 78, 30), border_radius=8)
        pygame.draw.rect(screen, BLACK, (bx, by, 78, 30), 2, border_radius=8)
        pygame.draw.polygon(screen, WHITE, [(bx + 60, by + 28), (bx + 72, by + 40), (bx + 52, by + 28)])
        font = pygame.font.SysFont("monospace", 11, bold=True)
        txt = font.render("Press E!", True, BLACK)
        screen.blit(txt, (bx + 6, by + 8))


# ══════════════════════════════════════════════════════════════════════════════
# Classroom Door  (victory trigger)
# ══════════════════════════════════════════════════════════════════════════════
class ClassroomDoor:
    W, H = 60, 96

    def __init__(self, x, y):
        self.rect  = pygame.Rect(x, y, self.W, self.H)
        self._x    = float(x)
        self._y    = float(y)
        self.anim  = 0.0

    def update(self, dx):
        self._x -= dx
        self.anim += 0.04
        self.rect.x = int(self._x)

    def draw(self, screen):
        r = self.rect
        # Door frame
        pygame.draw.rect(screen, BROWN, r.inflate(8, 8))
        # Door body
        pygame.draw.rect(screen, (200, 150, 80), r)
        # Panels
        pygame.draw.rect(screen, (180, 130, 60), (r.x + 6,  r.y + 8,  r.w - 12, 36), 2)
        pygame.draw.rect(screen, (180, 130, 60), (r.x + 6,  r.y + 52, r.w - 12, 36), 2)
        # Doorknob
        pygame.draw.circle(screen, YELLOW, (r.x + r.w - 10, r.centery), 5)
        # Star/glow effect above door
        glow_y = r.y - 16 + int(math.sin(self.anim * 3) * 4)
        pygame.draw.circle(screen, YELLOW, (r.centerx, glow_y), 10)
        pygame.draw.circle(screen, WHITE,  (r.centerx, glow_y), 5)
        # Label
        font = pygame.font.SysFont("monospace", 11, bold=True)
        txt  = font.render("CLASS", True, WHITE)
        pygame.draw.rect(screen, (60, 40, 20),
                         (r.centerx - 24, r.y - 30, 48, 16), border_radius=4)
        screen.blit(txt, txt.get_rect(center=(r.centerx, r.y - 22)))