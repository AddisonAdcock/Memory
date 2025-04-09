import os
import random
import pygame

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Memory")

clock = pygame.time.Clock()

ORIG_CARD_WIDTH, ORIG_CARD_HEIGHT = 72, 96
scale_factor = 1.5
CARD_WIDTH = int(ORIG_CARD_WIDTH * scale_factor)
CARD_HEIGHT = int(ORIG_CARD_HEIGHT * scale_factor)

GRID_COLS, GRID_ROWS = 4, 4
card_gap = 5
ANIMATION_DURATION = 1000

CARD_DIR = "cards"
card_images = {}

ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
suits = ['C', 'D', 'H', 'S']

for suit in suits:
    for rank in ranks:
        card_key = rank + suit
        image_path = os.path.join(CARD_DIR, f"{card_key}.png")
        if os.path.exists(image_path):
            image = pygame.image.load(image_path).convert_alpha()
            image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
            card_images[card_key] = image
        else:
            print(f"Warning: {image_path} not found!")

back_image_path = os.path.join(CARD_DIR, "back.png")
if os.path.exists(back_image_path):
    back_image = pygame.image.load(back_image_path).convert_alpha()
    back_image = pygame.transform.scale(back_image, (CARD_WIDTH, CARD_HEIGHT))
    card_images["back"] = back_image
else:
    print(f"Warning: {back_image_path} not found!")

TOTAL_CARDS = GRID_COLS * GRID_ROWS
PAIR_COUNT = TOTAL_CARDS // 2

available_cards = list(card_images.keys())
if "back" in available_cards:
    available_cards.remove("back")
selected_cards = random.sample(available_cards, PAIR_COUNT)
cards_for_game = selected_cards * 2
random.shuffle(cards_for_game)

grid_width = GRID_COLS * CARD_WIDTH + (GRID_COLS - 1) * card_gap
grid_height = GRID_ROWS * CARD_HEIGHT + (GRID_ROWS - 1) * card_gap
start_x = (SCREEN_WIDTH - grid_width) // 2
start_y = (SCREEN_HEIGHT - grid_height) // 2

cards_grid = []
for row in range(GRID_ROWS):
    for col in range(GRID_COLS):
        index = row * GRID_COLS + col
        x = start_x + col * (CARD_WIDTH + card_gap)
        y = start_y + row * (CARD_HEIGHT + card_gap)
        card = {
            'rect': pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT),
            'image': cards_for_game[index],
            'revealed': False,
            'matched': False,
            'shrinking': False,
            'animation_start_time': 0
        }
        cards_grid.append(card)

first_selection = None
second_selection = None
flip_back_time = 0
pending_match = False
turns = 0

def check_for_match(card1, card2):
    return card1['image'] == card2['image']

def reset_selections():
    global first_selection, second_selection, flip_back_time, pending_match
    first_selection = None
    second_selection = None
    flip_back_time = 0
    pending_match = False
pygame.display.set_icon(card_images["back"])
running = True
while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and flip_back_time == 0:
            pos = pygame.mouse.get_pos()
            for card in cards_grid:
                if card['rect'].collidepoint(pos) and not card['revealed'] and not card['matched'] and not card['shrinking']:
                    card['revealed'] = True
                    if first_selection is None:
                        first_selection = card
                    elif second_selection is None and card is not first_selection:
                        second_selection = card
                        turns += 1
                        if check_for_match(first_selection, second_selection):
                            pending_match = True
                        else:
                            pending_match = False
                        flip_back_time = current_time + 1000
                    break
    if flip_back_time != 0 and current_time >= flip_back_time:
        if pending_match:
            first_selection['shrinking'] = True
            first_selection['animation_start_time'] = current_time
            second_selection['shrinking'] = True
            second_selection['animation_start_time'] = current_time
        else:
            first_selection['revealed'] = False
            second_selection['revealed'] = False
        reset_selections()
    for card in cards_grid:
        if card['shrinking']:
            elapsed = current_time - card['animation_start_time']
            progress = max(0, 1.0 - elapsed / ANIMATION_DURATION)
            if progress <= 0:
                card['shrinking'] = False
                card['matched'] = True
            else:
                card['current_scale'] = progress
        else:
            card['current_scale'] = 1.0
    if all(card['matched'] for card in cards_grid):
        font_big = pygame.font.SysFont(None, 60)
        win_text = font_big.render("You win!", True, (255, 215, 0))
        screen.fill((34, 139, 34))
        win_x = (SCREEN_WIDTH - win_text.get_width()) // 2
        win_y = (SCREEN_HEIGHT - win_text.get_height()) // 2
        screen.blit(win_text, (win_x, win_y))
        pygame.display.flip()
        pygame.time.wait(2000)
        random.shuffle(cards_for_game)
        for index, card in enumerate(cards_grid):
            card['image'] = cards_for_game[index]
            card['revealed'] = False
            card['matched'] = False
            card['shrinking'] = False
            card['current_scale'] = 1.0
        turns = 0
    screen.fill((34, 139, 34))
    for card in cards_grid:
        if not card['matched']:
            if card['shrinking']:
                scale = card['current_scale']
                new_width = int(CARD_WIDTH * scale)
                new_height = int(CARD_HEIGHT * scale)
                center = card['rect'].center
                if card['revealed']:
                    image = card_images.get(card['image'], card_images["back"])
                else:
                    image = card_images["back"]
                scaled_image = pygame.transform.scale(image, (new_width, new_height))
                new_rect = scaled_image.get_rect(center=center)
                screen.blit(scaled_image, new_rect.topleft)
            else:
                if card['revealed']:
                    image = card_images.get(card['image'], card_images["back"])
                else:
                    image = card_images["back"]
                screen.blit(image, card['rect'].topleft)
    font_small = pygame.font.SysFont(None, 36)
    turn_text = font_small.render(f"Turns: {turns}", True, (255, 255, 255))
    screen.blit(turn_text, (10, 10))
    pygame.display.flip()
    clock.tick(30)
pygame.quit()
