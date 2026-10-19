# RUIN - Pygame game (ROLAND SAN)
# INSTRUCTION: Shoot down the targets and score as much as possible within 60 seconds.
# INSPIRED BY DUCKHUNT, DOOM, AND OTHER SHOOTING GAMES
import pygame
import math
import os

pygame.init()

fps = 60
timer = pygame.time.Clock()

WIDTH = 800  # WIDTH OF GAME
HEIGHT = 600  # HEIGHT OF GAME
TIME_LIMIT = 60  

font = pygame.font.Font(None, 24)
bgs = []  # backgrounds of each level
target_imgs = [[], [], []]
targets = {  # number of targets of each type on each level
    1: [4, 5, 6],
    2: [10, 8, 6],
    3: [15, 12, 8, 5]
}

level = 0
points = 0
shot = False
menu = True
game_over = False
clicked = False
new_coords = True

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('RUIN')


def load_image(path, size=None):
    image = pygame.image.load(path).convert_alpha()
    if size is not None:
        image = pygame.transform.scale(image, size)
    return image

font = pygame.font.Font('assets/INVASION2000.TTF', 36)
menu_img = load_image('assets/menu/menu.png', (WIDTH, HEIGHT))
game_over_img = load_image('assets/menu/gameover.png', (WIDTH, HEIGHT))
replay_btn = load_image('assets/replaybtn.png', (160, 42))
start_btn = load_image('assets/startbtn.png', (160, 42))
shot_img = load_image('assets/middle_fired.png', (WIDTH, HEIGHT))
guns = load_image('assets/middle.png', (WIDTH, HEIGHT))
banner = load_image('assets/POINTS.png', (WIDTH, 100))

shot_sound = None
if os.path.exists('assets/pistol_shot.mp3'):
    try:
        shot_sound = pygame.mixer.Sound('assets/pistol_shot.mp3')
    except pygame.error:
        pass
if os.path.exists('assets/DOOM_OST.mp3'):
    try:
        pygame.mixer.music.load('assets/DOOM_OST.mp3')
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

# background and target loading
for i in range(1, 4):
    bgs.append(load_image(f'assets/bgs/{i}.png', (WIDTH, HEIGHT)))
    if i < 3:
        for j in range(1, 4):
            target_imgs[i - 1].append(
                load_image(f'assets/targets/{i}/{j}.png',
                           (120 - (j * 18), 80 - (j * 12)))
            )
    elif i == 3:
        for j in range(1, 5):
            target_imgs[i - 1].append(
                load_image(f'assets/targets/{i}/{j}.png',
                           (120 - (j * 18), 80 - (j * 12)))
            )

time_remaining = 0
counter = 1
one_coords = [[], [], []]  # 3 tiers
two_coords = [[], [], []]  # 3 tiers
three_coords = [[], [], [], []]  # 4 tiers


def draw_score():  # Timer and score on UI
    points_text = font.render(f'{points}', True, pygame.Color('WHITE'))
    screen.blit(points_text, (100, 530))
    mode_text = font.render(f'Timer: {time_remaining:.2f}', True, pygame.Color('WHITE'), pygame.Color('BLACK'))
    screen.blit(mode_text, (520, 530))


def draw_gun():  # gun on screen
    mouse_pos = pygame.mouse.get_pos()
    lasers = 'red'
    if shot:
        pygame.draw.circle(screen, lasers, mouse_pos, 5)
        screen.blit(shot_img, (0, 0))


def movement_level(coords):  # movement of targets according to level
    if level == 1 or level == 2:
        max_val = 3
    else:
        max_val = 4
    for i in range(max_val):
        for j in range(len(coords[i])):
            my_coords = coords[i][j]
            if my_coords[0] < -150:
                coords[i][j] = (WIDTH, my_coords[1])
            else:
                coords[i][j] = (my_coords[0] - 2 ** i, my_coords[1])
    return coords


def draw_level(coords):  # the placement of targets depending on level
    if level == 1 or level == 2:
        target_rects = [[], [], []]
    else:
        target_rects = [[], [], [], []]
    for i in range(len(coords)):
        for j in range(len(coords[i])):
            image = target_imgs[level - 1][i]
            rect = pygame.Rect(coords[i][j][0], coords[i][j][1],
                               image.get_width(), image.get_height())
            target_rects[i].append(rect)
            screen.blit(image, coords[i][j])
    return target_rects


def check_shot(targets_rect, coords):  # checking whether the shot is hit or not
    global points
    mouse_pos = pygame.mouse.get_pos()
    for i in range(len(targets_rect)):
        # Work backwards so removing a target does not skip the next target.
        for j in range(len(targets_rect[i]) - 1, -1, -1):
            if targets_rect[i][j].collidepoint(mouse_pos):
                coords[i].pop(j)  # if hit, remove
                points += 10 + 10 * i  # points: 10, 20, 30, 40
                return coords  # one demon per shot
    return coords


def draw_menu():  # menu pop-up
    global game_over, level, menu, points
    global time_remaining, clicked, new_coords, counter
    game_over = False
    screen.blit(menu_img, (0, 0))
    btn_start = screen.blit(start_btn, (320, 480))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    if btn_start.collidepoint(mouse_pos) and clicks[0] and not clicked:
        level = 1
        menu = False
        time_remaining = TIME_LIMIT
        points = 0
        counter = 1
        clicked = True
        new_coords = True
    elif not clicks[0]:
        clicked = False


def draw_game_over():  # gameover pop-up
    global game_over, level, menu, points
    global time_remaining, clicked, new_coords
    game_over = True
    screen.blit(game_over_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    btn_replay = screen.blit(replay_btn, (320, 480))
    text = font.render(f'POINTS : {points}', True, pygame.Color('WHITE'))
    screen.blit(text, (20, 20))
    if btn_replay.collidepoint(mouse_pos) and clicks[0] and not clicked:
        level = 0
        game_over = False
        menu = True
        points = 0
        time_remaining = 0
        clicked = True
        new_coords = True
    elif not clicks[0]:
        clicked = False


run = True
while run:
    timer.tick(fps)
    # Use elapsed time rather than decrementing a counter every 60 frames.
    dt = timer.get_time() / 1000.0
    if level != 0 and not game_over:
        time_remaining = max(0, time_remaining - dt)

    if new_coords and level > 0:
        # initialize enemy coordinates
        one_coords = [[], [], []]
        two_coords = [[], [], []]
        three_coords = [[], [], [], []]
        for i in range(3):
            my_list = targets[1]
            for j in range(my_list[i]):
                one_coords[i].append((WIDTH // my_list[i] * j,
                                      300 - (i * 150) + 30 * (j % 2)))
        for i in range(3):
            my_list = targets[2]
            for j in range(my_list[i]):
                two_coords[i].append((WIDTH // my_list[i] * j,
                                      300 - (i * 150) + 30 * (j % 2)))
        for i in range(4):
            my_list = targets[3]
            for j in range(my_list[i]):
                three_coords[i].append((WIDTH // my_list[i] * j,
                                        300 - (i * 100) + 30 * (j % 2)))
        new_coords = False

    screen.fill('black')
    if level > 0:
        screen.blit(bgs[level - 1], (0, 0))
        screen.blit(banner, (0, HEIGHT - 100))
        screen.blit(guns, (0, 0))

    if menu:
        level = 0
        draw_menu()
    elif game_over:
        level = 0
        draw_game_over()
    else:
        if level == 1:
            target_rec = draw_level(one_coords)
            one_coords = movement_level(one_coords)
        elif level == 2:
            target_rec = draw_level(two_coords)
            two_coords = movement_level(two_coords)
        elif level == 3:
            target_rec = draw_level(three_coords)
            three_coords = movement_level(three_coords)
        draw_gun()
        draw_score()

    # Process clicks once per frame; shots only count inside the play area.
    shot = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_position = event.pos
            if level > 0 and 0 < mouse_position[0] < WIDTH and 0 < mouse_position[1] < HEIGHT - 100:
                shot = True
                if shot_sound is not None:
                    shot_sound.play()
                # Collision happens immediately, against the sprites drawn this frame.
                if level == 1:
                    one_coords = check_shot(target_rec, one_coords)
                elif level == 2:
                    two_coords = check_shot(target_rec, two_coords)
                elif level == 3:
                    three_coords = check_shot(target_rec, three_coords)

    if level > 0:
        if level == 1 and not any(one_coords):
            level += 1
        elif level == 2 and not any(two_coords):
            level += 1
        elif (level == 3 and not any(three_coords)) or time_remaining <= 0:
            game_over = True
            level = 0

    pygame.display.flip()

pygame.quit()
