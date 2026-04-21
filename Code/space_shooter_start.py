import pygame
import sys
import random

# 파일 이름에 맞춰서 불러옵니다.
import space_shooter_main as game 

def get_scaled_mouse_pos():
    """창 크기를 늘리거나 줄였을 때, 마우스 좌표를 가상 도화지(800x600) 비율에 맞춰줍니다."""
    mouse_x, mouse_y = pygame.mouse.get_pos()
    window_w, window_h = game.screen.get_size()
    
    scale_x = game.WIDTH / window_w
    scale_y = game.HEIGHT / window_h
    
    return (mouse_x * scale_x, mouse_y * scale_y)

def get_title_font(size):
    """게임 제목용으로 더 멋지고 굵은 영문 폰트를 찾습니다."""
    candidates = ["impact", "arialblack", "segoeui", "malgungothic"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return game.get_korean_font(size)

def show_help():
    """게임 설명 버튼을 눌렀을 때 나오는 화면입니다."""
    title_font = game.get_korean_font(50)
    text_font = game.get_korean_font(28) # 문구가 길어져서 폰트 크기를 살짝 줄였습니다.
    
    # 돌아가기 버튼
    back_btn_rect = pygame.Rect(game.WIDTH // 2 - 100, game.HEIGHT - 100, 200, 60)

    while True:
        game.clock.tick(game.FPS)
        game.game_surface.fill((20, 30, 50)) # 약간 푸른빛이 도는 어두운 배경

        mx, my = get_scaled_mouse_pos()
        is_hovering_back = back_btn_rect.collidepoint((mx, my))

        # --- 수정: 블랙홀 전략 요소 문구 업데이트 및 간격 조정 ---
        texts = [
            ("게임 설명", title_font, game.YELLOW, game.HEIGHT // 6),
            ("이동: 방향키 또는 W, A, S, D", text_font, game.WHITE, game.HEIGHT // 3),
            ("발사: SPACE BAR", text_font, game.WHITE, game.HEIGHT // 3 + 50),
            ("아이템 획득 시 7초간 적을 밀쳐내는 PUSH MODE 발동!", text_font, game.GREEN, game.HEIGHT // 3 + 110),
            ("경고: 본인 우주선이 블랙홀에 빠지면 즉시 게임 오버!", text_font, game.RED, game.HEIGHT // 3 + 170),
            ("적 우주선이 블랙홀에 빠지지 않게 하세요! (얻을 수 있는 점수 소멸)", text_font, game.ORANGE, game.HEIGHT // 3 + 220)
        ]

        for text, font_obj, color, y_pos in texts:
            rendered = font_obj.render(text, True, color)
            rect = rendered.get_rect(center=(game.WIDTH // 2, y_pos))
            game.game_surface.blit(rendered, rect)

        # 돌아가기 버튼 그리기
        btn_color = (255, 200, 50) if is_hovering_back else (200, 150, 30)
        pygame.draw.rect(game.game_surface, btn_color, back_btn_rect, border_radius=15)
        
        back_text = text_font.render("돌아가기", True, game.BLACK)
        back_text_rect = back_text.get_rect(center=back_btn_rect.center)
        game.game_surface.blit(back_text, back_text_rect)

        game.render_to_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if is_hovering_back:
                    return  # 함수를 종료하여 다시 메인 메뉴 루프로 돌아감
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

def show_menu():
    title_font = get_title_font(90) # 제목용 특수 폰트
    btn_font = get_title_font(35)   # 버튼용 폰트
    korean_btn_font = game.get_korean_font(30)
    
    # 두 개의 버튼을 나란히 배치
    start_btn_rect = pygame.Rect(game.WIDTH // 2 - 220, game.HEIGHT // 2 + 50, 200, 70)
    help_btn_rect = pygame.Rect(game.WIDTH // 2 + 20, game.HEIGHT // 2 + 50, 200, 70)
    
    stars = [(random.randint(0, game.WIDTH), random.randint(0, game.HEIGHT), random.randint(1, 2)) for _ in range(80)]

    while True:
        game.clock.tick(game.FPS)
        game.game_surface.fill(game.GRAY)

        for s in stars:
            pygame.draw.circle(game.game_surface, game.WHITE, (s[0], s[1]), s[2])

        mx, my = get_scaled_mouse_pos()
        is_hovering_start = start_btn_rect.collidepoint((mx, my))
        is_hovering_help = help_btn_rect.collidepoint((mx, my))

        # 게임 제목
        title_text = title_font.render("NOVA BLASTER", True, game.WHITE)
        title_rect = title_text.get_rect(center=(game.WIDTH // 2, game.HEIGHT // 3 - 20))
        
        # 제목 그림자 효과
        shadow_text = title_font.render("NOVA BLASTER", True, game.BLACK)
        game.game_surface.blit(shadow_text, (title_rect.x + 4, title_rect.y + 4))
        game.game_surface.blit(title_text, title_rect)

        # 1. 스타트 버튼
        start_color = (255, 60, 60) if is_hovering_start else (180, 30, 30)
        pygame.draw.rect(game.game_surface, start_color, start_btn_rect, border_radius=15)
        start_text = btn_font.render("START", True, game.WHITE)
        game.game_surface.blit(start_text, start_text.get_rect(center=start_btn_rect.center))

        # 2. 게임 설명 버튼
        help_color = (60, 220, 80) if is_hovering_help else (40, 160, 50)
        pygame.draw.rect(game.game_surface, help_color, help_btn_rect, border_radius=15)
        help_text = korean_btn_font.render("게임 설명", True, game.WHITE)
        game.game_surface.blit(help_text, help_text.get_rect(center=help_btn_rect.center))

        game.render_to_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if is_hovering_start:
                    game.main() # 게임 시작
                elif is_hovering_help:
                    show_help() # 게임 설명 화면으로 이동

if __name__ == "__main__":
    show_menu()