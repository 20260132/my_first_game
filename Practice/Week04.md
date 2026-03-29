# week 4 실습 기록

## 목표, 오늘 한 것
[WASD로 플레이어 움직이게 구현, 회전하는 적 구현, AABB, 원형 충돌, OBB 충돌 Bounding Box 구현]

## AI 대화 기록
**Q1. WASD로 움직일 때 코드 앞에 왜 K가 붙는거야?**
--> AI 답변 :
    pygame 내부에서 키보드 키를 상수로 정의했기 때문이다.
    ex) pygame.K.w --> K = Key(키보드 키), w = 실제 키 이름
    왜 그냥 w로 안쓰는가?
        pygame.key.get_pressed()는 문자열이 아니라 키 코드값으로 반환하기 때문.
궁금증 해결됐나? : Yes


**Q2. Thonny에 폴더를 생성해주고, 스프라이트를 넣을 건데 나를 "adventurer"로 해주고, 적을 "sword"로 해줘** 
--> AI 답변 :
    Thonny 위쪽 메뉴에서 View를 클릭하고 우클릭 -> New directory -> 이름 : sprites로 하면 폴더가 생성되고, 그 폴더에 스프라이트 이름을 adventurer, sword로 설정한 후에 
    player_img = pygame.image.load("sprites/adventurer.png")
    enemy_img = pygame.image.load("sprites/sword.png") 를 삽입해준다.
적용 결과 : 넣은 스프라이트로 사진이 변경되었다.


**Q3. AABB와 OBB에 관해 정의를 알려주고, 회전시에 어떤 차이가 있는 지 알려줘**
--> AI 답변 :
    AABB는 축에 정렬된 경계 상자로, 화면의 가로/세로 축에 평행한 사각형임.
    특징은 회전하지 않고, 계산이 빠르며, 정확도가 떨어짐.
    OBB는 방향이 있는 경계 상자로, 객체의 회전에 맞춰 같이 회전하는 사각형임.
    특징은 회전하고, 계산이 느리며, 정확도가 높음.
    둘은 회전시에 AABB같은 경우 객체가 회전하면 더 커지지만, OBB 같은 경우 객체가 회전하면 같이 회전한다. 따라서 게임에서는 AABB를 먼저 검사하고, 충돌 가능 시 OBB를 검사한다.
결과 : AABB와 OBB의 차이를 알게 됨.



## 시행착오와 해결과정
A. 처음에는 AABB만 사용했었는데 회전할수록 충돌 범위가 커지는 문제가 발생했다.
이때는 회전을 고려하지 않는 사각형인 AABB이기 때문이었다.
--> 회전을 반영해주는 OBB 방식을 추가로 구현함으로써 해결하였다.
B. 처음에는 x,y를 기준으로 원형 충돌을 계산하려고 했었음
그래서 충돌 위치가 이상하게 나타났고, 원 위치가 어긋났음. 중심 좌표 기준이 아닌 좌측 상단 기준으로 계산하여 오류가 났었음
--> player_center = player_rect.center로 해서 중심 좌표를 계산함.


## 어려웠던 점
A. pygame에서 rect 객체를 직접 회전하려고 했지만 회전 기능이 없었음.
--> surface를 생성하고 pygame.transform.rotate()를 사용해 회전시킴.


## 배운 점
A. math.radians(enemy_angle) 에서 각도를 라디안 값으로 바꾸는 코드로, 삼각함수를 사용한다는 걸 알게 됨.
B. pygame.transform.rotate(surface, enemy_angle)에서 객체를 회전시키는 코드로, rect가 아닌 surface를 회전해야 된다는 점을 배움.
