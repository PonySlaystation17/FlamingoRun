import pygame
import sys
import os
import random

pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flamingo Run")

font = pygame.font.SysFont('freesansbold.ttf', 40)
score_font = pygame.font.SysFont('freesansbold.ttf', 30)

points = 0
high_scores = {
    "dino": 0,
    "mario": 0,
    "minecraft": 0
}
PINK = (240, 98, 146)

#Habit stats
longest_streak_days = 63
streaks_over_week = 7
active_streaks = 11

theme_unlocks = {}
character_unlocks = {}
initial_laser_time = 0
initial_fireballs = 0
initial_punches = 0

# Characters
character_assets = {
    "flamingo_pink": {
        "RUNNING": [pygame.image.load(os.path.join("Assets/Birb", "FlamingoRun1.png")),
                    pygame.image.load(os.path.join("Assets/Birb", "FlamingoRun2.png"))],
        "JUMPING": pygame.image.load(os.path.join("Assets/Birb", "FlamingoJump.png")),
        "DUCKING": [pygame.image.load(os.path.join("Assets/Birb", "FlamingoDuck1.png")),
                    pygame.image.load(os.path.join("Assets/Birb", "FlamingoDuck2.png"))]
    },
    "flamingo_green": {
        "RUNNING": [pygame.image.load(os.path.join("Assets/Birb", "FlamingoGreenRun1.png")),
                    pygame.image.load(os.path.join("Assets/Birb", "FlamingoGreenRun2.png"))],
        "JUMPING": pygame.image.load(os.path.join("Assets/Birb", "FlamingoGreenJump.png")),
        "DUCKING": [pygame.image.load(os.path.join("Assets/Birb", "FlamingoGreenDuck1.png")),
                    pygame.image.load(os.path.join("Assets/Birb", "FlamingoGreenDuck2.png"))]
    },
    "flamingo_black": {
        "RUNNING": [pygame.image.load(os.path.join("Assets/Birb", "FlamingoBlackRun1.png")),
                    pygame.image.load(os.path.join("Assets/Birb", "FlamingoBlackRun2.png"))],
        "JUMPING": pygame.image.load(os.path.join("Assets/Birb", "FlamingoBlackJump.png")),
        "DUCKING": [pygame.image.load(os.path.join("Assets/Birb", "FlamingoBlackDuck1.png")),
                    pygame.image.load(os.path.join("Assets/Birb", "FlamingoBlackDuck2.png"))]
    }
}

current_character = "flamingo_pink"
RUNNING = character_assets[current_character]["RUNNING"]
JUMPING = character_assets[current_character]["JUMPING"]
DUCKING = character_assets[current_character]["DUCKING"]

# Sound Effects
LASER_SOUND = pygame.mixer.Sound(os.path.join("Assets/Sound", "laser.wav"))
LASER_SOUND.set_volume(0.6)
FIREBALL_SOUND = pygame.mixer.Sound(os.path.join("Assets/Sound", "fireball.wav"))
GLOVE_SOUND = pygame.mixer.Sound(os.path.join("Assets/Sound", "punch_miss.wav"))
GLOVE_HIT_SOUND = pygame.mixer.Sound(os.path.join("Assets/Sound", "punch_hit.wav"))
BOW_SHOOT_SOUND = pygame.mixer.Sound(os.path.join("Assets/Sound", "bow_shoot.wav"))
BOW_SHOOT_SOUND.set_volume(1)

# Other
FIREBALL_RAW = pygame.image.load(os.path.join("Assets/Other", "fireball.png"))
FIREBALL = pygame.transform.scale(FIREBALL_RAW, (50, 50))
FIREBALL_ICON = pygame.transform.scale(FIREBALL, (35, 30))

LASER_EYE_RAW = pygame.image.load(os.path.join("Assets/Birb", "laser_eye5.png")).convert_alpha()
LASER_EYE = pygame.transform.scale(LASER_EYE_RAW, (130, 130))
LASER_ICON = pygame.transform.scale(LASER_EYE, (75, 75))

GLOVE_IMG = pygame.transform.scale(pygame.image.load(os.path.join("Assets/Other", "glove.png")), (120, 100))
GLOVE_HIT_IMG = pygame.transform.scale(pygame.image.load(os.path.join("Assets/Other", "glove_hit.png")), (120, 100))
GLOVE_ICON = pygame.transform.scale(GLOVE_IMG, (45, 40))


ARROW = pygame.image.load(os.path.join("Assets/Other", "arrow.png")).convert_alpha()
ARROW = pygame.transform.scale(ARROW, (50, 15))

# Background Themes
current_theme = "dino"
themes = {
    "dino": {
        "BG": pygame.image.load(os.path.join("Assets/Other", "Track.png")),
        "CLOUD": pygame.image.load(os.path.join("Assets/Other", "Cloud.png")),
        "y_offset": 380
    },
    "mario": {
        "BG": pygame.transform.scale(pygame.image.load(os.path.join("Assets/Other", "mario_track.png")), (2000, 600)),
        "CLOUD": pygame.transform.scale(pygame.image.load(os.path.join("Assets/Other", "Mario_cloud.png")), (120, 100)),
        "y_offset": -20
    },
    "minecraft": {
        "BG": pygame.transform.scale(pygame.image.load(os.path.join("Assets/Other", "minecraft_track.png")), (2000, 600)),
        "CLOUD": pygame.image.load(os.path.join("Assets/Other", "Minecraft_cloud.png")),
        "y_offset": -7
    }
}

BG = themes[current_theme]["BG"]
CLOUD = themes[current_theme]["CLOUD"]
y_offset = themes[current_theme]["y_offset"]

# habits and unlocks
def apply_unlocks():
    global character_unlocks, theme_unlocks, initial_fireballs, initial_punches, initial_laser_time
    character_unlocks = {
        "flamingo_pink": True,
        "flamingo_green": streaks_over_week >= 3,
        "flamingo_black": streaks_over_week >= 5
        }
    theme_unlocks = {
        "dino": True,
        "mario": longest_streak_days >= 30,
        "minecraft": longest_streak_days >= 60
        }
    # Powerups
    initial_laser_time = longest_streak_days * 100  # 0.1 sec = 100 ms per day
    initial_fireballs = streaks_over_week
    initial_punches = active_streaks

# Classes
class Flamingo(pygame.sprite.Sprite):
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        super().__init__()
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING
        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False
        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.rect = self.image.get_rect()
        self.rect.x = self.X_POS
        self.rect.y = self.Y_POS

        self.laser_active = False
        self.laser_allowed = True
        self.laser_duration = 0
        self.laser_used_time = 0
        self.laser_last_on_time = None
        self.fireball_count = 0
        self.punching = False
        self.punch_start_time = 0
        self.punch_duration = 300
        self.glove_uses = 0
        self.glove_rect = None
        self.glove_hit = False

    def update(self, userInput):
        if self.dino_duck:
            self.duck()
        elif self.dino_run:
            self.run()
        elif self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if userInput[pygame.K_UP] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

        current_time = pygame.time.get_ticks()

        if userInput[pygame.K_SPACE] and self.laser_allowed:
            if not self.laser_active:
                self.laser_active = True
                self.laser_last_on_time = current_time
                LASER_SOUND.play(-1)
            else:
                time_on = current_time - self.laser_last_on_time
                total_used = self.laser_used_time + time_on
                if total_used >= self.laser_duration:
                    self.laser_allowed = False
                    self.laser_active = False
                    self.laser_used_time = self.laser_duration
                    self.laser_last_on_time = None
                    LASER_SOUND.stop()

        elif self.laser_active:
            if self.laser_last_on_time is not None:
                time_on = current_time - self.laser_last_on_time
                self.laser_used_time += time_on
            self.laser_active = False
            self.laser_last_on_time = None
            LASER_SOUND.stop()

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        self.rect.y -= self.jump_vel * 4
        self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def punch(self, obstacle_group):
        if not self.punching and self.glove_uses > 0:
            self.punch_start_time = pygame.time.get_ticks()
            self.glove_hit = False
            self.punching = True
            self.glove_uses -= 1

            glove_x = self.rect.right
            glove_y = self.rect.centery - GLOVE_IMG.get_height() // 2
            glove_rect = pygame.Rect(glove_x, glove_y, GLOVE_IMG.get_width(), GLOVE_IMG.get_height())

            for obstacle in obstacle_group:
                if glove_rect.colliderect(obstacle.rect):
                    obstacle.kill()
                    self.glove_hit = True
                    GLOVE_HIT_SOUND.play()
                    return
            GLOVE_SOUND.play()

# Obstacle base class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            self.kill()

# Dino obstacles
class SmallCactus(Obstacle):
    def __init__(self):
        images = [pygame.image.load(os.path.join("Assets/Cactus", f"SmallCactus{i+1}.png")) for i in range(3)]
        super().__init__(random.choice(images))
        self.rect.y = 325

class LargeCactus(Obstacle):
    def __init__(self):
        images = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png"))]
        super().__init__(random.choice(images))
        self.rect.y = 300

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
                    pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = random.choice([200, 260, 300])

    def update(self):
        self.rect.x -= game_speed
        self.index = (self.index + 1) % 10
        self.image = self.images[self.index // 5]
        if self.rect.x < -self.rect.width:
            self.kill()

# Mario obstacles
class Goomba(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        raw_images = [pygame.image.load(os.path.join("Assets/Cactus", "goomba1.png")),
                    pygame.image.load(os.path.join("Assets/Cactus", "goomba2.png"))]
        self.images = [pygame.transform.scale(img, (60, 60)) for img in raw_images]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = 340

    def update(self):
        self.rect.x -= (game_speed + 3)
        self.index = (self.index + 1) % 10
        self.image = self.images[self.index // 5]
        if self.rect.x < -self.rect.width:
            self.kill()

class GreenPipe(Obstacle):
    def __init__(self):
        image = pygame.image.load(os.path.join("Assets/Cactus", "green_pipe_long.png"))
        image = pygame.transform.scale(image, (65, 100))
        super().__init__(image)
        self.rect.y = 300

class Fish(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        raw_images = [pygame.image.load(os.path.join("Assets/Bird", "fish1.png")),
                    pygame.image.load(os.path.join("Assets/Bird", "fish2.png"))]
        self.images = [pygame.transform.scale(img, (65, 65)) for img in raw_images]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = random.choice([200, 260, 300])

    def update(self):
        self.rect.x -= game_speed
        self.index = (self.index + 1) % 10
        self.image = self.images[self.index // 5]
        if self.rect.x < -self.rect.width:
            self.kill()

# Minecraft obstacles
class Skele(pygame.sprite.Sprite):
    global arrow_group
    def __init__(self):
        super().__init__()
        raw_images = [pygame.image.load(os.path.join("Assets/Cactus", "skele1.png")),
                    pygame.image.load(os.path.join("Assets/Cactus", "skele2.png"))]
        self.images = [pygame.transform.scale(img, (65, 100)) for img in raw_images]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = 300

        self.last_shot_time = 0

    def update(self):
        self.rect.x -= game_speed
        self.index = (self.index + 1) % 10
        self.image = self.images[self.index // 5]
        self.rect.x -= 1
        if self.rect.x < -self.rect.width:
            self.kill()
        # Skeleton shooting
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > 2000:  # 2000 ms = 2 seconds
            if random.randint(0, 100) == 0:  # still random chance to shoot
                arrow = Arrow(self.rect.centerx, 325)
                arrow_group.add(arrow)
                BOW_SHOOT_SOUND.play()
                self.last_shot_time = current_time

class MinecraftCactus(Obstacle):
    def __init__(self):
        image = pygame.image.load(os.path.join("Assets/Cactus", "minecraft_cactus.png"))
        image = pygame.transform.scale(image, (60, 60))
        super().__init__(image)
        self.rect.y = 340

class Ghast(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        raw_images = [pygame.image.load(os.path.join("Assets/Bird", "Ghast1.png")),
                    pygame.image.load(os.path.join("Assets/Bird", "Ghast2.png"))]
        self.images = [pygame.transform.scale(img, (65, 95)) for img in raw_images]
        self.index = 0
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = random.choice([200, 260, 300])
        
        self.float_direction = 1  # 1 = down, -1 = up
        self.float_counter = 0

    def update(self):
        # Animate
        self.index = (self.index + 1) % 10
        self.image = self.images[self.index // 5]

        # Float up and down smoothly
        self.float_counter += 1
        if self.float_counter >= 20:
            self.float_direction *= -1
            self.float_counter = 0
        self.rect.y += self.float_direction * random.randint(1, 2)

        # Move left
        self.rect.x -= game_speed

        if self.rect.x < -self.rect.width:
            self.kill()

# Other
class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = CLOUD
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.rect.y = random.randint(50, 100)

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            self.rect.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.rect.y = random.randint(50, 100)

class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = FIREBALL
        self.rect = self.image.get_rect()
        self.rect.x = x - 15
        self.rect.y = y
        self.speed = 15

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > SCREEN_WIDTH:
            self.kill()

class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = ARROW
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 8

    def update(self):
        self.rect.x -= (game_speed + self.speed)
        if self.rect.x < 0:
            self.kill()


# Managers
def setObstacleList(current_theme):
    global obstacleList
    if current_theme == "dino":
        obstacleList = [SmallCactus, LargeCactus, Bird]
    elif current_theme == "mario":
        obstacleList = [Goomba, GreenPipe, Fish]
    elif current_theme == "minecraft":
        obstacleList = [Skele, MinecraftCactus, Ghast]

def obstacleManager():
    global obstacle_group, obstacleList
    obstacle_type = random.choice(obstacleList)
    obstacle_group.add(obstacle_type())

# Theme and Character Switch
def setCharacter(character):
    global RUNNING, JUMPING, DUCKING
    if character == "flamingo_pink":
        RUNNING = [pygame.image.load(os.path.join("Assets/Birb", "FlamingoRun1.png")),
                pygame.image.load(os.path.join("Assets/Birb", "FlamingoRun2.png"))]
        JUMPING = pygame.image.load(os.path.join("Assets/Birb", "FlamingoJump.png"))
        DUCKING = [pygame.image.load(os.path.join("Assets/Birb", "FlamingoDuck1.png")),
                pygame.image.load(os.path.join("Assets/Birb", "FlamingoDuck2.png"))]
    elif character == "flamingo_green":
        RUNNING = [pygame.image.load(os.path.join("Assets/Birb", "FlamingoGreenRun1.png")),
                pygame.image.load(os.path.join("Assets/Birb", "FlamingoGreenRun2.png"))]
        JUMPING = pygame.image.load(os.path.join("Assets/Birb", "FlamingoGreenJump.png"))
        DUCKING = [pygame.image.load(os.path.join("Assets/Birb", "FlamingoGreenDuck1.png")),
                pygame.image.load(os.path.join("Assets/Birb", "FlamingoGreenDuck2.png"))]
    elif character == "flamingo_black":
        RUNNING = [pygame.image.load(os.path.join("Assets/Birb", "FlamingoBlackRun1.png")),
                pygame.image.load(os.path.join("Assets/Birb", "FlamingoBlackRun2.png"))]
        JUMPING = pygame.image.load(os.path.join("Assets/Birb", "FlamingoBlackJump.png"))
        DUCKING = [pygame.image.load(os.path.join("Assets/Birb", "FlamingoBlackDuck1.png")),
                pygame.image.load(os.path.join("Assets/Birb", "FlamingoBlackDuck2.png"))]

def setWorld(theme):
    global BG, y_offset, CLOUD
    if theme == "dino":
        BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))
        y_offset = 380
        CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))
    elif theme == "mario":
        BG = pygame.transform.scale(pygame.image.load(os.path.join("Assets/Other", "mario_track.png")), (2000, 600))
        y_offset = -20
        CLOUD = pygame.transform.scale(pygame.image.load(os.path.join("Assets/Other", "Mario_cloud.png")), (160, 110))
    elif theme == "minecraft":
        BG = pygame.transform.scale(pygame.image.load(os.path.join("Assets/Other", "minecraft_track.png")), (2000, 600))
        y_offset = -5
        CLOUD = pygame.transform.scale(pygame.image.load(os.path.join("Assets/Other", "Minecraft_cloud.png")), (200, 75))

    setObstacleList(theme)

# Drawing functions
def draw_theme_background(current_theme):
    if current_theme == "dino":
        SCREEN.fill((255, 255, 255))
    SCREEN.blit(BG, (0, y_offset))

def draw_text(text, y, color=None):
    if color is None:
        color = PINK if current_character == "flamingo_pink" else (0, 0, 0)

    shadow_color = (150, 150, 150)  # Light grey shadow
    rendered = font.render(text, True, color)
    shadow = font.render(text, True, shadow_color)

    x = SCREEN_WIDTH // 2 - rendered.get_width() // 2

    # Draw shadow first, then text
    SCREEN.blit(shadow, (x + 1, y + 1))
    SCREEN.blit(rendered, (x, y))

def draw_score_text(text, y, color=None):
    rendered = score_font.render(text, True, (0, 0, 0))
    x = SCREEN_WIDTH // 2 - rendered.get_width() // 2
    SCREEN.blit(rendered, (x, y))

def get_hitbox(sprite_name, rect):
    if sprite_name == "player":
        return rect.inflate(-30, -20)
    elif sprite_name == "small_cactus":
        return rect.inflate(-20, -10)
    elif sprite_name == "large_cactus":
        return rect.inflate(-25, -10)
    elif sprite_name == "bird":
        hitbox = rect.inflate(-35, -20)
        hitbox.y += 5
        return hitbox
    elif sprite_name == "goomba":
        return rect.inflate(-20, -10)
    elif sprite_name == "green_pipe":
        return rect.inflate(-15, -10)
    elif sprite_name == "fish":
        return rect.inflate(-20, -15)
    elif sprite_name == "skele":
        return rect.inflate(-20, -10)
    elif sprite_name == "minecraft_cactus":
        return rect.inflate(-15, -10)
    elif sprite_name == "ghast":
        return rect.inflate(-20, -15)
    elif sprite_name == "arrow":
        return rect.inflate(-10, -5)
    else:
        return rect

# Menus
def theme_menu():
    global current_theme, theme_unlocks
    menu_running = True
    options = ["Chrome Dinosaur", "Mario", "Minecraft", "Back"]
    theme_keys = ["dino", "mario", "minecraft"]
    selected = 0

    while menu_running:
        draw_theme_background(current_theme)
        draw_text("Select Theme:", 150, (0, 0, 0))

        for i, option in enumerate(options):
            if i < 3:
                is_unlocked = theme_unlocks.get(theme_keys[i], False)
            else:
                is_unlocked = True

            color = PINK if i == selected else (160, 160, 160) if not is_unlocked else (0, 0, 0)
            draw_text(f"{i+1}. {option}", 220 + i * 50, color)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected in [0, 1, 2] and theme_unlocks[theme_keys[selected]]:
                        current_theme = theme_keys[selected]
                        setWorld(current_theme)
                    elif selected == 3:
                        return

def character_menu():
    global current_character, character_unlocks
    menu_running = True
    options = ["Flamingo Pink", "Flamingo Green", "Flamingo Black", "Back"]
    char_keys = ["flamingo_pink", "flamingo_green", "flamingo_black"]
    selected = 0
    menu_clock = pygame.time.Clock()
    step_index = 0

    active_character_preview = current_character

    while menu_running:
        draw_theme_background(current_theme)
        draw_text("Select Character:", 150, (0, 0, 0))

        # Draw menu options
        for i, option in enumerate(options):
            if i < 3:
                is_unlocked = character_unlocks.get(char_keys[i], False)
            else:
                is_unlocked = True  # Back is always unlocked

            color = PINK if i == selected else (160, 160, 160) if not is_unlocked else (0, 0, 0)
            draw_text(f"{i+1}. {option}", 220 + i * 50, color)

        # Show active character preview
        if active_character_preview in character_assets:
            running_frames = character_assets[active_character_preview]["RUNNING"]
            frame = running_frames[step_index // 5]
            preview_img = pygame.transform.scale(frame, (100, 100))
            SCREEN.blit(preview_img, (SCREEN_WIDTH // 2 + 200, 260))

        pygame.display.update()
        menu_clock.tick(10)
        step_index = (step_index + 1) % 10

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected in [0, 1, 2] and character_unlocks[char_keys[selected]]:
                        current_character = char_keys[selected]
                        setCharacter(current_character)
                        active_character_preview = current_character
                    elif selected == 3:
                        return

def main_menu():
    global points, high_scores, current_theme
    apply_unlocks()
    menu_options = ["Start Game", "Change Theme", "Change Character", "Quit Game"]
    selected = 0
    menu_running = True

    while menu_running:
        setWorld(current_theme)
        setCharacter(current_character)
        draw_theme_background(current_theme)

        draw_text(f"High Scores: ", 40, (0, 0, 0))
        draw_score_text(f"Dino - {high_scores['dino']}", 85, (0, 0, 0))
        draw_score_text(f"Mario - {high_scores['mario']}", 125, (0, 0, 0))
        draw_score_text(f"Minecraft - {high_scores['minecraft']}", 165, (0, 0, 0))


        character_preview = pygame.transform.scale(RUNNING[0], (100, 100))
        SCREEN.blit(character_preview, (SCREEN_WIDTH // 2 - 50, 210))

        for i, option in enumerate(menu_options):
            color = (240, 98, 146) if i == selected else (0, 0, 0)
            if i == 0:
                draw_text(option, 330, color)
            else:
                draw_text(option, 350 + (i * 50), color)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        menu_running = False
                    elif selected == 1:
                        theme_menu()
                    elif selected == 2:
                        character_menu()
                    elif selected == 3:
                        pygame.quit()
                        sys.exit()

def game_over_screen(score, high_score):
    selected = 0
    options = ["Restart", "Main Menu"]
    clock = pygame.time.Clock()

    while True:
        draw_theme_background(current_theme)

        draw_text("Game Over", 100, (200, 0, 0))
        draw_text(f"Score: {score}", 180)
        draw_text(f"High Score: {high_scores[current_theme]}", 230)

        for i, option in enumerate(options):
            color = (240, 98, 146) if i == selected else (0, 0, 0)
            draw_text(option, 300 + i * 50, color)

        pygame.display.flip()  # ← more reliable than update()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return "restart" if selected == 0 else "menu"


# Helpers
def end_of_round():
    global points, high_scores, current_theme
    if points > high_scores[current_theme]:
        high_scores[current_theme] = points

    return game_over_screen(points, high_scores[current_theme])

def background():
    global x_pos_bg, y_offset
    image_width = BG.get_width()

    SCREEN.blit(BG, (x_pos_bg, y_offset))
    SCREEN.blit(BG, (image_width + x_pos_bg, y_offset))

    if x_pos_bg <= -image_width:
        x_pos_bg = 0

    x_pos_bg -= game_speed

def draw_hints():
    global start_time
    elapsed = pygame.time.get_ticks() - start_time
    fade_duration = 5000  # Show hints for 4 seconds

    if elapsed > fade_duration:
        return

    # Calculate fade-out alpha
    alpha = max(0, 255 - int((elapsed / fade_duration) * 255))

    hint_font = pygame.font.SysFont('freesansbold.ttf', 24)
    hint_surface = pygame.Surface((SCREEN_WIDTH, 120), pygame.SRCALPHA)
    hint_surface.set_alpha(alpha)

    hint_texts = [
        "Up/Down Arrows: Jump/Duck",
        "G: Glove Punch",
        "F: Fireball",
        "SPACE: Laser Eyes"
    ]

    for i, text in enumerate(hint_texts):
        rendered = hint_font.render(text, True, (0, 0, 0))
        x = SCREEN_WIDTH // 2 - rendered.get_width() // 2
        y = 500 + (i * 25)
        hint_surface.blit(rendered, (x, y - 500))

    SCREEN.blit(hint_surface, (0, 50))


def score():
    global points, game_speed
    points += 1
    if points % 250 == 0:
        game_speed += 1
    text = font.render(f"Points: {points}", True, (0, 0, 0))
    SCREEN.blit(text, (900, 40))

def laser_score(player):
    remaining_ms = player.laser_duration - player.laser_used_time
    if player.laser_active and player.laser_last_on_time:
        remaining_ms -= pygame.time.get_ticks() - player.laser_last_on_time
    remaining_ms = max(0, remaining_ms)
    remaining_sec = round(remaining_ms / 1000, 1)

    SCREEN.blit(LASER_ICON, (1, 10))
    text = font.render(f"{remaining_sec}s", True, (0, 0, 0))
    SCREEN.blit(text, (60, 30))

def fireball_score(player):
    SCREEN.blit(FIREBALL_ICON, (20, 70))
    text = font.render(f"{player.fireball_count}", True, (0, 0, 0))
    SCREEN.blit(text, (60, 70))

def glove_score(player):
    SCREEN.blit(GLOVE_ICON, (20, 105))
    text = font.render(f"{player.glove_uses}", True, (0, 0, 0))
    SCREEN.blit(text, (60, 110))

# Main
def main():
    global game_speed, x_pos_bg, points, obstacle_group, obstacleList, arrow_group, start_time
    run = True
    start_time = pygame.time.get_ticks()
    clock = pygame.time.Clock()
    apply_unlocks()

    player = Flamingo()
    player.laser_duration = initial_laser_time
    player.fireball_count = initial_fireballs
    player.glove_uses = initial_punches

    fireball_group = pygame.sprite.Group()
    cloud_group = pygame.sprite.Group(Cloud())
    obstacle_group = pygame.sprite.Group()
    arrow_group = pygame.sprite.Group()

    next_obstacle_delay = random.randint(800, 2200)  # ms
    last_spawn_time = pygame.time.get_ticks()


    game_speed = 10
    x_pos_bg = 0
    points = 0
    laser_hits = []

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f and player.fireball_count > 0:
                    fireball_y = player.rect.centery - 40
                    fireball = Fireball(player.rect.right, fireball_y)
                    fireball_group.add(fireball)
                    FIREBALL_SOUND.play()
                    player.fireball_count -= 1
                if event.key == pygame.K_g:
                    player.punch(obstacle_group)

        userInput = pygame.key.get_pressed()

        player.update(userInput)
        cloud_group.update()
        obstacle_group.update()
        fireball_group.update()

        if current_theme == "dino":
            SCREEN.fill((255, 255, 255))
        background()
        draw_hints()
        cloud_group.draw(SCREEN)
        SCREEN.blit(player.image, player.rect)
        obstacle_group.draw(SCREEN)
        fireball_group.draw(SCREEN)

        # Laser
        if player.laser_active:
            if player.dino_duck:
                eye_y = (player.rect.y) + (player.rect.height // 5) - 10
                eye_x = player.rect.right - 10
            else:
                eye_y = (player.rect.y - 10) + (player.rect.height // 6) + 5
                if player.image == RUNNING[0]:
                    eye_x = player.rect.right - 16
                else:
                    eye_x = player.rect.right - 10

            pygame.draw.circle(SCREEN, (255, 0, 0), (eye_x, eye_y), 7)
            pygame.draw.circle(SCREEN, (255, 102, 102), (eye_x, eye_y), 4)
            SCREEN.blit(LASER_EYE, (eye_x - LASER_EYE.get_width() // 2, eye_y - LASER_EYE.get_height() // 2 + 5))

            laser_start = (eye_x, eye_y)
            laser_end = (SCREEN_WIDTH, eye_y)

            pygame.draw.line(SCREEN, (255, 0, 0), laser_start, laser_end, 5)
            pygame.draw.line(SCREEN, (255, 153, 153), (laser_start[0], laser_start[1]-1), (laser_end[0], laser_end[1]-1), 2)

            laser_rect = pygame.Rect(player.rect.right, eye_y, SCREEN_WIDTH - player.rect.right, 1)

            for obstacle in obstacle_group:
                if laser_rect.colliderect(obstacle.rect):
                    laser_hits.append(obstacle.rect.center)
                    obstacle.kill()

        for hit in laser_hits:
            pygame.draw.circle(SCREEN, (255, 0, 0), hit, 20)

        laser_hits.clear()

        # Fireball hit detection
        for fireball in fireball_group:
            for obstacle in obstacle_group:
                if fireball.rect.colliderect(obstacle.rect):
                    fireball.kill()
                    obstacle.kill()

        # Spawn new obstacles
        current_time = pygame.time.get_ticks()
        if (current_time - last_spawn_time) > next_obstacle_delay:
            obstacleManager()
            last_spawn_time = current_time
            next_obstacle_delay = random.randint(800, 2200)

        # Punch
        if player.punching:
            elapsed = pygame.time.get_ticks() - player.punch_start_time
            glove_x = player.rect.right - 30
            if player.dino_duck:
                glove_y = (player.rect.centery - GLOVE_IMG.get_height() // 2) - 10
            else:
                glove_y = player.rect.centery - GLOVE_IMG.get_height() // 2
            glove_image = GLOVE_HIT_IMG if player.glove_hit else GLOVE_IMG
            SCREEN.blit(glove_image, (glove_x, glove_y))
            if elapsed > player.punch_duration:
                player.punching = False

        # Arrows
        arrow_group.update()
        arrow_group.draw(SCREEN)


        # Collision check
        player_hitbox = get_hitbox("player", player.rect)

        for obstacle in obstacle_group:
            if isinstance(obstacle, SmallCactus):
                obstacle_hitbox = get_hitbox("small_cactus", obstacle.rect)
            elif isinstance(obstacle, LargeCactus):
                obstacle_hitbox = get_hitbox("large_cactus", obstacle.rect)
            elif isinstance(obstacle, Bird):
                obstacle_hitbox = get_hitbox("bird", obstacle.rect)
            elif isinstance(obstacle, Goomba):
                obstacle_hitbox = get_hitbox("goomba", obstacle.rect)
            elif isinstance(obstacle, GreenPipe):
                obstacle_hitbox = get_hitbox("green_pipe", obstacle.rect)
            elif isinstance(obstacle, Fish):
                obstacle_hitbox = get_hitbox("fish", obstacle.rect)
            elif isinstance(obstacle, Skele):
                obstacle_hitbox = get_hitbox("skele", obstacle.rect)
            elif isinstance(obstacle, MinecraftCactus):
                obstacle_hitbox = get_hitbox("minecraft_cactus", obstacle.rect)
            elif isinstance(obstacle, Ghast):
                obstacle_hitbox = get_hitbox("ghast", obstacle.rect)
            else:
                obstacle_hitbox = obstacle.rect

            if player_hitbox.colliderect(obstacle_hitbox):
                LASER_SOUND.stop()
                pygame.time.delay(1000)
                action = end_of_round()
                return action

        for arrow in arrow_group:
            arrow_hitbox = get_hitbox("arrow", arrow.rect)
            if player_hitbox.colliderect(arrow_hitbox):
                LASER_SOUND.stop()
                pygame.time.delay(1000)
                action = end_of_round()
                return action


        score()
        laser_score(player)
        fireball_score(player)
        glove_score(player)

        clock.tick(30)
        pygame.display.update()

# run game
main_menu()
while True:
    apply_unlocks()
    outcome = main()
    if outcome == "restart":
        continue
    elif outcome == "menu":
        apply_unlocks()
        main_menu()
    else:
        break  # Just in case


