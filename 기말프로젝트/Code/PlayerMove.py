import pygame
import sys
import os
import random  # 💡 코인이 3개의 차선 중 랜덤하게 나오게 하려고 추가!



# PyInstaller 에셋 경로 처리 함수
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



# 1. 게임 초기화
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Politician - Coin Collection")
clock = pygame.time.Clock()
FPS = 60

ROAD_H = 500

# --- 2. 에셋 로드 ---

# --- 2. 에셋 로드 ---
try:
    ROAD_W = 470
    
    # 1. 파일 경로 설정
    paths = {
        "bg1": resource_path(os.path.join("assets", "sprites", "2nd_back1.png")),
        "bg2": resource_path(os.path.join("assets", "sprites", "2nd_back2.png")),
        "char1": resource_path(os.path.join("assets", "sprites", "char1.png")),
        "char2": resource_path(os.path.join("assets", "sprites", "char2.png")),
        "gd1": resource_path(os.path.join("assets", "sprites", "1st_gd.png")),
        "gd2": resource_path(os.path.join("assets", "sprites", "1st_gd2.png")),
        "gd3": resource_path(os.path.join("assets", "sprites", "2nd_gd2.png")),
        "gd4": resource_path(os.path.join("assets", "sprites", "3rd_gd2.png")),
        "coin": resource_path(os.path.join("assets", "sprites", "coin.png"))
    }

    # 2. 이미지 로드 및 크기 조정
    bg_image1 = pygame.transform.scale(pygame.image.load(paths["bg1"]).convert(), (WIDTH, HEIGHT))
    bg_image2 = pygame.transform.scale(pygame.image.load(paths["bg2"]).convert(), (WIDTH, HEIGHT))
    
    char1 = pygame.transform.scale(pygame.image.load(paths["char1"]).convert_alpha(), (120, 160))
    char2 = pygame.transform.scale(pygame.image.load(paths["char2"]).convert_alpha(), (120, 160))
    
    gd_image1 = pygame.transform.scale(pygame.image.load(paths["gd1"]).convert_alpha(), (ROAD_W, HEIGHT))
    gd_image2 = pygame.transform.scale(pygame.image.load(paths["gd2"]).convert_alpha(), (ROAD_W, ROAD_H))
    gd_image_2nd = pygame.transform.scale(pygame.image.load(paths["gd3"]).convert_alpha(), (ROAD_W, ROAD_H))
    gd_image_3rd = pygame.transform.scale(pygame.image.load(paths["gd4"]).convert_alpha(), (ROAD_W, ROAD_H))
    # 길 이미지 로드할 때 같이 불러와
    people_img = pygame.transform.scale(pygame.image.load(resource_path(os.path.join("assets", "sprites", "people.png"))).convert_alpha(), (350, 720))
    people_img_flipped = pygame.transform.flip(people_img, True, False) # 좌우 반전

    # 3. Rect 및 기타 설정
    gd_rect1 = gd_image1.get_rect(centerx=WIDTH // 2)
    gd_rect2 = gd_image2.get_rect(centerx=WIDTH // 2)

    # 4. 코인 로드
    coin_sheet = pygame.image.load(paths["coin"]).convert_alpha()
    coin_w = coin_sheet.get_width() // 6
    coin_h = coin_sheet.get_height()
    coin_frames = [pygame.transform.scale(coin_sheet.subsurface((i * coin_w, 0, coin_w, coin_h)), (int(coin_w * 3), int(coin_h * 3))) for i in range(6)]

    print("✅ 모든 에셋 로드 완료!")

except Exception as e:
    print(f"🚨 에셋 로드 오류: {e}")
    pygame.quit()
    sys.exit()



# --- 3. 게임 변수 설정 ---

scroll_speed = 10
people_y = 0

current_road_image = gd_image2
flash_timer = 0  # 효과 유지 시간



# [그리기]
screen.blit(people_img, (50, int(people_y)))
screen.blit(people_img, (50, int(people_y + 720))) # 이어지게 하려면 2장을 겹쳐서 그려

bg1_y = 0               
bg2_y1 = HEIGHT         
bg2_y2 = HEIGHT * 2     


gd_y1 = 0                       
gd_y2 = HEIGHT                  
gd_y3 = HEIGHT + ROAD_H         
current_gd_image1 = gd_image1 
current_h1 = HEIGHT             



LANE_LEFT = 490
LANE_CENTER = 640
LANE_RIGHT = 790
lanes = [LANE_LEFT, LANE_CENTER, LANE_RIGHT]
current_lane_idx = 1


player_target_x = lanes[current_lane_idx]
player_x = player_target_x
player_y = 300 


anim_timer = 0
current_frame = char1
anim_speed = 10 


# 🌟 코인 시스템 변수
coins = []             # 화면에 존재하는 코인들의 [x, y] 위치를 담을 리스트
coin_spawn_timer = 0   # 코인 생성 타이머
coin_spawn_rate = 40  # 1.5배 자주 생성
coin_anim_timer = 0
coin_anim_speed = 5  # 숫자가 작을수록 코인이 빨리 돌아!
coin_frame_idx = 0
score = 0
start_ticks = pygame.time.get_ticks() 
limit_time = 80 
# 가장 확실한 픽셀 폰트 설정
# 추천하는 안전한 폰트 로드 방식
font_path = resource_path(os.path.join("assets", "Jersey10.ttf"))
font = pygame.font.Font(font_path, 30)
    

# --- 4. 메인 루프 ---
running = True
while running:
    
    # [시간 계산]
    elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
    remaining_time = max(0, limit_time - elapsed_time)
    if remaining_time <= 0: 
        running = False
    
    # [이벤트 처리]
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_a or event.key == pygame.K_LEFT) and current_lane_idx > 0:
                current_lane_idx -= 1
            elif (event.key == pygame.K_d or event.key == pygame.K_RIGHT) and current_lane_idx < 2:
                current_lane_idx += 1
            player_target_x = lanes[current_lane_idx]

    # [시간대별 길 교체 로직]
    new_road = None
    if remaining_time <= 20:
        if current_road_image != gd_image_3rd: flash_timer = 10 # 바뀔 때 10프레임 동안 효과
        new_road = gd_image_3rd
            
        # [메인 루프 내]
        people_y -= scroll_speed
        if people_y <= -720:
            people_y = 0    
    
    elif remaining_time <= 50:
        if current_road_image != gd_image_2nd: flash_timer = 10
        new_road = gd_image_2nd
    else:
        new_road = gd_image2
    current_road_image = new_road

    # 첫 화면 길 교체 (필요하다면)
    if remaining_time > 79:
        current_gd_image1 = gd_image1
    else:
        current_gd_image1 = current_road_image
        
    # [배경 및 길 스크롤 업데이트]
    bg1_y -= scroll_speed
    bg2_y1 -= scroll_speed
    bg2_y2 -= scroll_speed
    if bg2_y1 <= -HEIGHT: bg2_y1 = bg2_y2 + HEIGHT
    if bg2_y2 <= -HEIGHT: bg2_y2 = bg2_y1 + HEIGHT
        

    gd_y1 -= scroll_speed
    gd_y2 -= scroll_speed
    gd_y3 -= scroll_speed
    if gd_y1 <= -current_h1: 
        gd_y1 = gd_y3 + ROAD_H
        current_gd_image1 = gd_image2  
        current_h1 = ROAD_H  
    if gd_y2 <= -ROAD_H: gd_y2 = gd_y1 + ROAD_H
    if gd_y3 <= -ROAD_H: gd_y3 = gd_y2 + ROAD_H

        

    # [캐릭터 애니메이션]
    player_x += (player_target_x - player_x) * 0.4 
    anim_timer += 1
    if anim_timer >= anim_speed:
        anim_timer = 0
        current_frame = char2 if current_frame == char1 else char1


    # 🌟 [코인 생성]
    coin_spawn_timer += 1
    if coin_spawn_timer >= coin_spawn_rate:
        coin_spawn_timer = 0

        # 아래에서 올라오는 코인 딱 1개만 생성!
        spawn_x = random.choice(lanes)
        spawn_y = HEIGHT + 100 
        coins.append([spawn_x, spawn_y])
        

    # 🌟 [코인 애니메이션 프레임 업데이트]
    coin_anim_timer += 1
    if coin_anim_timer >= coin_anim_speed:
        coin_anim_timer = 0
        coin_frame_idx = (coin_frame_idx + 1) % 6 # 0~5 반복
        

    current_coin_img = coin_frames[coin_frame_idx]


    # 🌟 [코인 이동 및 충돌 판정] - 가장 안전한 방식
    player_rect = char1.get_rect(center=(int(player_x), int(player_y)))
    next_coins = [] 

    

    for c in coins:
        c[1] -= scroll_speed # 위로 이동
        

        # 1. 화면 밖으로 나가면 삭제 (next_coins에 담지 않음)
        if c[1] < -100:
            continue

            

        # 2. 플레이어와 충돌 판정

        # 여기서 사용된 current_coin_img는 위에서 이미 선언된 상태야
        coin_rect = current_coin_img.get_rect(center=(c[0], int(c[1])))
        if player_rect.colliderect(coin_rect):
            score += 10000 # 점수만 올리고 
            continue    # 이 코인은 next_coins에 추가하지 않음 (삭제 효과)

        # 3. 살아남은 코인만 새 리스트에 담기
        next_coins.append(c)

    coins = next_coins

    # --- 5. 화면 그리기 ---
    # [1] 배경 
    if bg1_y > -HEIGHT: screen.blit(bg_image1, (0, int(bg1_y)))
    screen.blit(bg_image2, (0, int(bg2_y1)))
    screen.blit(bg_image2, (0, int(bg2_y2)))

    

    # [2] 길 
    screen.blit(current_gd_image1, (gd_rect1.x, int(gd_y1)))
    screen.blit(current_road_image, (gd_rect2.x, int(gd_y2)))
    screen.blit(current_road_image, (gd_rect2.x, int(gd_y3)))

   # [5] 사람들 그리기 - 60초 경과(남은 시간 20초 이하)일 때만 그리기
    if remaining_time <= 20:
        # 왼쪽 (기본)
        screen.blit(people_img, (50, int(people_y)))
        screen.blit(people_img, (50, int(people_y + 720)))
        
        # 오른쪽 (좌우 반전된 이미지 사용)
        screen.blit(people_img_flipped, (900, int(people_y)))
        screen.blit(people_img_flipped, (900, int(people_y + 720)))    

    # 🌟 [3] 코인 그리기 (캐릭터 뒤, 길 위에 그려짐)

    # 캐릭터 그리기 직전에 추가
    current_coin_img = coin_frames[coin_frame_idx]
    for c in coins:
        # 코인의 중심(center)을 c[0], c[1]로 맞추고 그리기
        rect = current_coin_img.get_rect(center=(c[0], int(c[1])))
        screen.blit(current_coin_img, rect.topleft)


    # [4] 캐릭터 

    screen.blit(current_frame, player_rect.topleft)

    # [5] 펀딩 현황 및 시간 표시 (글자 크기를 줄이고 겹치지 않게 배치)
    funding_text = font.render(f"FUNDING: {score:,} / 1,000,000", True, (255, 255, 0))
    time_text = font.render(f"TIME: {int(remaining_time)}s", True, (255, 255, 255))
    
    # 펀딩은 왼쪽 위, 시간은 오른쪽 위로 깔끔하게 분리
    screen.blit(funding_text, (20, 20))
    screen.blit(time_text, (1100, 20))
    
    # [6] 화면 전환 효과
    if flash_timer > 0:
        flash_timer -= 1
        # 반투명한 흰색 혹은 검은색 사각형 생성
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200) # 투명도 (0~255)
        overlay.fill((255, 255, 255)) # 흰색 번쩍임
        screen.blit(overlay, (0, 0))
    
    
    pygame.display.flip()
    clock.tick(FPS)



pygame.quit()

sys.exit()