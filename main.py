"""
VIT Sprint - Main Game Loop & State Manager
Run: python main.py
Requires: pip install pygame
"""
import pygame
import sys
import random
import math
from entities import Player, Obstacle, PowerUp, ClassroomDoor, Professor
from ui_elements import Timer, HitBar, ProgressBar, Notification, draw_text
import os

# ─── Constants ────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1100, 600
FPS = 60
TITLE = "VIT Sprint"

# Colours
WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
RED        = (220, 50, 50)
GREEN      = (60, 200, 80)
YELLOW     = (255, 215, 0)
DARK_GREY  = (30, 30, 40)
SEMI_BLACK = (0, 0, 0, 160)

# Game tuning
START_TIME      = 20.0   # seconds
MAX_TIME        = 40.0
BASE_SPEED      = 4.0
SPEED_INCREMENT = 0.7    # added every 5 s
STAGE_DURATION  = 40     # seconds of background scroll

# Background label sequence (visual only – generated art)
BG_LABELS = ["Main Gate", "Gazebo", "SJT Block"]

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # ── Asset generation (procedural – no external files needed) ─────────────
    assets = generate_assets()

    # ── Game state ────────────────────────────────────────────────────────────
    state = "menu"
    game_data = {}

    while True:
        if state == "menu":
            state = menu_screen(screen, clock, assets)
        elif state == "play":
            state, game_data = play_game(screen, clock, assets)
        elif state == "result":
            state = result_screen(screen, clock, assets, game_data)
        elif state == "quit":
            break

    pygame.quit()
    sys.exit()


# ══════════════════════════════════════════════════════════════════════════════
# Asset Generation
# ══════════════════════════════════════════════════════════════════════════════
def generate_assets():
    assets = {}

    # ── Background: load background.png and tile into a wide surface ──────────
    assets["backgrounds"] = [load_background() for _ in range(3)]

    # ── Start screen image (static, shown before game begins) ────────────────
    try:
        start_img = pygame.image.load(resource_path("start.png")).convert()
        #start_img = pygame.image.load("start.png").convert()
        assets["start_img"] = pygame.transform.scale(start_img, (SCREEN_W, SCREEN_H))
    except Exception:
        assets["start_img"] = assets["backgrounds"][0]  # fallback if missing

    # ── Fonts ─────────────────────────────────────────────────────────────────
    assets["font_lg"]  = pygame.font.SysFont("monospace", 48, bold=True)
    assets["font_md"]  = pygame.font.SysFont("monospace", 28, bold=True)
    assets["font_sm"]  = pygame.font.SysFont("monospace", 18)
    assets["font_xl"]  = pygame.font.SysFont("monospace", 72, bold=True)

    # ── Obstacle / sprite images ───────────────────────────────────────────────
    assets["img_shuttle"] = load_sprite("shuttle.png",   (85,  90))
    assets["img_warden"]  = load_sprite("warden.png",    (85,  90))
    assets["img_red_tag"] = load_sprite("red_tag.png",   (85,  90))
    assets["img_player1"] = load_sprite("player1.png",  (85,  90))
    assets["img_player2"] = load_sprite("player2.png",   (85,  90))
    assets["img_player3"] = load_sprite("player3.png", (85, 90))
    assets["img_player4"] = load_sprite("player4.png", (85, 90))
    assets["img_player5"] = load_sprite("player5.png", (85, 90)) 
    assets["img_player6"] = load_sprite("player6.png", (85, 90)) 
    assets["img_player7"] = load_sprite("player7.png", (85, 90)) 
    # ── Sounds (synthesised beeps) ─────────────────────────────────────────
    assets["snd_jump"]  = make_beep(880, 80)
    assets["snd_hit"]   = make_beep(200, 180)
    assets["snd_win"]   = make_beep(660, 400)
    assets["snd_lose"]  = make_beep(110, 600)
    assets["snd_od"]    = make_beep(550, 200)
    assets["snd_tick"]  = make_beep(1000, 40)

    return assets


def load_background():
    """Load background.png, scale to screen height, tile into a wide surface."""
    try:
        img = pygame.image.load(resource_path("background.png")).convert()
        #img = pygame.image.load("background.png").convert()
    except Exception:
        img = pygame.Surface((SCREEN_W, SCREEN_H))
        img.fill((100, 160, 220))

    aspect = img.get_width() / img.get_height()
    scaled_w = int(SCREEN_H * aspect)
    img = pygame.transform.scale(img, (scaled_w, SCREEN_H))

    total_w = max(SCREEN_W * 3, scaled_w * 2)
    surf = pygame.Surface((total_w, SCREEN_H))
    x = 0
    while x < total_w:
        surf.blit(img, (x, 0))
        x += scaled_w
    return surf


def load_sprite(filename, size):
    """Load a PNG with transparency, strip black background, scale to size."""
    try:
        img = pygame.image.load(resource_path(filename)).convert_alpha()
        #img = pygame.image.load(filename).convert_alpha()
        _remove_black_bg(img)
        img = pygame.transform.scale(img, size)
        return img
    except Exception:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((200, 100, 50, 200))
        return surf


def _remove_black_bg(surface, threshold=40):
    """Set near-black pixels to fully transparent."""
    arr = pygame.surfarray.pixels_alpha(surface)
    rgb = pygame.surfarray.pixels3d(surface)
    mask = (rgb[:, :, 0].astype(int) +
            rgb[:, :, 1].astype(int) +
            rgb[:, :, 2].astype(int)) < threshold
    arr[mask] = 0
    del arr, rgb



def make_beep(freq, duration_ms):
    """Synthesise a simple sine-wave beep."""
    try:
        import numpy as np
        sample_rate = 44100
        n = int(sample_rate * duration_ms / 1000)
        t = np.linspace(0, duration_ms / 1000, n, endpoint=False)
        wave = (np.sin(2 * np.pi * freq * t) * 16000).astype(np.int16)
        stereo = np.column_stack([wave, wave])
        sound = pygame.sndarray.make_sound(stereo)
        return sound
    except Exception:
        return None


def play_sound(assets, key):
    snd = assets.get(key)
    if snd:
        try:
            snd.play()
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════════
# Menu Screen
# ══════════════════════════════════════════════════════════════════════════════
def menu_screen(screen, clock, assets):
    anim = 0

    while True:
        dt = clock.tick(FPS) / 1000
        anim += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return "play"
                if event.key == pygame.K_ESCAPE:
                    return "quit"

        # Draw static start screen image
        screen.blit(assets["start_img"], (0, 0))

        # Dark overlay ((removed right now))
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 40))
        # screen.blit(overlay, (0, 0))
        '''
        # Title
        pulse = abs(math.sin(anim * 2)) * 20
        draw_text(screen, "VIT SPRINT", assets["font_xl"],
                  (SCREEN_W // 2, 130 + int(pulse * 0.3)), YELLOW, center=True)
        draw_text(screen, "Can you make it to class?", assets["font_md"],
                  (SCREEN_W // 2, 210), WHITE, center=True)
        
        # Info box
        info = [
            "⏱  Start: 20s  |  Max: 40s",
            "💀 Timer hits 0 → DEBARRED",
            "🎓 Reach the Door → 100% Attendance",
            "",
            "CONTROLS",
            "  SPACE / ↑  →  Jump",
            "  E / ENTER  →  Answer Professor",
        ]
        y = 265
        for line in info:
            col = YELLOW if line == "CONTROLS" else (200, 230, 255)
            draw_text(screen, line, assets["font_sm"], (SCREEN_W // 2, y), col, center=True)
            y += 24
        '''
        # Blink prompt
        if int(anim * 2) % 2 == 0:
            draw_text(screen, "  PRESS SPACE TO RUN  ",
                      assets["font_md"], (SCREEN_W // 2.07, 450), GREEN, center=True)

        pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════════════
# Main Game
# ══════════════════════════════════════════════════════════════════════════════
def play_game(screen, clock, assets):
    # ── Objects ───────────────────────────────────────────────────────────────
    player      = Player(120, SCREEN_H - 80 - 64)
    timer       = Timer(START_TIME, MAX_TIME)
    hit_bar     = HitBar()
    prog_bar    = ProgressBar(BG_LABELS)
    notifs      = []

    obstacles   = []
    powerups    = []
    professor   = None
    door        = None

    # ── State vars ────────────────────────────────────────────────────────────
    game_speed       = BASE_SPEED
    bg_scroll        = 0.0
    elapsed          = 0.0          # total play time
    speed_timer      = 0.0          # for speed increments
    obs_spawn_timer  = 0.0
    pu_spawn_timer   = 0.0
    prof_timer       = 0.0          # next professor appearance
    next_prof_at     = random.uniform(8, 30)
    freeze_timer     = 0.0          # screen freeze after lecture
    invincible       = False
    invincible_timer = 0.0
    panic_active     = False
    panic_timer      = 0.0
    flicker          = False
    flicker_t        = 0.0
    door_spawned     = False
    victory          = False
    obs_history      = []   # tracks last 2 spawned obstacle types for no-repeat rule
    next_obs_gap     = random.randint(35, 240)  # first gap (px) after player width

    GROUND_Y = SCREEN_H - 80 - 64   # player feet y

    def add_notif(text, color=WHITE):
        notifs.append(Notification(text, color, SCREEN_W // 2, 100))
    last_height = None
    HEIGHT_LEVELS = [
            SCREEN_H - 80 - 30,   # low (ground)
            SCREEN_H - 80 - 75,   # medium
            SCREEN_H - 80 - 110    # high (jump required)
            ]
            

    # ── Main loop ─────────────────────────────────────────────────────────────
    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        elapsed += dt

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", {}

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu", {}

                # Jump
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if player.on_ground:
                        player.jump()
                        play_sound(assets, "snd_jump")

                # Duck start
                if event.key == pygame.K_DOWN:
                    player.duck()

            # ✅ OUTSIDE KEYDOWN
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    player.stand()

                # Professor interaction
                if event.key in (pygame.K_e, pygame.K_RETURN):
                    if professor and professor.active and hit_bar.visible:
                        result = hit_bar.press()
                        if result == "success":
                            timer.add(5)
                            add_notif("+5s Permission Granted!", GREEN)
                            play_sound(assets, "snd_od")
                        else:
                            timer.add(-2)
                            freeze_timer = 1.0
                            add_notif("-2s  The Lecture", RED)
                            play_sound(assets, "snd_hit")
                        professor = None
                        hit_bar.hide()

        if freeze_timer > 0:
            freeze_timer -= dt
            _draw_frame(screen, assets, player, obstacles, powerups, professor,
                        door, timer, hit_bar, prog_bar, notifs, bg_scroll,
                        elapsed, game_speed, panic_active, invincible, flicker, dt)
            # Red flash
            flash = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            flash.fill((200, 0, 0, 80))
            screen.blit(flash, (0, 0))
            pygame.display.flip()
            continue

        # ── Speed ramp ────────────────────────────────────────────────────────
        speed_timer += dt
        if speed_timer >= 5:
            speed_timer = 0
            game_speed = min(game_speed + SPEED_INCREMENT, BASE_SPEED * 2.5)

        # Effective scroll speed (panic slows world, not timer)
        effective_speed = game_speed * (0.8 if panic_active else 1.0) * 60

        # ── Background scroll ─────────────────────────────────────────────────
        bg_scroll += effective_speed * dt
        bg_w = SCREEN_W * 3
        bg_scroll %= bg_w

        # ── Panic power-up timer ──────────────────────────────────────────────
        if panic_active:
            panic_timer -= dt
            if panic_timer <= 0:
                panic_active = False
                add_notif("Speed restored!", YELLOW)

        # ── Invincibility timer ───────────────────────────────────────────────
        if invincible:
            invincible_timer -= dt
            flicker_t += dt
            flicker = int(flicker_t * 12) % 2 == 0
            if invincible_timer <= 0:
                invincible = False
                flicker = False
                add_notif("Invincibility over", YELLOW)

        # ── Timer ─────────────────────────────────────────────────────────────
        timer.update(dt)
        if timer.time <= 0:
            play_sound(assets, "snd_lose")
            return "result", {"victory": False, "score": elapsed}

        # ── Player physics ────────────────────────────────────────────────────
        player.update(dt, GROUND_Y)

        # ── Obstacle spawning ─────────────────────────────────────────────────
        # Each gap is chosen once at spawn time: player_width (40px) + random 40–240px.
        # A new obstacle only appears once the previous one has scrolled far enough
        # to leave exactly that pre-chosen gap.
        PLAYER_W = 40
        if obstacles:
            rightmost_x = max(obs.draw_rect.right for obs in obstacles)
        else:
            rightmost_x = 0

        required_clear = SCREEN_W + 40 - (PLAYER_W + next_obs_gap)
        can_spawn = (not obstacles) or (rightmost_x <= required_clear)

        if can_spawn and obs_spawn_timer <= 0:
            all_types = ["shuttle", "warden", "red_tag", "player1", "player2","player3","player4","player5","player6","player7"]
            if len(obs_history) >= 2 and obs_history[-1] == obs_history[-2]:
                choices = [t for t in all_types if t != obs_history[-1]]
            else:
                choices = all_types
            obs_type = random.choice(choices)
            obs_history.append(obs_type)
            if len(obs_history) > 2:
                obs_history.pop(0)
            
            
            choices = [h for h in HEIGHT_LEVELS if h != last_height]
            y = random.choice(choices)
            last_height = y
            obstacles.append(Obstacle(SCREEN_W + 40, y, obs_type, assets))
            
            #obstacles.append(Obstacle(SCREEN_W + 40, SCREEN_H - 80 - 30, obs_type, assets))
            # Roll the NEXT gap now so every interval is independently random
            next_obs_gap = random.randint(80,340)
            obs_spawn_timer = 0.1   # tiny cooldown to avoid double-spawn in one frame
        else:
            obs_spawn_timer -= dt

        # ── Power-up spawning ─────────────────────────────────────────────────
        pu_spawn_timer -= dt
        if pu_spawn_timer <= 0:
            pu_spawn_timer = random.uniform(7, 34)
            pu_type = random.choice(["od", "od", "invincible", "panic"])
            powerups.append(PowerUp(SCREEN_W + 40, SCREEN_H - 80 - 55, pu_type))

        # ── Professor spawn ───────────────────────────────────────────────────
        prof_timer += dt
        if professor is None and prof_timer >= next_prof_at:
            professor = Professor(SCREEN_W - 60, SCREEN_H - 80 - 80)
            hit_bar.show(game_speed)
            prof_timer = 0
            next_prof_at = random.uniform(10, 28)

        # ── Update obstacles ──────────────────────────────────────────────────
        for obs in obstacles[:]:
            obs.update(effective_speed * dt)
            if obs.rect.right < 0:
                obstacles.remove(obs)
                continue
            is_high=obs.rect.bottom < (GROUND_Y-10)
            if player.is_ducking and is_high:
                continue

            if player.is_ducking and obs.rect.y < SCREEN_H-80-80:
                continue
            if not invincible and player.rect.inflate(-20, -20).colliderect(obs.rect.inflate(-10, -10)):
                timer.add(-2.5)
                msg = {
                    "shuttle":  "-2.5s  Ok Bro ! - Cool Bro ! - Chill bro !",             # aman
                    "warden":   "-2.5s  Don't underestimate me as a LABUBU fan boy!",     # acharya
                    "red_tag":  "-2.5s  Ae daaa ! - Where are you looking ?  :| ",        # Varshith               
                    "player1":  "-2.5s  You Hitting me !! That's crazyyyyy ! ",           # shukla
                    "player2":  "-2.5s  Ghaziabad se hu ! - Bachke rahiyo laadle :)",     # bhavya
                    "player3":  "-2.5s  Chuck It Bruhhh !",                               # sarah
                    "player4":  "-2.5s  Behind this smile is a scary Teenu Byju",         # reenu
                    "player5":  "-2.5s  Oh Boss ! - Zara Sambhal Ke !"        ,           # rujin
                    "player6":  "-2.5s  Oyeeee Lalllluuuuu !!"         ,                  # radhika
                    "player7":  "-2.5s  No problem BUDDY, Be Careful :))"                 # Nitin 
                    
                }.get(obs.kind, "-3s  Ouch!")
                add_notif(msg, RED) 
                play_sound(assets, "snd_hit")
                obstacles.remove(obs)

        # ── Update power-ups ──────────────────────────────────────────────────
        for pu in powerups[:]:
            pu.update(effective_speed * dt)
            if pu.rect.right < 0:
                powerups.remove(pu)
                continue
            if player.rect.inflate(-10, -10).colliderect(pu.rect.inflate(-10, -10)):
                _apply_powerup(pu.kind, timer, add_notif, assets,
                               lambda: setattr(player, "invincible_ref", True))
                if pu.kind == "invincible":
                    invincible = True
                    invincible_timer = 3.0
                    flicker_t = 0
                elif pu.kind == "panic":
                    panic_active = True
                    panic_timer = 5.0
                powerups.remove(pu)

        # ── Update professor ──────────────────────────────────────────────────
        if professor:
            professor.update(effective_speed * dt)
            if professor.rect.right < 0:
                professor = None
                hit_bar.hide()
                timer.add(-1)
                add_notif("-1s  Missed Professor!", RED)

        # ── Hit bar ───────────────────────────────────────────────────────────
        hit_bar.update(dt)

        # ── Spawn classroom door at ~30 s ─────────────────────────────────────
        if elapsed >= 30 and not door_spawned:
            door = ClassroomDoor(SCREEN_W + 50, SCREEN_H - 80 - 86)
            door_spawned = True

        if door:
            door.update(effective_speed * dt)
            if player.rect.inflate(-10, -10).colliderect(door.rect.inflate(-10, -10)):
                play_sound(assets, "snd_win")
                return "result", {"victory": True, "score": elapsed,
                                  "time_left": timer.time}

        # ── Progress bar ──────────────────────────────────────────────────────
        prog_bar.update(elapsed, STAGE_DURATION)

        # ── Notifications ─────────────────────────────────────────────────────
        for n in notifs[:]:
            n.update(dt)
            if n.dead:
                notifs.remove(n)

        # ── Draw ──────────────────────────────────────────────────────────────
        _draw_frame(screen, assets, player, obstacles, powerups, professor,
                    door, timer, hit_bar, prog_bar, notifs, bg_scroll,
                    elapsed, game_speed, panic_active, invincible, flicker, dt)
        pygame.display.flip()

    return "menu", {}


def _apply_powerup(kind, timer, add_notif, assets, _inv_cb):
    if kind == "od":
        bonus = random.randint(5, 10)
        timer.add(bonus)
        add_notif(f"+{bonus}s  OD Collected!", GREEN)
        play_sound(assets, "snd_od")
    elif kind == "invincible":
        add_notif("Invincibility! 3s", YELLOW)
        play_sound(assets, "snd_od")
    elif kind == "panic":
        add_notif("⚠ PANIC! Speed slowed!", RED)
        play_sound(assets, "snd_hit")


def _draw_frame(screen, assets, player, obstacles, powerups, professor,
                door, timer, hit_bar, prog_bar, notifs, bg_scroll,
                elapsed, game_speed, panic_active, invincible, flicker, dt):
    # Background (real image – ground is baked into bg)
    bg_idx = min(int(elapsed / (STAGE_DURATION / 3)), 2)
    bg = assets["backgrounds"][bg_idx]
    bx = int(bg_scroll) % (SCREEN_W * 3)
    screen.blit(bg, (-bx, 0))
    if -bx + SCREEN_W * 3 < SCREEN_W:
        screen.blit(bg, (-bx + SCREEN_W * 3, 0))

    # Entities
    for obs in obstacles:
        obs.draw(screen, assets)
    for pu in powerups:
        pu.draw(screen)
    if professor:
        professor.draw(screen)
    if door:
        door.draw(screen)

    if not flicker:
        player.draw(screen, invincible)

    # Panic overlay
    if panic_active:
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((255, 0, 0, 30))
        screen.blit(ov, (0, 0))

    # UI
    timer.draw(screen, assets)
    hit_bar.draw(screen, assets)
    prog_bar.draw(screen, assets)
    for n in notifs:
        n.draw(screen, assets)

    # Speed indicator
    spd_txt = assets["font_sm"].render(f"Speed: {game_speed:.1f}x", True, (180, 180, 180))
    screen.blit(spd_txt, (SCREEN_W - 130, 10))

    # Panic label
    if panic_active:
        pt = assets["font_md"].render("⚠ PANIC MODE", True, RED)
        screen.blit(pt, (SCREEN_W // 2 - pt.get_width() // 2, SCREEN_H // 2 - 20))


# ══════════════════════════════════════════════════════════════════════════════
# Result Screen
# ══════════════════════════════════════════════════════════════════════════════
def result_screen(screen, clock, assets, data):
    victory    = data.get("victory", False)
    time_left  = data.get("time_left", 0)
    score_time = data.get("score", 0)
    anim       = 0

    if victory:
        headline = "You Made It To GDG"
        sub      = "Lets Do Crazy Things That Matter!"
        colour   = GREEN
    else:
        headline = "REJECTED !"
        sub      = "See you in the Next Semester."
        colour   = RED

    while True:
        dt = clock.tick(FPS) / 1000
        anim += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return "play"
                if event.key == pygame.K_ESCAPE:
                    return "menu"

        bg = assets["backgrounds"][2 if victory else 0]
        screen.blit(bg, (0, 0))
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        # Pulse headline
        scale = 1 + 0.05 * math.sin(anim * 3)
        font_big = assets["font_xl"]
        hl = font_big.render(headline, True, colour)
        screen.blit(hl, hl.get_rect(center=(SCREEN_W // 2, 170)))

        draw_text(screen, sub, assets["font_md"], (SCREEN_W // 2, 250), WHITE, center=True)

        if victory:
            draw_text(screen, f"Time Remaining: {time_left:.2f}s",
                      assets["font_md"], (SCREEN_W // 2, 310), YELLOW, center=True)
        draw_text(screen, f"Distance run: {score_time:.1f}s",
                  assets["font_sm"], (SCREEN_W // 2, 350), (180, 180, 180), center=True)

        draw_text(screen, "SPACE → Play Again     ESC → Menu",
                  assets["font_sm"], (SCREEN_W // 2, 440), (160, 200, 255), center=True)

        pygame.display.flip()


if __name__ == "__main__":
    main()