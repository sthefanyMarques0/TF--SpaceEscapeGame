##############################################################
###               S P A C E     E S C A P E                ###
##############################################################
###                  versao Alpha 0.3                      ###
##############################################################
### Objetivo: desviar dos meteoros que caem.               ###
### Cada colisão tira uma vida. Sobreviva o máximo que     ###
### conseguir!                                             ###
##############################################################
### Prof. Filipo Novo Mor - github.com/ProfessorFilipo     ###
##############################################################

import pygame
import random
import os

# Cria arquivos de salvamento e funções auxiliares
SAVE_FILE = "savegame.json"

def save_game():
    data = {
        "score": score,
        "lives": lives,
        "level": current_level_idx,
        "player_x": player_rect.centerx,
        "player_y": player_rect.centery
    }
    with open(SAVE_FILE, "w") as f:
        import json
        json.dump(data, f)


def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    
    try:
        import json
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        data = {}
        return None


def reset_save():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


# Inicializa o PyGame
pygame.init()
# Inicializa o mixer de áudio explicitamente; em alguns ambientes o mixer
# pode falhar (sem dispositivo de áudio). Detectamos isso e prosseguimos
# sem sons quando não disponível.
mixer_initialized = False
try:
    pygame.mixer.init()
    mixer_initialized = True
except pygame.error:
    mixer_initialized = False

# ----------------------------------------------------------
# 🔧 CONFIGURAÇÕES GERAIS DO JOGO
# ----------------------------------------------------------
WIDTH, HEIGHT = 800, 600

# Constantes e funções de High Score
HIGHSCORES_FILE = "highscores.txt"
MAX_HIGHSCORES = 5

def load_highscores():
    scores = []
    if os.path.exists(HIGHSCORES_FILE):
        with open(HIGHSCORES_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line.isdigit():
                    scores.append(int(line))
    scores.sort(reverse=True)
    return scores[:MAX_HIGHSCORES]


def save_highscores(scores):
    with open(HIGHSCORES_FILE, "w") as f:
        for s in scores[:MAX_HIGHSCORES]:
            f.write(str(s) + "\n")


def update_highscores(new_score):
    scores = load_highscores()
    scores.append(new_score)
    scores.sort(reverse=True)
    save_highscores(scores)

FPS = 60
pygame.display.set_caption("🚀 Space Escape")

# ----------------------------------------------------------
# 🧩 SEÇÃO DE ASSETS (troque os arquivos de assets aqui)
# ----------------------------------------------------------
# Dica: coloque as imagens e sons na mesma pasta do arquivo .py
# e troque apenas os nomes abaixo.

ASSETS = {
    "background": "fundo_espacial.jpg",                         # imagem de fundo (padrão)
    "player": "nave001.png",                                    # imagem da nave
    "meteor": "meteoro001.png",                                 # imagem do meteoro
    "sound_point": "classic-game-action-positive-5-224402.mp3", # som ao desviar com sucesso
    "sound_hit": "stab-f-01-brvhrtz-224599.mp3",                # som de colisão
    "music": "distorted-future-363866.mp3",           # música de fundo. direitos: Music by Maksym Malko from Pixabay
    "victory_screen": "Tela_vitoria.png",              # tela de vitória
    "defeat_screen": "Tela_Derrota.png"                # tela de derrota
}

# ----------------------------------------------------------
# 🎚️ CONFIGURAÇÃO DE FASES (níveis)
# Cada nível pode ter um fundo diferente, quantidade de meteoros
# e velocidade distinta. Os arquivos de imagem podem ser alterados
# sem quebrar — o `load_image` gera um fallback quando ausentes.
# ----------------------------------------------------------
LEVELS = [
    {"name": "Nível 1", "bg": "fundo_espacial.png", "meteor_count": 5, "meteor_speed": 5, "threshold": 0},
    {"name": "Nível 2", "bg": "fundo_espacial2.jpg",   "meteor_count": 7, "meteor_speed": 7, "threshold": 10},
    {"name": "Nível 3", "bg": "fundo_espacial3.png",    "meteor_count": 10, "meteor_speed": 9, "threshold": 20},
]

# ----------------------------------------------------------
# 🖼️ CARREGAMENTO DE IMAGENS E SONS
# ----------------------------------------------------------
# Cores para fallback (caso os arquivos não existam)
WHITE = (255, 255, 255)
RED = (255, 60, 60)
BLUE = (60, 100, 255)

# Tela do jogo
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Função auxiliar para carregar imagens de forma segura
def load_image(filename, fallback_color, size=None):
    if os.path.exists(filename):
        img = pygame.image.load(filename).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    else:
        # Gera uma superfície simples colorida se a imagem não existir
        surf = pygame.Surface(size or (50, 50))
        surf.fill(fallback_color)
        return surf

# Carrega imagens
player_img = load_image(ASSETS["player"], BLUE, (80, 60))
meteor_base = load_image("meteoro001.png", RED, (40, 40))

life_meteor_img = load_image(ASSETS["life_meteor"], (0, 255, 0), (40, 40))
LIFE_METEOR_COUNT = 2


# Gera alguns frames rotacionados a partir da imagem
meteor_frames = []
angles = [-10, -5, 0, 5, 10, 5, 0, -5]  # sequência para dar impressão de "balanço"

for ang in angles:
    frame = pygame.transform.rotate(meteor_base, ang)
    meteor_frames.append(frame)

meteor_anim_index = 0
meteor_anim_timer = 0
METEOR_ANIM_SPEED = 5  # quanto menor, mais rápida a troca de frames


# Carrega imagens de telas finais (vitória e derrota)
victory_screen = load_image(ASSETS["victory_screen"], WHITE, (WIDTH, HEIGHT))
defeat_screen = load_image(ASSETS["defeat_screen"], WHITE, (WIDTH, HEIGHT))

# Carrega fundos das fases
backgrounds = []
for lvl in LEVELS:
    bg_img = load_image(lvl.get("bg", ASSETS["background"]), WHITE, (WIDTH, HEIGHT))
    backgrounds.append(bg_img)

# Nível inicial (index em LEVELS)
current_level_idx = 0
background = backgrounds[current_level_idx]

# Sons
def load_sound(filename):
    # Se o mixer não estiver disponível, não tentamos carregar sons
    if not mixer_initialized:
        return None
    if os.path.exists(filename):
        return pygame.mixer.Sound(filename)
    return None

sound_point = load_sound(ASSETS["sound_point"])
sound_hit = load_sound(ASSETS["sound_hit"])

# Música de fundo (opcional)
if mixer_initialized and os.path.exists(ASSETS["music"]):
    try:
        pygame.mixer.music.load(ASSETS["music"])
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)  # loop infinito
    except pygame.error:
        # Se por algum motivo a música falhar ao carregar, ignoramos
        pass

# ----------------------------------------------------------
# 🧠 VARIÁVEIS DE JOGO
# ----------------------------------------------------------
player_rect = player_img.get_rect(center=(WIDTH // 2, HEIGHT - 60))
player_speed = 7

# --- Armas / Projéteis ---
# lista de projéteis ativos (cada projétil é um pygame.Rect)
bullets = []
# velocidade dos projéteis (pixels por frame)
BULLET_SPEED = 12
# tamanho do projétil
BULLET_SIZE = (6, 12)
# cooldown entre tiros em milissegundos
FIRE_COOLDOWN_MS = 200
last_shot_time = 0

def make_meteors(count):
    lst = []
    for _ in range(count):
        x = random.randint(0, WIDTH - 40)
        y = random.randint(-500, -40)
        lst.append(pygame.Rect(x, y, 40, 40))
    return lst

# Inicializa meteoros de acordo com o nível inicial
meteor_list = make_meteors(LEVELS[current_level_idx]["meteor_count"])
meteor_speed = LEVELS[current_level_idx]["meteor_speed"]

def set_level(idx):
    global current_level_idx, background, meteor_list, meteor_speed
    if idx < 0 or idx >= len(LEVELS):
        return
    current_level_idx = idx
    background = backgrounds[current_level_idx]
    meteor_speed = LEVELS[current_level_idx]["meteor_speed"]
    # Ajusta a quantidade de meteoros para o nível
    desired = LEVELS[current_level_idx]["meteor_count"]
    if len(meteor_list) < desired:
        # adiciona novos meteoros
        meteor_list.extend(make_meteors(desired - len(meteor_list)))
    elif len(meteor_list) > desired:
        # reduz a lista (mantém os primeiros)
        meteor_list = meteor_list[:desired]

score = 0
lives = 3
# Pontuação necessária para vencer
WIN_SCORE = 30
# razão do fim do jogo: None | 'victory' | 'defeat'
game_over_reason = None
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()
running = True

# ----------------------------------------------------------
# 🕹️ LOOP PRINCIPAL
# ----------------------------------------------------------
while running:
    clock.tick(FPS)
    screen.blit(background, (0, 0))

    # --- Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Disparo: clique esquerdo do mouse ou barra de espaço
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # botão esquerdo
                now = pygame.time.get_ticks()
                if now - last_shot_time >= FIRE_COOLDOWN_MS:
                    # cria um projétil na frente da nave
                    bx = player_rect.centerx - BULLET_SIZE[0] // 2
                    by = player_rect.top - BULLET_SIZE[1]
                    bullets.append(pygame.Rect(bx, by, BULLET_SIZE[0], BULLET_SIZE[1]))
                    last_shot_time = now
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                now = pygame.time.get_ticks()
                if now - last_shot_time >= FIRE_COOLDOWN_MS:
                    bx = player_rect.centerx - BULLET_SIZE[0] // 2
                    by = player_rect.top - BULLET_SIZE[1]
                    bullets.append(pygame.Rect(bx, by, BULLET_SIZE[0], BULLET_SIZE[1]))
                    last_shot_time = now

    # --- Movimento do jogador via mouse (apenas mouse ativa o movimento) ---
    # Obtém a posição do cursor e move a nave para essa posição
    mx, my = pygame.mouse.get_pos()
    player_rect.centerx = mx
    player_rect.centery = my
    # Garante que a nave permaneça dentro da tela
    if player_rect.left < 0:
        player_rect.left = 0
    if player_rect.right > WIDTH:
        player_rect.right = WIDTH
    if player_rect.top < 0:
        player_rect.top = 0
    if player_rect.bottom > HEIGHT:
        player_rect.bottom = HEIGHT

    # --- Movimento dos meteoros ---
    for meteor in meteor_list:
        meteor.y += meteor_speed

        # Saiu da tela → reposiciona e soma pontos
        if meteor.y > HEIGHT:
            meteor.y = random.randint(-100, -40)
            meteor.x = random.randint(0, WIDTH - meteor.width)
            score += 1
            if sound_point:
                sound_point.play()

            # Verifica troca de nível com base na pontuação
            # seleciona o maior nível cujo threshold <= score
            new_level_idx = current_level_idx
            for idx in range(len(LEVELS)):
                if score >= LEVELS[idx]["threshold"]:
                    new_level_idx = idx
            if new_level_idx != current_level_idx:
                set_level(new_level_idx)

            # Verifica condição de vitória por pontuação
            if score >= WIN_SCORE:
                game_over_reason = 'victory'
                running = False

        # Colisão
        if meteor.colliderect(player_rect):
            lives -= 1
            meteor.y = random.randint(-100, -40)
            meteor.x = random.randint(0, WIDTH - meteor.width)
            if sound_hit:
                sound_hit.play()
            if lives <= 0:
                game_over_reason = 'defeat'
                running = False
        
    # --- Movimento dos meteoros de vida (meteoros especiais) ---
    for meteor in life_meteors:
        meteor.y += meteor_speed  # pode usar outra velocidade se quiser

        # Se sair da tela, reposiciona
        if meteor.y > HEIGHT:
            meteor.y = random.randint(-200, -40)
            meteor.x = random.randint(0, WIDTH - meteor.width)

        # Colisão com a nave -> ganha vida extra
        if meteor.colliderect(player_rect):
            # aqui tu decide se é +1 ou +2 vidas
            lives += 1
            # se quiser limitar o máximo de vidas:
            # lives = min(lives + 1, 5)

            # reposiciona o meteoro para cima
            meteor.y = random.randint(-200, -40)
            meteor.x = random.randint(0, WIDTH - meteor.width)

    
    # Atualiza animação dos meteoros
    meteor_anim_timer += 1
    if meteor_anim_timer >= METEOR_ANIM_SPEED:
        meteor_anim_timer = 0
        meteor_anim_index = (meteor_anim_index + 1) % len(meteor_frames)
    

    # --- Movimento dos projéteis ---
    # atualiza posição, remove projéteis fora da tela e detecta colisões
    for b in bullets[:]:
        b.y -= BULLET_SPEED
        # projétil saiu da tela
        if b.bottom < 0:
            try:
                bullets.remove(b)
            except ValueError:
                pass
            continue

        # verifica colisão com meteoros regulares
        hit = False
        for meteor in meteor_list:
            if b.colliderect(meteor):
                # 'destrói' o meteoro reposicionando-o lá em cima
                meteor.y = random.randint(-200, -40)
                meteor.x = random.randint(0, WIDTH - meteor.width)
                # aumenta a pontuação por destruir
                score += 2
                if sound_point:
                    sound_point.play()
                # remove o projétil
                try:
                    bullets.remove(b)
                except ValueError:
                    pass
                hit = True
                break
        if hit:
            # pula para o próximo projétil
            continue


    # --- Desenha tudo ---
    screen.blit(player_img, player_rect)

    # Desenha projéteis
    for b in bullets:
        pygame.draw.rect(screen, WHITE, b)

    for meteor in meteor_list:
        frame = meteor_frames[meteor_anim_index]
        # centraliza o frame no rect (porque a imagem rotacionada pode ficar maior)
        rect = frame.get_rect(center=meteor.center)
        screen.blit(frame, rect)
        
    # Meteoros de vida
    for meteor in life_meteors:
        screen.blit(life_meteor_img, meteor)


    # --- Exibe pontuação e vidas ---
    text = font.render(f"Pontos: {score}   Vidas: {lives}", True, WHITE)
    screen.blit(text, (10, 10))

    # Exibe o nível atual
    level_name = LEVELS[current_level_idx]["name"]
    level_text = font.render(f"{level_name}", True, WHITE)
    screen.blit(level_text, (WIDTH - 180, 10))

    pygame.display.flip()

# ----------------------------------------------------------
# 🏁 TELA DE FIM DE JOGO
# ----------------------------------------------------------
if mixer_initialized:
    try:
        pygame.mixer.music.stop()
    except pygame.error:
        pass

# Exibe a tela apropriada (vitória ou derrota)
if game_over_reason == 'victory':
    screen.blit(victory_screen, (0, 0))
elif game_over_reason == 'defeat':
    screen.blit(defeat_screen, (0, 0))
else:
    # Fallback genérico
    screen.fill((20, 20, 20))

# Exibe a pontuação final no rodapé
final_score_text = pygame.font.Font(None, 48).render(f"Pontuação final: {score}", True, WHITE)
final_score_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
screen.blit(final_score_text, final_score_rect)

pygame.display.flip()

waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            waiting = False

pygame.quit()
