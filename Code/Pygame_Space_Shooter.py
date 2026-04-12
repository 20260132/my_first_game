import pygame
import random
import sys

pygame.init()

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

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter - Enhanced Push Mode")
clock = pygame.time.Clock()
font = get_korean_font(30)
font_big = get_korean_font(72)
font_small = get_korean_font(24)

PLAYER_W, PLAYER_H = 40, 40
ENEMY_W,  ENEMY_H  = 36, 36
BULLET_W, BULLET_H = 6,  14
ITEM_W,   ITEM_H   = 30, 30

SPAWN_RATE = 40
ENEMY_LIFETIME = 600 # 10초

def draw_player(surf, rect):
    cx = rect.centerx
    pygame.draw.polygon(surf, BLUE, [
        (cx, rect.top),
        (rect.left, rect.bottom),
        (cx, rect.bottom - 8),
        (rect.right, rect.bottom),
    ])
    pygame.draw.rect(surf, YELLOW, (cx - 4, rect.bottom - 10, 8, 10))

def draw_enemy(surf, rect, push_count):
    # 핵심 수정 4: 투명도 지원을 위해 별도의 Surface 생성 (SRCALPHA 사용)
    enemy_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    
    # 3번 맞으면 사라지므로, 한 번 맞을 때마다 투명도를 약 80씩 감소
    # 0(완전 투명) ~ 255(완전 불투명)
    alpha = max(40, 255 - (push_count * 80)) 
    
    # 맞은 횟수에 따른 색상 지정 (RGBA 사용)
    color = (220, 50, 50, alpha) # 빨간색 + 투명도
    if push_count == 1: color = (255, 140, 0, alpha) # 주황색 + 투명도
    elif push_count == 2: color = (240, 220, 0, alpha) # 노란색 + 투명도
    
    cx = rect.width // 2
    # enemy_surf 내부(좌표 0,0 기준)에 그리기
    pygame.draw.polygon(enemy_surf, color, [
        (cx, rect.height),
        (0, 0),
        (cx, 8),
        (rect.width, 0),
    ])
    
    # 메인 화면의 적 위치에 투명도가 적용된 Surface를 출력
    surf.blit(enemy_surf, (rect.x, rect.y))

def spawn_enemy(existing_enemies, player_rect):
    for _ in range(50):
        x = random.randint(0, WIDTH - ENEMY_W)
        y = random.randint(40, 300 - ENEMY_H) 
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

def main():
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

    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 2)) for _ in range(80)]

    while True:
        clock.tick(FPS)
        screen.fill(GRAY)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player.left > 0: player.x -= 6
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player.right < WIDTH: player.x += 6
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and player.top > 0: player.y -= 6
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player.bottom < HEIGHT: player.y += 6

        # 핵심 수정 1: 아이템 등장 주기 20초(1200 프레임)로 변경
        item_spawn_timer += 1
        if item_spawn_timer >= 1200: 
            item_spawn_timer = 0
            ix = random.randint(50, WIDTH - 50)
            iy = -ITEM_H
            items.append({"rect": pygame.Rect(ix, iy, ITEM_W, ITEM_H), "float_y": float(iy)})

        # 핵심 수정 2: 아이템 하강 속도 상향 (1.2 -> 2.5)
        for it in items[:]:
            it["float_y"] += 2.5
            it["rect"].y = int(it["float_y"])
            if player.colliderect(it["rect"]):
                push_mode_timer = 420 
                items.remove(it)
            elif it["rect"].top > HEIGHT:
                items.remove(it)

        if push_mode_timer > 0: push_mode_timer -= 1

        shoot_cd -= 1
        if keys[pygame.K_SPACE] and shoot_cd <= 0:
            b_type = "push" if push_mode_timer > 0 else "normal"
            bullets.append({"rect": pygame.Rect(player.centerx - 3, player.top, 6, 14), "type": b_type})
            shoot_cd = 15

        for b in bullets[:]:
            b["rect"].y -= 10
            if b["rect"].bottom < 0: bullets.remove(b)

        spawn_timer += 1
        if spawn_timer >= SPAWN_RATE:
            spawn_timer = 0
            new_en = spawn_enemy(enemies, player)
            if new_en: enemies.append(new_en)

        # 핵심 수정 3: 밀쳐지는 거리 및 속도 강화
        for en in enemies[:]:
            en["timer"] += 1
            if en["timer"] > ENEMY_LIFETIME:
                enemies.remove(en)
                continue
            
            if en["knockback"] > 0:
                en["float_y"] -= 1.5 # 밀려나는 속도 강화 (기존 1.0)
                en["knockback"] -= 1
            else:
                en["float_y"] += 0.3 
            en["rect"].y = int(en["float_y"])

        # 충돌 판정 (총알 vs 적)
        for b in bullets[:]:
            for en in enemies[:]:
                if b["rect"].colliderect(en["rect"]):
                    if b in bullets: bullets.remove(b)
                    if b["type"] == "normal":
                        enemies.remove(en)
                        score += 10
                    else: 
                        en["push_count"] += 1
                        en["knockback"] = 25 # 밀려나는 프레임 강화 (기존 15)
                        score += 10
                        if en["push_count"] >= 3:
                            enemies.remove(en)
                    break

        # 연쇄 충돌 판정
        for i, en1 in enumerate(enemies):
            if en1["knockback"] > 0:
                for j, en2 in enumerate(enemies):
                    if i != j and en1["rect"].colliderect(en2["rect"]) and en2["knockback"] == 0:
                        en2["knockback"] = 25 # 연쇄 밀치기도 강화
                        en2["push_count"] += 1
                        score += 20 
                        score_popups.append({"text": "+20", "x": en2["rect"].x, "y": en2["rect"].y, "life": 30})
                        if en2["push_count"] >= 3:
                            if en2 in enemies: enemies.remove(en2)
                        break

        # 플레이어 피격
        if invincible > 0: invincible -= 1
        else:
            for en in enemies:
                if player.colliderect(en["rect"]):
                    lives -= 1
                    invincible = 90
                    enemies.clear()
                    if lives <= 0:
                        if game_over_screen(score): main()
                        return
                    break

        # 그리기
        for s in stars: pygame.draw.circle(screen, WHITE, (s[0], s[1]), s[2])
        for it in items:
            pygame.draw.rect(screen, GREEN, it["rect"])
            pygame.draw.rect(screen, WHITE, it["rect"].inflate(-12, -12))
        for b in bullets:
            pygame.draw.rect(screen, GREEN if b["type"]=="push" else YELLOW, b["rect"])
        for en in enemies:
            draw_enemy(screen, en["rect"], en["push_count"])
        if (invincible // 10) % 2 == 0: draw_player(screen, player)
        
        # HUD
        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Lives: {'♥ ' * lives}", True, RED), (WIDTH - 180, 10))
        if push_mode_timer > 0:
            msg = font.render(f"PUSH MODE: {push_mode_timer//60 + 1}s", True, GREEN)
            screen.blit(msg, (WIDTH//2 - 70, 10))
            
        for p in score_popups[:]:
            screen.blit(font_small.render(p["text"], True, YELLOW), (p["x"], p["y"]))
            p["y"] -= 1; p["life"] -= 1
            if p["life"] <= 0: score_popups.remove(p)

        pygame.display.flip()

def game_over_screen(score):
    screen.fill((10, 10, 30))
    screen.blit(font_big.render("GAME OVER", True, RED), (220, 220))
    screen.blit(font.render(f"Final Score: {score}", True, WHITE), (330, 310))
    screen.blit(font.render("Press R to Restart or Q to Quit", True, WHITE), (230, 370))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()