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
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()
font = get_korean_font(36)
font_big = get_korean_font(72)

PLAYER_W, PLAYER_H = 40, 40
ENEMY_W,  ENEMY_H  = 36, 36
BULLET_W, BULLET_H = 6,  14

# 고정 스폰 속도
SPAWN_RATE = 40
# 적 수명 (60 FPS 기준 300 프레임 = 5초)
ENEMY_LIFETIME = 300

def draw_player(surf, rect):
    cx = rect.centerx
    pygame.draw.polygon(surf, BLUE, [
        (cx, rect.top),
        (rect.left, rect.bottom),
        (cx, rect.bottom - 8),
        (rect.right, rect.bottom),
    ])
    pygame.draw.rect(surf, YELLOW, (cx - 4, rect.bottom - 10, 8, 10))

def draw_enemy(surf, rect):
    cx = rect.centerx
    pygame.draw.polygon(surf, RED, [
        (cx, rect.bottom),
        (rect.left, rect.top),
        (cx, rect.top + 8),
        (rect.right, rect.top),
    ])

def spawn_enemy(existing_enemies, player_rect):
    for _ in range(50):
        x = random.randint(0, WIDTH - ENEMY_W)
        # 상단 300 픽셀 이내에만 생성 (UI 영역 40은 제외)
        y = random.randint(40, 300 - ENEMY_H) 
        new_rect = pygame.Rect(x, y, ENEMY_W, ENEMY_H)
        
        # 1. 플레이어와 안전 거리 확보
        if new_rect.colliderect(player_rect.inflate(100, 100)):
            continue
            
        # 2. 기존 적들과 겹치는지 확인 (이제 딕셔너리로 관리되므로 ["rect"] 확인)
        overlap = False
        for en in existing_enemies:
            if new_rect.colliderect(en["rect"]):
                overlap = True
                break
                
        # 겹치지 않으면 딕셔너리 형태로 정보 반환 (수명과 부드러운 이동을 위한 실수 Y좌표 포함)
        if not overlap:
            return {"rect": new_rect, "float_y": float(y), "timer": 0}
            
    return None

def draw_stars(stars):
    for s in stars:
        pygame.draw.circle(screen, WHITE, (s[0], s[1]), s[2])

def draw_hud(score, lives):
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Lives: {'♥ ' * lives}", True, RED), (WIDTH - 180, 10))

def game_over_screen(score):
    screen.fill((10, 10, 30))
    screen.blit(font_big.render("GAME OVER", True, RED), (220, 220))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (350, 310))
    screen.blit(font.render("R: Restart   Q: Quit", True, WHITE), (270, 360))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: pygame.quit(); sys.exit()

def main():
    player = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 70, PLAYER_W, PLAYER_H)
    bullets  = []
    enemies  = []  # 이제 Rect가 아닌 딕셔너리를 저장합니다.
    score    = 0
    lives    = 3
    shoot_cd = 0
    spawn_timer = 0
    invincible = 0

    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 2))
             for _ in range(80)]

    while True:
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        
        if (keys[pygame.K_LEFT] or keys[pygame.K_a])  and player.left  > 0:      player.x -= 6
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player.right < WIDTH:  player.x += 6
        if (keys[pygame.K_UP] or keys[pygame.K_w])    and player.top   > 0:      player.y -= 6
        if (keys[pygame.K_DOWN] or keys[pygame.K_s])  and player.bottom < HEIGHT: player.y += 6

        shoot_cd -= 1
        if keys[pygame.K_SPACE] and shoot_cd <= 0:
            b = pygame.Rect(player.centerx - BULLET_W // 2, player.top, BULLET_W, BULLET_H)
            bullets.append(b)
            shoot_cd = 15

        bullets = [b for b in bullets if b.bottom > 0]
        for b in bullets:
            b.y -= 10

        # 적 스폰
        spawn_timer += 1
        if spawn_timer >= SPAWN_RATE:
            spawn_timer = 0
            new_enemy = spawn_enemy(enemies, player)
            if new_enemy:
                enemies.append(new_enemy)

        # 적 업데이트 로직 (아주 천천히 하강 + 5초 지나면 삭제)
        alive_enemies = []
        for en in enemies:
            en["timer"] += 1
            if en["timer"] <= ENEMY_LIFETIME: # 5초가 안 지난 적만 유지
                en["float_y"] += 0.3 # 매 프레임 0.3 픽셀씩 아주 천천히 하강
                en["rect"].y = int(en["float_y"])
                alive_enemies.append(en)
        enemies = alive_enemies

        # 총알과 적 충돌 판정
        hit_bullets = set()
        hit_enemies = set()
        for bi, b in enumerate(bullets):
            for ei, en in enumerate(enemies):
                expanded = en["rect"].inflate(6,6)
                if b.colliderect(expanded):
                    hit_bullets.add(bi)
                    hit_enemies.add(ei)
                    score += 10
        bullets  = [b  for i, b  in enumerate(bullets)  if i not in hit_bullets]
        enemies  = [en for i, en in enumerate(enemies)   if i not in hit_enemies]

        # 플레이어와 적 충돌 판정
        if invincible > 0:
            invincible -= 1
        else:
            for en in enemies:
                if player.colliderect(en["rect"]):
                    lives -= 1
                    invincible = 90
                    enemies.clear()
                    if lives <= 0:
                        if game_over_screen(score):
                            main()
                        return
                    break

        screen.fill(GRAY)
        draw_stars(stars)

        for b in bullets:
            pygame.draw.rect(screen, YELLOW, b)

        # 딕셔너리의 "rect" 값을 전달하여 그리기
        for en in enemies:
            draw_enemy(screen, en["rect"])

        blink = (invincible // 10) % 2 == 0
        if blink:
            draw_player(screen, player)

        draw_hud(score, lives)
        pygame.display.flip()

if __name__ == "__main__":
    main()