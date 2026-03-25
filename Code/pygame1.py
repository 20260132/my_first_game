import pygame
import sys
import math

pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AABB + Circle + OBB")

clock = pygame.time.Clock()

# 색상
GRAY = (150, 150, 150)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# 플레이어 설정
player_size = 50
player_x = 100
player_y = 100
player_speed = 5

# 적 설정
enemy_size = 50
enemy_x = WIDTH // 2 - enemy_size // 2
enemy_y = HEIGHT // 2 - enemy_size // 2

# 회전 변수
enemy_angle = 0
rotation_speed = 1

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    # WASD 이동
    if keys[pygame.K_a]:
        player_x -= player_speed
    if keys[pygame.K_d]:
        player_x += player_speed
    if keys[pygame.K_w]:
        player_y -= player_speed
    if keys[pygame.K_s]:
        player_y += player_speed

    # Z 키로 회전 속도 증가
    if keys[pygame.K_z]:
        rotation_speed = 3
    else:
        rotation_speed = 1

    # 적 회전
    enemy_angle += rotation_speed

    # Rect 생성
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_size, enemy_size)

    # 중심 좌표
    player_center = player_rect.center
    enemy_center = enemy_rect.center

    # 반지름
    player_radius = player_size // 2
    enemy_radius = enemy_size // 2

    # 원형 충돌 감지
    distance = math.sqrt(
        (player_center[0] - enemy_center[0]) ** 2 +
        (player_center[1] - enemy_center[1]) ** 2
    )

    circle_collision = distance < (player_radius + enemy_radius)

    # 배경색 변경
    if circle_collision:
        screen.fill(YELLOW)
    else:
        screen.fill(WHITE)

    # 플레이어 그리기
    pygame.draw.rect(screen, GRAY, player_rect)

    # -------- 회전 적 그리기 --------
    surface = pygame.Surface((enemy_size, enemy_size), pygame.SRCALPHA)
    pygame.draw.rect(surface, GRAY, (0, 0, enemy_size, enemy_size))

    rotated_surface = pygame.transform.rotate(surface, enemy_angle)
    rotated_rect = rotated_surface.get_rect(center=enemy_center)

    screen.blit(rotated_surface, rotated_rect.topleft)

    # AABB 표시
    pygame.draw.rect(screen, RED, player_rect, 2)
    pygame.draw.rect(screen, RED, rotated_rect, 2)

    # 원형 바운더리 표시
    pygame.draw.circle(screen, BLUE, player_center, player_radius, 2)
    pygame.draw.circle(screen, BLUE, enemy_center, enemy_radius, 2)

    # -------- OBB 계산 --------
    w, h = enemy_size, enemy_size
    cx, cy = enemy_center

    rad = math.radians(enemy_angle)

    corners = [
        (-w/2, -h/2),
        ( w/2, -h/2),
        ( w/2,  h/2),
        (-w/2,  h/2)
    ]

    obb_points = []

    for x, y in corners:
        rx = x * math.cos(rad) - y * math.sin(rad)
        ry = x * math.sin(rad) + y * math.cos(rad)

        obb_points.append((cx + rx, cy + ry))

    pygame.draw.polygon(screen, GREEN, obb_points, 2)

    pygame.display.update()
    clock.tick(60)