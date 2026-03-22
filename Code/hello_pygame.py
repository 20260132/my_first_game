import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My First Pygame")

clock = pygame.time.Clock()

# ✅ 원의 위치
x = 30
y = 570
speed = 5  # 이동 속도
radius = 20

# 적 추가하기 
enemy_x = 400
enemy_y = 300
enemy_speed = 7
enemy_move_delay = 5
frame_count = 0

# ✅ 반투명 레이어 (잔상용)
trail_surface = pygame.Surface((800, 600))
trail_surface.set_alpha(40)  # 숫자 ↓ = 더 오래 잔상 남음
trail_surface.fill((255, 0, 0))

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ✅ 키 입력 받기 (WASD)
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_w]:
        y -= speed
    if keys[pygame.K_s]:
        y += speed
    if keys[pygame.K_a]:
        x -= speed
    if keys[pygame.K_d]:
        x += speed

    # ✅ 플레이어 따라오기
    frame_count += 1

# ✅ 일정 프레임마다만 이동(적)
    if frame_count % enemy_move_delay == 0:
        if enemy_x < x:
            enemy_x += enemy_speed
        if enemy_x > x:
            enemy_x -= enemy_speed
        if enemy_y < y:
            enemy_y += enemy_speed
        if enemy_y > y:
            enemy_y -= enemy_speed

# ✅ 화면 밖 못 나가게 제한
    if x < radius:
        x = radius
    if x > 800 - radius:
        x = 800 - radius
    if y < radius:
        y = radius
    if y > 600 - radius:
        y = 600 - radius
        
    screen.blit(trail_surface, (0, 0))
    
    for i in range(8):
        pygame.draw.circle(screen, (0, 100, 255), (x, y), radius - 10 + i*2, 1)
    
    # 본체
    pygame.draw.circle(screen, (0, 150, 255), (x, y), radius)
    # 테두리
    pygame.draw.circle(screen, (200, 0, 0), (x, y), radius - 10, 2)

    #적 
    pygame.draw.circle(screen, (0, 50, 50), (enemy_x, enemy_y), 15)
    
    pygame.display.flip()
    clock.tick(60)  # 부드럽게

pygame.quit()
sys.exit()
