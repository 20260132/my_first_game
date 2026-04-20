import pygame
import random
import sys
import os

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

# 수정 1: 창 크기 조절(최대화 버튼 활성화) 옵션 추가
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
# 수정 2: 게임 그래픽을 그릴 800x600 고정 크기의 가상 도화지 생성
game_surface = pygame.Surface((WIDTH, HEIGHT))

pygame.display.set_caption("Space Shooter - Enhanced Push Mode")
clock = pygame.time.Clock()
font = get_korean_font(30)
font_big = get_korean_font(72)
font_small = get_korean_font(24)

PLAYER_W, PLAYER_H = 40, 40
ENEMY_W,  ENEMY_H  = 48, 48  
BULLET_W, BULLET_H = 8,  20  
ITEM_W,   ITEM_H   = 30, 30

SPAWN_RATE = 30 
ENEMY_LIFETIME = 600

# --- 스프라이트 및 사운드 로드 ---
try:
    player_img = pygame.image.load(os.path.join(BASE_DIR, "sprite", "Spaceship.png")).convert_alpha()
    player_img = pygame.transform.scale(player_img, (PLAYER_W, PLAYER_H))

    enemy_img = pygame.image.load(os.path.join(BASE_DIR, "sprite", "Enemy.png")).convert_alpha()
    enemy_img = pygame.transform.scale(enemy_img, (ENEMY_W, ENEMY_H))

    item_img = pygame.image.load(os.path.join(BASE_DIR, "sprite", "Force_icon.png")).convert_alpha()
    item_img = pygame.transform.scale(item_img, (ITEM_W, ITEM_H))
    
    shoot_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "sound", "Shoot.wav"))
    shoot_sound.set_volume(0.3)
    
    pygame.mixer.music.load(os.path.join(BASE_DIR, "sound", "Background.MP3"))
    pygame.mixer.music.set_volume(0.5) 
    
except Exception as e:
    print(f"파일 로드 오류: {e}")
    pygame.quit()
    sys.exit()
# ------------------------------------------

def draw_enemy_sprite(surf, rect, push_count, base_image):
    alpha = max(40, 255 - (push_count * 80)) 
    temp_img = base_image.copy()
    temp_img.set_alpha(alpha)
    surf.blit(temp_img, (rect.x, rect.y))

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
            return {"rect": new_rect, "float_y": float(y), "timer": 0, "push_count": 0, "knockback": 0}
    return None

def render_to_screen():
    # 창 크기가 변해도 화면에 꽉 차게 늘려주는 렌더링 함수
    window_size = screen.get_size()
    scaled_surface = pygame.transform.scale(game_surface, window_size)
    screen.blit(scaled_surface, (0, 0))
    pygame.display.flip()

def main():
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 2)) for _ in range(80)]

    for i in range(3, 0, -1):
        # screen 대신 game_surface에 그림
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
    push_mode_timer = 0
    score_popups = [] 

    tilt_angle = 0  

    while True:
        clock.tick(FPS)
        game_surface.fill(GRAY) # 메인 게임 화면도 game_surface 초기화

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
        if item_spawn_timer >= 1000: 
            item_spawn_timer = 0
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

        # --- 그리기 영역 (screen 대신 game_surface에 그림) ---
        for s in stars: pygame.draw.circle(game_surface, WHITE, (s[0], s[1]), s[2])
        
        for it in items:
            game_surface.blit(item_img, (it["rect"].x, it["rect"].y))
            
        for b in bullets:
            pygame.draw.rect(game_surface, GREEN if b["type"]=="push" else YELLOW, b["rect"])
            
        for en in enemies:
            draw_enemy_sprite(game_surface, en["rect"], en["push_count"], enemy_img)
            
        if (invincible // 10) % 2 == 0: 
            rotated_player = pygame.transform.rotate(player_img, tilt_angle)
            new_player_rect = rotated_player.get_rect(center=player.center)
            game_surface.blit(rotated_player, new_player_rect.topleft)
            
        # HUD
        game_surface.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        game_surface.blit(font.render(f"Lives: {'♥ ' * lives}", True, RED), (WIDTH - 180, 10))
        if push_mode_timer > 0:
            msg = font.render(f"PUSH MODE: {push_mode_timer//60 + 1}s", True, GREEN)
            game_surface.blit(msg, (WIDTH//2 - 70, 10))
            
        for p in score_popups[:]:
            game_surface.blit(font_small.render(p["text"], True, YELLOW), (p["x"], p["y"]))
            p["y"] -= 1; p["life"] -= 1
            if p["life"] <= 0: score_popups.remove(p)

        # 다 그린 도화지를 창 크기에 맞게 렌더링
        render_to_screen()

def game_over_screen(score):
    game_surface.fill((10, 10, 30))
    game_surface.blit(font_big.render("GAME OVER", True, RED), (220, 220))
    game_surface.blit(font.render(f"Final Score: {score}", True, WHITE), (330, 310))
    game_surface.blit(font.render("Press R to Restart or Q to Quit", True, WHITE), (230, 370))
    render_to_screen()
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()