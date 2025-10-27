import pygame
import random
import sys
import time

# Initialization
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((720, 960))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier", 48)
pixel_font = pygame.font.Font(pygame.font.match_font('pixeltype', bold=True), 72)

# # Load and display cover image for 3 seconds
# cover_image = pygame.image.load("cover image.png").convert()
# cover_image = pygame.transform.scale(cover_image, (720, 960))
# screen.blit(cover_image, (0, 0))
# pygame.display.flip()
# pygame.time.wait(3000)  # Display for 3 seconds

# Load assets
def load_image(path, scale_size):
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, scale_size)

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    return lines

char = load_image("char.png", (120, 120))
char_right = load_image("char_left.png", (150, 120))
char_left = pygame.transform.flip(char_right, True, False)
cat_images = [load_image(f"cute_cat{i}.png", (150, 100)) for i in range(1, 5)]
bomb_img = load_image("bomb.png", (80, 80))
background = load_image("backgrounds.png", (720, 960))
scary_cat = load_image("scary cat.jpeg", (720, 960))

# Sounds
jumpscare_sound = pygame.mixer.Sound("jump scare.mp3")
cat_scream = pygame.mixer.Sound("catscreaming.wav")
im_coming = pygame.mixer.Sound("im coming.mp3")
hit_sound = pygame.mixer.Sound("catscreaming.wav")

# 🔊 Play background music
pygame.mixer.music.load("totally normall game... .wav")
pygame.mixer.music.play(-1)  # Loop forever

# Game variables
char_x = 320
char_y = 800
char_speed = 5
current_image = char
cat_drops = []
bombs = []
score = 0
spawn_timer = 0
bomb_timer = 0

questions = [
    "What's your name?", "Do you live alone?", "How old are you?",
    "What's your cat's name again?", "Why is your bedroom light still on?",
    "Do you always leave your window open at night?", "What's your IP address?",
    "Has anyone ever watched you sleep?", "Why did your cat just hide under the bed?",
    "Who's behind you?", "Why is it purring?"
]
question_index = 0
question_triggered_scores = set()
asking_question = False
user_input = ""
question_text_display = ""
question_display_index = 0
question_timer = 0
letter_delay = 30

final_sequence_triggered = False
final_sequence_started = False
final_timer = 0
cat_scream_played = False
im_coming_started = False

running = True

# Main loop
while running:
    dt = clock.tick(60)
    spawn_timer += dt
    bomb_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if asking_question:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    asking_question = False
                    user_input = ""
                    question_display_index = 0
                    question_text_display = ""
                    question_index += 1
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    if len(user_input) < 30:
                        user_input += event.unicode

    # Movement
    keys = pygame.key.get_pressed()
    if not asking_question and not final_sequence_started:
        if keys[pygame.K_LEFT]:
            char_x -= char_speed
            current_image = char_left
        elif keys[pygame.K_RIGHT]:
            char_x += char_speed
            current_image = char_right
        else:
            current_image = char
        char_x = max(0, min(char_x, 720 - 120))

    # Spawn cats
    if spawn_timer > 1000 and not asking_question and not final_sequence_started:
        index = random.choices([0, 1, 2, 3], [33, 33, 29, 5])[0]
        cat_drops.append({
            "image": cat_images[index],
            "x": random.randint(0, 570),
            "y": 0,
            "index": index
        })
        spawn_timer = 0

    # Spawn bombs
    if bomb_timer > 2000 and not asking_question and not final_sequence_started:
        bombs.append(pygame.Rect(random.randint(0, 640), -80, 80, 80))
        bomb_timer = 0

    # Update objects
    if not final_sequence_started:
        human_hitbox = pygame.Rect(char_x, char_y, 120, 120)

        new_cat_drops = []
        for cat in cat_drops:
            cat["y"] += 5
            cat_hitbox = pygame.Rect(cat["x"], cat["y"], 150, 100)
            if human_hitbox.colliderect(cat_hitbox):
                score += 3 if cat["index"] == 3 else 1
                if score % 10 == 0 and score not in question_triggered_scores and question_index < len(questions):
                    asking_question = True
                    question_triggered_scores.add(score)
                    question_timer = pygame.time.get_ticks()
            else:
                if cat["y"] < 960:
                    new_cat_drops.append(cat)
        cat_drops = new_cat_drops

        # Bomb collisions
        new_bombs = []
        for bomb in bombs:
            bomb.move_ip(0, 5)
            if bomb.colliderect(human_hitbox):
                hit_sound.play()
                score = max(0, score - 2)
            elif bomb.top < 960:
                new_bombs.append(bomb)
        bombs = new_bombs

    # Final horror
    if score >= 120 and not final_sequence_triggered:
        final_sequence_triggered = True
        final_sequence_started = True
        pygame.mixer.music.stop()  # 🔇 Stop background music
        pygame.mixer.stop()        # Stop all current sounds
        jumpscare_sound.play()
        jumpscare_sound.stop()
        final_timer = pygame.time.get_ticks()

    # Drawing
    screen.blit(background, (0, 0))

    if not final_sequence_started:
        for cat in cat_drops:
            screen.blit(cat["image"], (cat["x"], cat["y"]))
        for bomb in bombs:
            screen.blit(bomb_img, bomb.topleft)
        screen.blit(current_image, (char_x, char_y))
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (20, 20))

        if asking_question and question_index < len(questions):
            pygame.draw.rect(screen, (255, 255, 255), (100, 300, 520, 300))
            pygame.draw.rect(screen, (0, 0, 0), (100, 300, 520, 300), 4)
            now = pygame.time.get_ticks()
            if question_display_index < len(questions[question_index]) and now - question_timer > letter_delay:
                question_text_display += questions[question_index][question_display_index]
                question_display_index += 1
                question_timer = now
            for i, line in enumerate(wrap_text(question_text_display, font, 500)):
                screen.blit(font.render(line, True, (0, 0, 0)), (110, 330 + i * 50))
            screen.blit(font.render(user_input, True, (0, 0, 255)), (110, 330 + len(wrap_text(question_text_display, font, 500)) * 50 + 10))

    else:
        now = pygame.time.get_ticks()
        elapsed = now - final_timer
        if elapsed < 2000:
            screen.fill((0, 0, 0))
            screen.blit(pixel_font.render("I'm coming", True, (255, 255, 255)), (180, 440))
        else:
            screen.blit(scary_cat, (0, 0))
            if not cat_scream_played:
                cat_scream.play()
                cat_scream_played = True
            if elapsed > 2000 and not im_coming_started:
                im_coming.play(loops=-1)
                im_coming_started = True

    pygame.display.flip()

pygame.quit()
