import pygame
import random
import sys
import os
import math


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        # 오타 수정: __file___ -> __file__
        base = os.path.dirname(__file__)
    return os.path.join(base, relative_path)




pygame.init()
pygame.mixer.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return pygame.font.SysFont(None, size)

def get_title_font(size):
    candidates = ["impact", "arialblack", "segoeui", "malgungothic"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return get_korean_font(size)

WIDTH, HEIGHT = 800, 600
FPS = 60

WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
GRAY    = (20,  20,  40)
BLUE    = (50,  150, 255)
RED     = (220, 50,  50)
YELLOW  = (240, 220, 0)
GREEN   = (50,  220, 80)
ORANGE  = (240, 140, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
game_surface = pygame.Surface((WIDTH, HEIGHT))

pygame.display.set_caption("NOVA BLASTER")
clock = pygame.time.Clock()

font = get_korean_font(30)
font_big = get_korean_font(72)
font_small = get_korean_font(24)
font_warning = get_korean_font(50) 
font_gameover = get_title_font(100)
# --- 수정: 점수용 두꺼운 폰트 추가 ---
font_thick_score = get_title_font(50) 

PLAYER_W, PLAYER_H = 40, 40
ENEMY_W,  ENEMY_H  = 48, 48  
BULLET_W, BULLET_H = 8,  20  
ITEM_W,   ITEM_H   = 30, 30
BLACKHOLE_W, BLACKHOLE_H = 200, 200 

SPAWN_RATE = 30 
ENEMY_LIFETIME = 600

# --- 스프라이트 및 사운드 로드 (resource_path 적용) ---
try:
    player_img = pygame.image.load(resource_path("assets/sprite/Spaceship.png")).convert_alpha()
    player_img = pygame.transform.scale(player_img, (PLAYER_W, PLAYER_H))

    enemy_img = pygame.image.load(resource_path("assets/sprite/Enemy.png")).convert_alpha()
    enemy_img = pygame.transform.scale(enemy_img, (ENEMY_W, ENEMY_H))

    item_img = pygame.image.load(resource_path("assets/sprite/Force_icon.png")).convert_alpha()
    item_img = pygame.transform.scale(item_img, (ITEM_W, ITEM_H))
    
    blackhole_img = pygame.image.load(resource_path("assets/sprite/Blackhole.png")).convert_alpha()
    blackhole_img = pygame.transform.scale(blackhole_img, (BLACKHOLE_W, BLACKHOLE_H))
    
    shoot_sound = pygame.mixer.Sound(resource_path("assets/sound/Shoot.wav"))
    shoot_sound.set_volume(0.3)
    
    bh_warning_sound = pygame.mixer.Sound(resource_path("assets/sound/Blackhole_enter.wav"))
    bh_warning_sound.set_volume(0.1)

    countdown_sound = pygame.mixer.Sound(resource_path("assets/sound/Countdown.wav"))
    countdown_sound.set_volume(0.5)
    
    pygame.mixer.music.load(resource_path("assets/sound/Background.MP3"))
    pygame.mixer.music.set_volume(0.5) 
    
except Exception as e:
    print(f"파일 로드 오류: {e}")
    pygame.quit()
    sys.exit()

def draw_enemy_sprite(surf, rect, push_count, base_image, angle=0):
    alpha = max(40, 255 - (push_count * 80)) 
    temp_img = base_image.copy()
    if angle != 0:
        temp_img = pygame.transform.rotate(temp_img, angle)
    temp_img.set_alpha(alpha)
    new_rect = temp_img.get_rect(center=rect.center)
    surf.blit(temp_img, new_rect.topleft)

def spawn_enemy(existing_enemies, player_rect):
    for _ in range(50):
        x = random.randint(0, WIDTH - ENEMY_W)
        y = random.randint(40, 100 - ENEMY_H) 
        new_rect = pygame.Rect(x, y, ENEMY_W, ENEMY_H)
        if new_rect.colliderect(player_rect.inflate(100, 100)): continue
        overlap = False
        for en in existing_enemies:
            if new_rect.colliderect(en["rect"]):
                overlap = True
                break
        if not overlap:
            return {"rect": new_rect, "float_y": float(y), "timer": 0, "push_count": 0, "knockback": 0, "bh_angle": 0}
    return None

def render_to_screen():
    window_size = screen.get_size()
    scaled_surface = pygame.transform.scale(game_surface, window_size)
    screen.blit(scaled_surface, (0, 0))
    pygame.display.flip()

def main():
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 2)) for _ in range(80)]

    countdown_sound.play() 

    for i in range(3, 0, -1):
        game_surface.fill(GRAY)
        for s in stars: pygame.draw.circle(game_surface, WHITE, (s[0], s[1]), s[2])
        count_text = font_big.render(str(i), True, YELLOW)
        game_surface.blit(count_text, (WIDTH//2 - count_text.get_width()//2, HEIGHT//2 - count_text.get_height()//2))
        render_to_screen()
        
        start_ticks = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_ticks < 1000:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
            clock.tick(60)

    game_surface.fill(GRAY)
    for s in stars: pygame.draw.circle(game_surface, WHITE, (s[0], s[1]), s[2])
    start_text = font_big.render("START!", True, GREEN)
    game_surface.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2 - start_text.get_height()//2))
    render_to_screen()
    pygame.time.delay(500) 

    pygame.mixer.music.play(-1)
    
    player = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 70, PLAYER_W, PLAYER_H)
    bullets = []
    enemies = []
    items = []
    score = 0
    lives = 3
    shoot_cd = 0
    spawn_timer = 0
    invincible = 0
    
    item_spawn_timer = 0
    item_spawn_interval = FPS * 10 
    push_mode_timer = 0
    score_popups = [] 
    tilt_angle = 0  

    blackhole = None
    blackhole_spawn_timer = 0
    blackhole_duration = 0
    blackhole_angle = 0

    while True:
        clock.tick(FPS)
        game_surface.fill(GRAY)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        target_angle = 0
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player.left > 0: 
            player.x -= 6
            target_angle = 15  
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player.right < WIDTH: 
            player.x += 6
            target_angle = -15 
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and player.top > 0: player.y -= 6
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player.bottom < HEIGHT: player.y += 6

        tilt_angle += (target_angle - tilt_angle) * 0.15

        item_spawn_timer += 1
        if item_spawn_timer >= item_spawn_interval: 
            item_spawn_timer = 0
            item_spawn_interval = FPS * 20 
            ix = random.randint(50, WIDTH - 50)
            iy = -ITEM_H
            items.append({"rect": pygame.Rect(ix, iy, ITEM_W, ITEM_H), "float_y": float(iy)})

        for it in items[:]:
            it["float_y"] += 3.5
            it["rect"].y = int(it["float_y"])
            if player.colliderect(it["rect"]):
                push_mode_timer = 420 
                items.remove(it)
            elif it["rect"].top > HEIGHT:
                items.remove(it)

        if push_mode_timer > 0: push_mode_timer -= 1

        shoot_cd -= 1
        if keys[pygame.K_SPACE] and shoot_cd <= 0:
            shoot_sound.play() 
            b_type = "push" if push_mode_timer > 0 else "normal"
            bullets.append({"rect": pygame.Rect(player.centerx - BULLET_W//2, player.top, BULLET_W, BULLET_H), "type": b_type})
            shoot_cd = 15

        for b in bullets[:]:
            b["rect"].y -= 10
            if b["rect"].bottom < 0: bullets.remove(b)

        if blackhole is None:
            blackhole_spawn_timer += 1
            if blackhole_spawn_timer == FPS * 13:
                bh_warning_sound.play(loops=1)
            if blackhole_spawn_timer >= FPS * 15:
                blackhole_spawn_timer = 0
                bh_x = random.randint(50, WIDTH - 50 - BLACKHOLE_W)
                bh_y = random.randint(50, HEIGHT - 200 - BLACKHOLE_H)
                blackhole = {
                    "rect": pygame.Rect(bh_x, bh_y, BLACKHOLE_W, BLACKHOLE_H), 
                    "center": (bh_x + BLACKHOLE_W//2, bh_y + BLACKHOLE_H//2)
                }
                blackhole_duration = FPS * 5

        if blackhole:
            blackhole_duration -= 1
            if blackhole_duration <= 0:
                blackhole = None 
                for en in enemies: en["bh_angle"] = 0 
            else:
                blackhole_angle = (blackhole_angle + 4) % 360
                event_horizon = blackhole["rect"].inflate(-100, -100) 
                
                # 플레이어 끌어당기기 (회전은 제거됨)
                dx = blackhole["center"][0] - player.centerx
                dy = blackhole["center"][1] - player.centery
                dist = math.hypot(dx, dy)
                if dist > 0:
                    player.x += int((dx / dist) * 2.8) 
                    player.y += int((dy / dist) * 2.8)
                    
                player.x = max(0, min(WIDTH - PLAYER_W, player.x))
                player.y = max(0, min(HEIGHT - PLAYER_H, player.y))
                if player.colliderect(event_horizon):
                    lives = 0
                    pygame.mixer.music.stop() 
                    if game_over_screen(score): main() 
                    return
                
                for en in enemies[:]:
                    edx = blackhole["center"][0] - en["rect"].centerx
                    edy = blackhole["center"][1] - en["rect"].centery
                    edist = math.hypot(edx, edy)
                    if edist > 0:
                        en["rect"].x += int((edx / edist) * 3.8)
                        en["float_y"] += (edy / edist) * 3.8
                        en["rect"].y = int(en["float_y"])
                        
                        enemy_bh_rotation_speed = 25 * (1 - edist / 400)
                        if enemy_bh_rotation_speed < 0: enemy_bh_rotation_speed = 0
                        en["bh_angle"] = (en["bh_angle"] + enemy_bh_rotation_speed) % 360
                        
                    if en["rect"].colliderect(event_horizon):
                        if en in enemies: enemies.remove(en)

        spawn_timer += 1
        if spawn_timer >= SPAWN_RATE:
            spawn_timer = 0
            new_en = spawn_enemy(enemies, player)
            if new_en: enemies.append(new_en)

        for en in enemies[:]:
            en["timer"] += 1
            if en["timer"] > ENEMY_LIFETIME:
                enemies.remove(en)
                continue
            if en["knockback"] > 0:
                en["float_y"] -= 2.5
                en["knockback"] -= 1
            else:
                en["float_y"] += 4.3 
            en["rect"].y = int(en["float_y"])

        for b in bullets[:]:
            for en in enemies[:]:
                if b["rect"].colliderect(en["rect"]):
                    if b in bullets: bullets.remove(b)
                    if b["type"] == "normal":
                        enemies.remove(en)
                        score += 10
                    else: 
                        en["push_count"] += 1
                        en["knockback"] = 25 
                        score += 10
                        if en["push_count"] >= 3:
                            enemies.remove(en)
                    break

        for i, en1 in enumerate(enemies):
            if en1["knockback"] > 0:
                for j, en2 in enumerate(enemies):
                    if i != j and en1["rect"].colliderect(en2["rect"]) and en2["knockback"] == 0:
                        en2["knockback"] = 25 
                        en2["push_count"] += 1
                        score += 20 
                        score_popups.append({"text": "+20", "x": en2["rect"].x, "y": en2["rect"].y, "life": 30})
                        if en2["push_count"] >= 3:
                            if en2 in enemies: enemies.remove(en2)
                        break

        if invincible > 0: invincible -= 1
        else:
            for en in enemies:
                if player.colliderect(en["rect"]):
                    lives -= 1
                    invincible = 90
                    enemies.clear()
                    if lives <= 0:
                        pygame.mixer.music.stop() 
                        if game_over_screen(score): main() 
                        return
                    break

        for s in stars: pygame.draw.circle(game_surface, WHITE, (s[0], s[1]), s[2])
        if blackhole:
            rotated_bh = pygame.transform.rotate(blackhole_img, blackhole_angle)
            bh_rect = rotated_bh.get_rect(center=blackhole["center"])
            game_surface.blit(rotated_bh, bh_rect.topleft)
        for it in items:
            game_surface.blit(item_img, (it["rect"].x, it["rect"].y))
        for b in bullets:
            pygame.draw.rect(game_surface, GREEN if b["type"]=="push" else YELLOW, b["rect"])
            
        for en in enemies:
            if blackhole and math.hypot(blackhole["center"][0] - en["rect"].centerx, blackhole["center"][1] - en["rect"].centery) < 400: 
                 draw_enemy_sprite(game_surface, en["rect"], en["push_count"], enemy_img, en["bh_angle"])
            else:
                 draw_enemy_sprite(game_surface, en["rect"], en["push_count"], enemy_img)
                 
        if (invincible // 10) % 2 == 0: 
            # --- 수정: 플레이어는 이제 블랙홀 회전 없이 기본 기울기(tilt_angle)만 적용됩니다 ---
            rotated_player = pygame.transform.rotate(player_img, tilt_angle)
            new_player_rect = rotated_player.get_rect(center=player.center)
            game_surface.blit(rotated_player, new_player_rect.topleft)
            
        game_surface.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        game_surface.blit(font.render(f"Lives: {'♥ ' * lives}", True, RED), (WIDTH - 180, 10))
        if push_mode_timer > 0:
            msg = font.render(f"PUSH MODE: {push_mode_timer//60 + 1}s", True, GREEN)
            game_surface.blit(msg, (WIDTH//2 - 70, 10))
        for p in score_popups[:]:
            game_surface.blit(font_small.render(p["text"], True, YELLOW), (p["x"], p["y"]))
            p["y"] -= 1; p["life"] -= 1
            if p["life"] <= 0: score_popups.remove(p)
        if blackhole is None and FPS * 13 <= blackhole_spawn_timer < FPS * 15:
            if (blackhole_spawn_timer // 10) % 2 == 0:
                warning_text = font_warning.render("블랙홀이 등장합니다!", True, RED)
                text_rect = warning_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                game_surface.blit(warning_text, text_rect.topleft)
        render_to_screen()

# --- 수정: 게임 오버 화면 디자인 업데이트 ---
def game_over_screen(score):
    game_surface.fill((10, 10, 30))
    
    go_text = font_gameover.render("GAME OVER", True, RED)
    go_shadow = font_gameover.render("GAME OVER", True, BLACK)
    go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    
    game_surface.blit(go_shadow, (go_rect.x + 5, go_rect.y + 5))
    game_surface.blit(go_text, go_rect)
    
    # 두껍고 빨간색으로 변경된 Final Score (그림자 효과 포함)
    score_text = font_thick_score.render(f"Final Score: {score}", True, RED)
    score_shadow = font_thick_score.render(f"Final Score: {score}", True, BLACK)
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    
    game_surface.blit(score_shadow, (score_rect.x + 3, score_rect.y + 3))
    game_surface.blit(score_text, score_rect)
    
    # 안내 텍스트
    guide_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
    guide_rect = guide_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    game_surface.blit(guide_text, guide_rect)
    
    render_to_screen()
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()