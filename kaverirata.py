try:
    import pygame
except:
    pass
import random
import os

# Alusta Pygame ja äänet
pygame.init()
pygame.mixer.init()

# Näytön asetukset
WIDTH = 800
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kaverirata")

# Lataa taustakuva
background_image = pygame.image.load("forest.png").convert()

# Lataa ääni, jos se on olemassa
sound_file = "pojoing.wav"
if os.path.exists(sound_file):
    pojoing_sound = pygame.mixer.Sound(sound_file)
else:
    pojoing_sound = None  # Ääntä ei soiteta, jos tiedostoa ei löydy

# Värit
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
TRANSPARENT_BLACK = (0, 0, 0, 128)  # Läpinäkyvä musta
TRANSPARENT_WHITE = (255, 255, 255, 128)  # Läpinäkyvä valkoinen
COLORS = {
    "Ralle": (255, 0, 0),    # Punainen
    "Tiiska": (0, 255, 0),   # Vihreä
    "Junnu": (0, 0, 255),    # Sininen
    "Pete": (255, 255, 0),   # Keltainen
    "Ile": (255, 165, 0),    # Oranssi
    "Tappi": (128, 0, 128),  # Violetti
    "Rintsu": (0, 255, 255), # Syaani
    "Salonen": (255, 192, 203), # Vaaleanpunainen
    "Aimo": (100, 100, 100)  # Harmaa
}

# Pelaaja (sydän)
player_width = 30
player_height = 30
player_x = 50
player_y = HEIGHT - player_height
player_speed = 5
player_jump = False
jump_velocity = 15  # Suurempi hyppyvoima
jumping = False
gravity = 0.4  # Pienempi painovoima
max_jump_height = HEIGHT - 200  # Nosta maksimi hyppykorkeutta
jump_time = 0  # Aikarajoituksen laskuri
max_jump_time = 15  # Lyhennä aikaa, jonka pelaaja voi pysyä ilmassa

# Esteet
obstacle_base_width = 15  # Pienennä esteiden perusleveyttä
obstacle_base_height = 60  # Ihmismäisen esteen korkeus
obstacle_speed = 4  # Esteiden nopeus
obstacles = []
min_gap = 150  # Minimiväli esteiden välillä
max_gap = 500  # Maksimiväli esteiden välillä
next_obstacle_distance = random.randint(min_gap, max_gap)  # Satunnainen etäisyys ensimmäiselle esteelle

# Nimet ja mittasuhteet esteille
obstacle_sizes = {
    "Ralle": 1.5,
    "Ile": 1.4,
    "Salonen": 1.4,
    "Tiiska": 1.2,
    "Junnu": 1.2,
    "Pete": 1.2,
    "Tappi": 1.2,
    "Rintsu": 1.2,
    "Aimo": 2.0  # Aimo on edelleen hieman suurempi este
}

# Pisteet
score = 0
font = pygame.font.Font(None, 36)

# Kierrokset
rounds = 3  # Määritä, että pelaaja saa kolme kierrosta
current_round = 1  # Alkuperäinen kierros

# Taustan liikkuminen
bg_x1 = 0
bg_x2 = WIDTH
background_speed = obstacle_speed  # Tausta liikkuu samaa nopeutta kuin esteet

# Pelin pääsilmukka
running = True
clock = pygame.time.Clock()
game_active = True  # Pelitila, joka seuraa onko peli käynnissä vai pysähdyksissä

def reset_game():
    global player_x, player_y, jumping, jump_velocity, jump_time, obstacles, score, game_active, current_round
    player_x = 50
    player_y = HEIGHT - player_height
    jumping = False
    jump_velocity = 15
    jump_time = 0
    obstacles = []
    score = 0
    game_active = True
    current_round = 1  # Nollaa kierrokset

def draw_heart(screen, color, x, y, width, height):
    top_circle_radius = width // 4
    bottom_triangle_height = height // 2

    # Piirrä kaksi ylintä ympyrää
    pygame.draw.circle(screen, color, (x + top_circle_radius, y + top_circle_radius), top_circle_radius)
    pygame.draw.circle(screen, color, (x + width - top_circle_radius, y + top_circle_radius), top_circle_radius)

    # Piirrä sydämen alaosan kolmio
    points = [
        (x, y + top_circle_radius),
        (x + width, y + top_circle_radius),
        (x + width // 2, y + height)
    ]
    pygame.draw.polygon(screen, color, points)

def draw_human(screen, color, x, y, width, height):
    # Pään koko suhteessa kehon leveyteen
    head_radius = int(width / 2)
    # Vartalon korkeus suhteessa kehon korkeuteen
    body_height = int(height * 0.6)
    # Vartalon paksuus
    body_thickness = 4
    # Kädet ja jalat
    arm_length = int(width * 0.8)
    leg_length = int(width * 0.5)

    # Piirrä pää
    pygame.draw.circle(screen, color, (x + head_radius, y + head_radius), head_radius)
    # Piirrä vartalo (paksumpi viiva)
    pygame.draw.line(screen, color, (x + head_radius, y + head_radius), (x + head_radius, y + head_radius + body_height), body_thickness)
    # Piirrä kädet
    pygame.draw.line(screen, color, (x + head_radius - arm_length // 2, y + head_radius + body_height // 3),
                     (x + head_radius + arm_length // 2, y + head_radius + body_height // 3), body_thickness)
    # Piirrä jalat
    pygame.draw.line(screen, color, (x + head_radius, y + head_radius + body_height), 
                     (x + head_radius - leg_length, y + height), body_thickness)
    pygame.draw.line(screen, color, (x + head_radius, y + head_radius + body_height), 
                     (x + head_radius + leg_length, y + height), body_thickness)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active and not jumping and player_y == HEIGHT - player_height:
                # Pelaaja voi hypätä vain, jos hän on maassa
                jumping = True
                if pojoing_sound:  # Soita ääni vain, jos se on ladattu
                    pojoing_sound.play()
            elif event.key == pygame.K_r and not game_active:
                if current_round < rounds:
                    current_round += 1
                    obstacles = []  # Nollaa esteet mutta säilytä pisteet
                    player_y = HEIGHT - player_height
                    game_active = True
                else:
                    reset_game()  # Nollaa peli kokonaan, kun kolme kierrosta on pelattu
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                jumping = False
                jump_time = 0  # Nollaa hyppyaika, kun välilyönti vapautetaan

    if game_active:
        # Pelaajan liike
        if jumping and player_y > max_jump_height and jump_time < max_jump_time:
            player_y -= jump_velocity
            jump_time += 1
        else:
            if player_y < HEIGHT - player_height:
                player_y += gravity * jump_velocity
            else:
                player_y = HEIGHT - player_height
                jumping = False  # Pysäytä hyppy, kun pelaaja osuu maahan

        # Jos pelaaja nousee liian korkealle, nopeuta putoamista
        if player_y <= max_jump_height:
            gravity = 1.0  # Nopeampi putoaminen
        else:
            gravity = 0.4  # Normaali painovoima

        # Esteiden luominen satunnaisella etäisyydellä
        if len(obstacles) == 0 or obstacles[-1][0] < WIDTH - next_obstacle_distance:
            obstacle_name = random.choice(list(obstacle_sizes.keys()))
            size_multiplier = obstacle_sizes[obstacle_name]
            obstacle_width = int(obstacle_base_width * size_multiplier)
            obstacle_height = int(obstacle_base_height * size_multiplier)
            obstacles.append([WIDTH, HEIGHT - obstacle_height, obstacle_name, obstacle_width, obstacle_height])
            next_obstacle_distance = random.randint(min_gap, max_gap)  # Päivitä seuraavan esteen etäisyys

        # Esteiden liike ja poisto
        for obstacle in obstacles:
            obstacle[0] -= obstacle_speed
            if obstacle[0] < -obstacle[3]:
                obstacles.remove(obstacle)
                score += 1

        # Törmäyksen tarkistus
        for obstacle in obstacles:
            if player_x < obstacle[0] + obstacle[3] and \
               player_x + player_width > obstacle[0] and \
               player_y < obstacle[1] + obstacle[4] and \
               player_y + player_height > obstacle[1]:
                game_active = False

        # Taustan liike
        bg_x1 -= background_speed
        bg_x2 -= background_speed

        if bg_x1 <= -WIDTH:
            bg_x1 = WIDTH

        if bg_x2 <= -WIDTH:
            bg_x2 = WIDTH

    # Piirtäminen
    # Piirrä tausta
    screen.blit(background_image, (bg_x1, 0))
    screen.blit(background_image, (bg_x2, 0))

    # Piirrä läpinäkyvä kerros taustalle
    dark_overlay = pygame.Surface((WIDTH, HEIGHT))
    dark_overlay.set_alpha(128)  # Säädä läpinäkyvyyttä
    dark_overlay.fill((0, 0, 0))
    screen.blit(dark_overlay, (0, 0))

    # Piirrä pelaaja (sydän)
    draw_heart(screen, RED, player_x, player_y, player_width, player_height)
    
    # Piirrä esteet
    for obstacle in obstacles:
        color = COLORS[obstacle[2]]
        draw_human(screen, color, obstacle[0], HEIGHT - obstacle[4], obstacle[3], obstacle[4])
        # Lisää läpinäkyvä taustalaatikko tekstin taakse
        text_background = pygame.Surface((font.size(obstacle[2])[0], font.size(obstacle[2])[1]))
        text_background.set_alpha(128)  # Tekstilaatikon läpinäkyvyys
        text_background.fill(TRANSPARENT_BLACK)
        screen.blit(text_background, (obstacle[0], HEIGHT - obstacle[4] - 30))
        name_text = font.render(obstacle[2], True, WHITE)  # Tekstin väri valkoinen
        screen.blit(name_text, (obstacle[0], HEIGHT - obstacle[4] - 30))

    # Pisteet
    score_text = font.render(f"Pisteet: {score}", True, WHITE)  # Muutettu valkoiseksi
    screen.blit(score_text, (10, 10))

    if not game_active:
        if current_round < rounds:
            next_round_text = font.render(f"Kierros {current_round}/{rounds} päättyi! Pisteet: " + str(score), True, WHITE)
            replay_text = font.render("Paina R jatkaaksesi seuraavalle kierrokselle", True, WHITE)
            screen.blit(next_round_text, (WIDTH // 2 - next_round_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(replay_text, (WIDTH // 2 - replay_text.get_width() // 2, HEIGHT // 2 + 10))
        else:
            game_over_text = font.render("Peli päättyi! Lopulliset pisteet: " + str(score), True, WHITE)
            reset_text = font.render("Paina R pelataksesi uudelleen", True, WHITE)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(reset_text, (WIDTH // 2 - reset_text.get_width() // 2, HEIGHT // 2 + 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
