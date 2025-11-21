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
    try:
        # tenta salvar; se falhar por permissão (ex: OneDrive lock), não quebra o jogo
        with open(SAVE_FILE, "w") as f:
            import json
            json.dump(data, f)
    except PermissionError as e:
        # loga no terminal para diagnóstico, mas segue em frente
        print(f"WARNING: não foi possível salvar o jogo ({e})")
    except Exception as e:
        # captura qualquer outro erro de I/O sem interromper o jogo
        print(f"WARNING: erro ao salvar jogo: {e}")


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
    "defeat_screen": "Tela_Derrota.png",                # tela de derrota
    "life_meteor": "meteoro_vida.png"                   # meteoro especial que dá vida             
}

# ----------------------------------------------------------
# 🎚️ CONFIGURAÇÃO DE FASES (níveis)
# Cada nível pode ter um fundo diferente, quantidade de meteoros
# e velocidade distinta. Os arquivos de imagem podem ser alterados
# sem quebrar — o `load_image` gera um fallback quando ausentes.
# ----------------------------------------------------------
LEVELS = [
    {"name": "Nível 1", "bg": "fundo_espacial.png", "meteor_count": 5, "meteor_speed": 3, "threshold": 0},
    {"name": "Nível 2", "bg": "fundo_espacial2.jpg",   "meteor_count": 7, "meteor_speed": 5, "threshold": 10},
    {"name": "Nível 3", "bg": "fundo_espacial3.png",    "meteor_count": 8, "meteor_speed": 6, "threshold": 20},
]

# ----------------------------------------------------------
# 🖼️ CARREGAMENTO DE IMAGENS E SONS
# ----------------------------------------------------------
# Cores para fallback (caso os arquivos não existam)
WHITE = (255, 255, 255)
RED = (255, 60, 60)
BLUE = (60, 100, 255)
# Cor do texto principal e sombra para garantir legibilidade sobre fundos variados
TEXT_COLOR = (255, 235, 59)  # amarelo claro para sobressair
TEXT_SHADOW = (10, 10, 10)


def draw_text(surface, text, font_obj, color=TEXT_COLOR, topleft=None, center=None, shadow=True, shadow_offset=(2,2)):
    """Desenha texto com sombra opcional. Use `topleft=(x,y)` ou `center=(x,y)`."""
    txt_surf = font_obj.render(text, True, color)
    txt_rect = txt_surf.get_rect()
    if center is not None:
        txt_rect.center = center
    elif topleft is not None:
        txt_rect.topleft = topleft

    if shadow:
        sh = font_obj.render(text, True, TEXT_SHADOW)
        sh_rect = sh.get_rect()
        if center is not None:
            sh_rect.center = (txt_rect.centerx + shadow_offset[0], txt_rect.centery + shadow_offset[1])
        else:
            sh_rect.topleft = (txt_rect.left + shadow_offset[0], txt_rect.top + shadow_offset[1])
        surface.blit(sh, sh_rect)

    surface.blit(txt_surf, txt_rect)
    return txt_rect

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

def show_intro_screen():
    intro = True
    font_big = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)

    while intro:
        # fundo da primeira fase na tela de introdução
        screen.blit(backgrounds[0], (0,0))

        draw_text(screen, "SPACE ESCAPE", font_big, center=(WIDTH // 2, 100))

        # High Scores
        scores = load_highscores()
        y = 200
        draw_text(screen, "High Scores:", font_small, topleft=(WIDTH // 2 - 80, y))
        y += 40

        if scores:
            for i, s in enumerate(scores, start=1):
                draw_text(screen, f"{i}. {s}", font_small, topleft=(WIDTH // 2 - 50, y))
                y += 30
        else:
            draw_text(screen, "Pressione qualquer tecla para começar", font_small, topleft=(WIDTH // 2 - 80, y))
        
        draw_text(screen, "Pressione qualquer tecla para começar", font_small, center=(WIDTH // 2, HEIGHT - 100))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                intro = False


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


life_meteors = make_meteors(LIFE_METEOR_COUNT)

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
    # Regenera a lista de meteoros com a quantidade desejada quando troca de nível.
    # Isso evita que meteoros antigos fiquem espalhados pela tela quando a velocidade aumenta
    # e reduz artefatos visuais de muitos meteoros simultâneos.
    meteor_list = make_meteors(desired)
    # Posiciona os meteoros mais para cima ao trocar de nível para evitar que todos
    # apareçam de repente próximo da parte inferior da tela.
    for m in meteor_list:
        m.y = random.randint(-800, -40)

score = 0
lives = 3
# Pontuação necessária para vencer
WIN_SCORE = 30
# Incremento ao escolher "Continuar" após vitória
WIN_SCORE_STEP = 30
# razão do fim do jogo: None | 'victory' | 'defeat'
game_over_reason = None
# flag para evitar mostrar repetidamente a tela de vitória
victory_shown = False
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()
running = True
# tempo até o qual movimentos do mouse são ignorados (ms) — usado para evitar
# teleporte imediato da nave após um reinício quando o cursor ainda está
# fora da posição inicial.
mouse_ignore_until = 0

# Tela de escolha: continuar jogo salvo ou começar novo
def show_start_screen():
    font_big = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    running_screen = True

    while running_screen:
        screen.fill((10, 10, 30))

        draw_text(screen, "SPACE ESCAPE", font_big, center=(WIDTH//2, 150))

        continue_msg = font_small.render("1 - Continuar jogo salvo", True, WHITE)
        new_msg = font_small.render("2 - Novo jogo", True, WHITE)
        quit_msg = font_small.render("ESC - Sair", True, WHITE)

        # posiciona as opções em linhas separadas para evitar sobreposição
        x = WIDTH // 2 - 150
        y = 300
        gap = 40
        cont_pos = (x, y)
        new_pos = (x, y + gap)
        quit_pos = (x, y + 2 * gap)
        draw_text(screen, "1 - Continuar jogo salvo", font_small, topleft=cont_pos)
        draw_text(screen, "2 - Novo jogo", font_small, topleft=new_pos)
        draw_text(screen, "ESC - Sair", font_small, topleft=quit_pos)

        # cria rects para tornar as opções clicáveis
        cont_rect = continue_msg.get_rect(topleft=cont_pos)
        new_rect = new_msg.get_rect(topleft=new_pos)
        quit_rect = quit_msg.get_rect(topleft=quit_pos)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                # DEBUG: loga tecla pressionada
                try:
                    print(f"DEBUG: KEYDOWN {event.key}")
                except Exception:
                    pass
                if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                    print("DEBUG: selecionado 'continue' via teclado")
                    return "continue"
                if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    print("DEBUG: selecionado 'new' via teclado")
                    reset_save()
                    return "new"
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit


def show_end_menu(reason):
    """Mostra menu de fim de rodada (victory/defeat) com opções:
    C - Continuar, R - Reiniciar, ESC - Sair. Retorna a ação escolhida.
    """
    font_big = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)

    overlay_running = True
    while overlay_running:
        if reason == 'victory':
            screen.blit(victory_screen, (0, 0))
            draw_text(screen, "VITÓRIA!", font_big, center=(WIDTH // 2, 100))
        else:
            screen.blit(defeat_screen, (0, 0))
            draw_text(screen, "DERROTA", font_big, center=(WIDTH // 2, 100))

        # opções de menu dependem do motivo (vitória mostra Continuar)
        x = WIDTH // 2 - 100
        y = HEIGHT // 2
        gap = 40
        if reason == 'victory':
            hints = ["C - Continuar", "R - Reiniciar", "ESC - Sair"]
        else:
            # na derrota não mostramos a opção 'Continuar'
            hints = ["R - Reiniciar", "ESC - Sair"]

        # desenha as dicas dinamicamente
        for i, h in enumerate(hints):
            draw_text(screen, h, font_small, topleft=(x, y + i * gap))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if reason == 'victory':
                    if event.key == pygame.K_c:
                        return 'continue'
                    if event.key == pygame.K_r:
                        return 'restart'
                    if event.key == pygame.K_ESCAPE:
                        return 'quit'
                else:
                    # derrota: só reiniciar ou sair
                    if event.key == pygame.K_r:
                        return 'restart'
                    if event.key == pygame.K_ESCAPE:
                        return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN:
                # clique: no caso de vitória continua, em derrota reinicia
                if reason == 'victory':
                    return 'continue'
                else:
                    return 'restart'
                
start_option = show_start_screen()

if start_option == "continue":
    saved = load_game()
    if saved:
        score = saved["score"]
        lives = saved["lives"]
        current_level_idx = saved["level"]
        background = backgrounds[current_level_idx]
        meteor_speed = LEVELS[current_level_idx]["meteor_speed"]
        player_rect.centerx = saved["player_x"]
        player_rect.centery = saved["player_y"]
        # reajusta os meteoros conforme o nível salvo
        set_level(current_level_idx)


# ----------------------------------------------------------
# 🕹️ LOOP PRINCIPAL
# ----------------------------------------------------------

# mostra a tela introdutória uma vez antes do loop principal
show_intro_screen()

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
            # respawn mais acima para espaçar os meteoros e evitar acumulo na tela
            meteor.y = random.randint(-800, -40)
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

            # Verifica condição de vitória por pontuação: apenas mostramos a tela
            # de vitória se o jogador cruzou o limiar e também superou o maior
            # high score salvo (ou quando não há nenhum high score).
            if (not victory_shown) and score >= WIN_SCORE:
                highs = load_highscores()
                top_score = highs[0] if highs else -1
                # só exibe a tela de vitória quando passou o top score salvo
                if score > top_score:
                    action = show_end_menu('victory')
                    victory_shown = True
                    if action == 'continue':
                        # aumenta o alvo de vitória e permite próximas vitórias
                        WIN_SCORE += WIN_SCORE_STEP
                        victory_shown = False
                    elif action == 'restart':
                        # debug: log antes do reset
                        try:
                            print(f"DEBUG: restart(victory) requested - before reset: score={score}, lives={lives}, level={current_level_idx}")
                        except Exception:
                            pass
                        # reinicia estado do jogo
                        score = 0
                        lives = 3
                        bullets.clear()
                        meteor_list = make_meteors(LEVELS[0]["meteor_count"])
                        # recria meteoros de vida
                        life_meteors = make_meteors(LIFE_METEOR_COUNT)
                        # reseta posição da nave para o centro-bottom
                        player_rect.centerx = WIDTH // 2
                        player_rect.centery = HEIGHT - 60
                        # também reposiciona o cursor do mouse para evitar que a
                        # nave seja teleportada de volta pelo movimento do mouse
                        try:
                            pygame.mouse.set_pos((player_rect.centerx, player_rect.centery))
                        except Exception:
                            pass
                        # ignora movimentos do mouse por um curto período
                        mouse_ignore_until = pygame.time.get_ticks() + 300
                        set_level(0)
                        # reseta estado de vitória e objetivo
                        victory_shown = False
                        WIN_SCORE = WIN_SCORE_STEP
                        # interrompe o processamento restante dos meteoros neste frame
                        # para evitar que meteoros restantes somem pontos imediatamente
                        break
                        try:
                            print(f"DEBUG: restart(victory) done - after reset: score={score}, lives={lives}, level={current_level_idx}")
                        except Exception:
                            pass
                        lives = 3
                        bullets.clear()
                        meteor_list = make_meteors(LEVELS[0]["meteor_count"])
                        # recria meteoros de vida
                        life_meteors = make_meteors(LIFE_METEOR_COUNT)
                        # reseta posição da nave para o centro-bottom
                        player_rect.centerx = WIDTH // 2
                        player_rect.centery = HEIGHT - 60
                        # também reposiciona o cursor do mouse quando possível
                        try:
                            pygame.mouse.set_pos((player_rect.centerx, player_rect.centery))
                        except Exception:
                            pass
                        # ignora movimentos do mouse por um curto período
                        mouse_ignore_until = pygame.time.get_ticks() + 300
                        set_level(0)
                        # reseta estado de vitória e objetivo
                        victory_shown = False
                        WIN_SCORE = WIN_SCORE_STEP
                    elif action == 'quit':
                        game_over_reason = 'victory'
                        running = False
                        break

        # Colisão
        if meteor.colliderect(player_rect):
            lives -= 1
            meteor.y = random.randint(-800, -40)
            meteor.x = random.randint(0, WIDTH - meteor.width)
            if sound_hit:
                sound_hit.play()
            if lives <= 0:
                    action = show_end_menu('defeat')
                    if action == 'restart' or action == 'continue':
                        try:
                            print(f"DEBUG: restart(defeat) requested - before reset: score={score}, lives={lives}, level={current_level_idx}")
                        except Exception:
                            pass
                        # reinicia o jogo quando o jogador escolhe reiniciar
                        score = 0
                        lives = 3
                        bullets.clear()
                        meteor_list = make_meteors(LEVELS[0]["meteor_count"])
                        # recria meteoros de vida
                        life_meteors = make_meteors(LIFE_METEOR_COUNT)
                        # reseta posição da nave
                        player_rect.centerx = WIDTH // 2
                        player_rect.centery = HEIGHT - 60
                        try:
                            pygame.mouse.set_pos((player_rect.centerx, player_rect.centery))
                        except Exception:
                            pass
                        mouse_ignore_until = pygame.time.get_ticks() + 300
                        set_level(0)
                        # interrompe o loop de meteoros após reiniciar para evitar
                        # acréscimos de pontuação no mesmo frame
                        break
                        try:
                            print(f"DEBUG: restart(defeat) done - after reset: score={score}, lives={lives}, level={current_level_idx}")
                        except Exception:
                            pass
                        # reseta estado de vitória
                        victory_shown = False
                        WIN_SCORE = WIN_SCORE_STEP
                        lives = 3
                        bullets.clear()
                        meteor_list = make_meteors(LEVELS[0]["meteor_count"])
                        # recria meteoros de vida
                        life_meteors = make_meteors(LIFE_METEOR_COUNT)
                        # reseta posição da nave
                        player_rect.centerx = WIDTH // 2
                        player_rect.centery = HEIGHT - 60
                        try:
                            pygame.mouse.set_pos((player_rect.centerx, player_rect.centery))
                        except Exception:
                            pass
                        mouse_ignore_until = pygame.time.get_ticks() + 300
                        set_level(0)
                        # reseta estado de vitória
                        victory_shown = False
                        WIN_SCORE = WIN_SCORE_STEP
                    elif action == 'quit':
                        game_over_reason = 'defeat'
                        running = False
                        break
        
    # --- Movimento dos meteoros de vida (meteoros especiais) ---
    for meteor in life_meteors:
        meteor.y += meteor_speed  # pode usar outra velocidade se quiser

        # Se sair da tela, reposiciona
        if meteor.y > HEIGHT:
            meteor.y = random.randint(-200, -40)
            meteor.x = random.randint(0, WIDTH - meteor.width)

        # Colisão com a nave -> ganha vida extra
        if meteor.colliderect(player_rect):
            # só ganha vida se estiver abaixo do máximo de 3
            if lives < 3:
                lives += 1

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
                # 'destrói' o meteoro reposicionando-o lá em cima (mais distante)
                meteor.y = random.randint(-800, -40)
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
    draw_text(screen, f"Pontos: {score}   Vidas: {lives}", font, topleft=(10, 10))

    # Exibe o nível atual
    level_name = LEVELS[current_level_idx]["name"]
    draw_text(screen, f"{level_name}", font, topleft=(WIDTH - 180, 10))

    save_game() # salva automaticamente durante o jogo

    pygame.display.flip()


# Atualiza High Scores
update_highscores(score)

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
final_score_font = pygame.font.Font(None, 48)
draw_text(screen, f"Pontuação final: {score}", final_score_font, center=(WIDTH // 2, HEIGHT - 50))

pygame.display.flip()

waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            waiting = False

reset_save() # evita carregar um jogo já terminado

pygame.quit()
