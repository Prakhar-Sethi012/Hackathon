"""
ui_elements.py – Timer, HitBar, ProgressBar, Notification, draw_text
"""

import pygame
import math

WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (220, 50, 50)
GREEN  = (60, 200, 80)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
GREY   = (100, 100, 110)
DARK   = (20, 20, 30)


# ── Utility ───────────────────────────────────────────────────────────────────
def draw_text(surface, text, font, pos, color, center=False, shadow=True):
    if shadow:
        sh = font.render(text, True, (0, 0, 0))
        r = sh.get_rect()
        if center:
            r.center = (pos[0] + 2, pos[1] + 2)
        else:
            r.topleft = (pos[0] + 2, pos[1] + 2)
        surface.blit(sh, r)
    txt = font.render(text, True, color)
    r   = txt.get_rect()
    if center:
        r.center = pos
    else:
        r.topleft = pos
    surface.blit(txt, r)


# ══════════════════════════════════════════════════════════════════════════════
# Timer
# ══════════════════════════════════════════════════════════════════════════════
class Timer:
    def __init__(self, start, max_time):
        self.time     = float(start)
        self.max_time = float(max_time)
        self._shake   = 0.0

    def add(self, seconds):
        self.time = max(0.0, min(self.time + seconds, self.max_time))
        if seconds < 0:
            self._shake = 0.4

    def update(self, dt):
        self.time     = max(0.0, self.time - dt)
        self._shake   = max(0.0, self._shake - dt)

    def draw(self, screen, assets):
        t     = self.time
        low   = t < 5
        col   = RED if low else (YELLOW if t < 12 else GREEN)

        # Box background
        bx, by = 10, 10
        bw, bh = 180, 54

        # Shake effect
        ox = oy = 0
        if low and self._shake > 0:
            ox = int(math.sin(pygame.time.get_ticks() * 0.05) * 4)
            oy = int(math.cos(pygame.time.get_ticks() * 0.07) * 3)

        pygame.draw.rect(screen, (*DARK, 200) if True else DARK,
                         (bx + ox, by + oy, bw, bh), border_radius=10)
        pygame.draw.rect(screen, col,
                         (bx + ox, by + oy, bw, bh), 3, border_radius=10)

        # Label
        draw_text(screen, "⏱ TIME", assets["font_sm"],
                  (bx + ox + 10, by + oy + 6), (180, 180, 180))

        # Value
        mins = int(t) // 60
        secs = int(t) % 60
        ms   = int((t - int(t)) * 100)
        time_str = f"{mins:01d}:{secs:02d}.{ms:02d}" if mins else f"{secs:02d}.{ms:02d}"

        draw_text(screen, time_str, assets["font_lg"],
                  (bx + ox + 14, by + oy + 22), col)

        # Pulse red background when critical
        if low:
            alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 60)
            ov    = pygame.Surface((bw, bh), pygame.SRCALPHA)
            ov.fill((220, 0, 0, alpha))
            screen.blit(ov, (bx + ox, by + oy))


# ══════════════════════════════════════════════════════════════════════════════
# Hit Bar  (Faculty Interaction)
# ══════════════════════════════════════════════════════════════════════════════
class HitBar:
    W, H      = 500, 36
    CURSOR_W  = 18
    GREEN_X   = 180   # green zone start (relative to bar)
    GREEN_W   = 120   # green zone width

    def __init__(self):
        self.visible   = False
        self.cursor_x  = 0.0   # 0..W - CURSOR_W
        self.cursor_dir = 1
        self.speed     = 180   # px/s

    def show(self, game_speed):
        self.visible   = True
        self.cursor_x  = 0.0
        self.cursor_dir = 1
        self.speed     = 140 + game_speed * 18

    def hide(self):
        self.visible = False

    def update(self, dt):
        if not self.visible:
            return
        self.cursor_x += self.speed * self.cursor_dir * dt
        if self.cursor_x >= self.W - self.CURSOR_W:
            self.cursor_x  = self.W - self.CURSOR_W
            self.cursor_dir = -1
        elif self.cursor_x <= 0:
            self.cursor_x  = 0
            self.cursor_dir = 1

    def press(self):
        cx = self.cursor_x
        if self.GREEN_X <= cx <= self.GREEN_X + self.GREEN_W - self.CURSOR_W:
            return "success"
        return "fail"

    def draw(self, screen, assets):
        if not self.visible:
            return

        sw = screen.get_width()
        bx = (sw - self.W) // 2
        by = 12

        # Background
        pygame.draw.rect(screen, DARK, (bx - 4, by - 4, self.W + 8, self.H + 28),
                         border_radius=10)
        pygame.draw.rect(screen, GREY, (bx, by + 16, self.W, self.H - 16), border_radius=6)

        # Red zone (everywhere else)
        pygame.draw.rect(screen, (180, 40, 40),
                         (bx, by + 16, self.W, self.H - 16), border_radius=6)

        # Green zone
        pygame.draw.rect(screen, GREEN,
                         (bx + self.GREEN_X, by + 16, self.GREEN_W, self.H - 16),
                         border_radius=4)

        # Border
        pygame.draw.rect(screen, WHITE, (bx, by + 16, self.W, self.H - 16), 2, border_radius=6)

        # Cursor
        cx = bx + int(self.cursor_x)
        pygame.draw.rect(screen, YELLOW,
                         (cx, by + 14, self.CURSOR_W, self.H - 12), border_radius=4)
        pygame.draw.rect(screen, BLACK,
                         (cx, by + 14, self.CURSOR_W, self.H - 12), 2, border_radius=4)

        # Label
        draw_text(screen, "Press  E  to answer!", assets["font_sm"],
                  (bx + self.W // 2, by + 6), YELLOW, center=True)


# ══════════════════════════════════════════════════════════════════════════════
# Progress Bar
# ══════════════════════════════════════════════════════════════════════════════
CHECKPOINTS = ["🚧 Gate", "🌿 Gazebo", "🏛 SJT"]

class ProgressBar:
    W, H = 460, 28

    def __init__(self, labels):
        self.labels   = labels
        self.progress = 0.0   # 0..1

    def update(self, elapsed, total):
        self.progress = min(elapsed / total, 1.0)

    def draw(self, screen, assets):
        sw = screen.get_width()
        sh = screen.get_height()
        bx = (sw - self.W) // 2
        by = sh - 48

        # Background
        pygame.draw.rect(screen, DARK, (bx - 4, by - 4, self.W + 8, self.H + 8),
                         border_radius=10)
        pygame.draw.rect(screen, GREY, (bx, by, self.W, self.H), border_radius=8)

        # Fill
        fw = int(self.W * self.progress)
        if fw > 0:
            pygame.draw.rect(screen, (50, 180, 255),
                             (bx, by, fw, self.H), border_radius=8)

        # Checkpoint markers
        for i, lbl in enumerate(CHECKPOINTS):
            mx = bx + int(self.W * (i / (len(CHECKPOINTS) - 1)) if len(CHECKPOINTS) > 1 else self.W)
            reached = self.progress >= (i / max(len(CHECKPOINTS) - 1, 1))
            col = YELLOW if reached else (120, 120, 120)
            pygame.draw.circle(screen, col, (mx, by + self.H // 2), 7)
            font = assets["font_sm"]
            txt  = font.render(lbl, True, col)
            screen.blit(txt, txt.get_rect(center=(mx, by - 12)))

        # Border
        pygame.draw.rect(screen, WHITE, (bx, by, self.W, self.H), 2, border_radius=8)

        # Running icon
        rx = bx + fw
        pygame.draw.circle(screen, YELLOW, (rx, by + self.H // 2), 10)


# ══════════════════════════════════════════════════════════════════════════════
# Floating Notification
# ══════════════════════════════════════════════════════════════════════════════
class Notification:
    LIFETIME = 2.0

    def __init__(self, text, color, x, y):
        self.text  = text
        self.color = color
        self.x     = x
        self.y     = float(y)
        self.life  = self.LIFETIME
        self.dead  = False

    def update(self, dt):
        self.life -= dt
        self.y    -= 30 * dt
        if self.life <= 0:
            self.dead = True

    def draw(self, screen, assets):
        alpha = max(0, min(255, int(255 * self.life / self.LIFETIME)))
        surf  = assets["font_md"].render(self.text, True, self.color)
        surf.set_alpha(alpha)
        r = surf.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(surf, r)