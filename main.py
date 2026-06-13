import pygame
import sys
import os

pygame.init()

# ===== TELA =====
info = pygame.display.Info()
LARGURA = info.current_w
ALTURA = info.current_h

tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
pygame.display.set_caption("Travessia Segura")

# ===== TAMANHOS =====
TAM_JOGADOR = int(min(LARGURA, ALTURA) * 0.40)
LARG_CAMINHAO = int(LARGURA * 0.50)
ALT_CAMINHAO = int(ALTURA * 0.30)

FONTE_NORMAL = int(ALTURA * 0.03)
FONTE_GRANDE = int(ALTURA * 0.045)

ALTURA_FAIXA = ALTURA // 3

# ===== CORES =====
MARROM = (120, 70, 20)
VERDE = (0, 220, 0)
VERMELHO = (220, 0, 0)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (80, 80, 80)
AMARELO = (255, 220, 0)
AZUL = (0, 120, 255)

# ===== FONTES =====
fonte = pygame.font.SysFont(None, FONTE_NORMAL)
fonte_grande = pygame.font.SysFont(None, FONTE_GRANDE)

clock = pygame.time.Clock()

VEL_JOGADOR = 120
VEL_CAMINHAO = 100

# ===== CARREGAR IMAGENS (com fallback robusto p/ Pydroid/Android) =====
PASTAS_BUSCA = []
try:
    PASTAS_BUSCA.append(os.path.dirname(os.path.abspath(__file__)))
except NameError:
    pass
PASTAS_BUSCA.append(os.getcwd())
PASTAS_BUSCA.append(os.path.join(os.getcwd(), "game"))


def carregar_imagem(nome, tamanho):
    caminho_encontrado = None
    for pasta in PASTAS_BUSCA:
        tentativa = os.path.join(pasta, nome)
        if os.path.exists(tentativa):
            caminho_encontrado = tentativa
            break

    if caminho_encontrado is None:
        caminho_encontrado = nome

    try:
        img = pygame.image.load(caminho_encontrado)
        try:
            img = img.convert_alpha()
        except Exception:
            try:
                img = img.convert()
            except Exception:
                pass
        img = pygame.transform.scale(img, tamanho)
        print(f"[OK] Imagem carregada: {caminho_encontrado}")
        return img
    except Exception as ex:
        print(f"[AVISO] Falha ao carregar {nome} ({ex}) - usando fallback.")
        return None


img_jogador = carregar_imagem("jogador.png", (TAM_JOGADOR, TAM_JOGADOR))
img_rua = carregar_imagem("rua.png", (LARGURA, ALTURA))
img_caminhao = carregar_imagem("caminhao.png", (LARG_CAMINHAO, ALT_CAMINHAO))

# ===== ESTADO =====
estado = "MENU"

# ===== BOTÕES =====
btn_jogar = pygame.Rect(LARGURA//2 - 150, ALTURA//2 - 80, 300, 70)
btn_credito = pygame.Rect(LARGURA//2 - 150, ALTURA//2 + 20, 300, 70)
btn_voltar = pygame.Rect(50, 50, 200, 60)

clicado = None
click_timer = 0


# ===== REINICIAR JOGO =====
def reiniciar():
    jogador = pygame.Rect(
        LARGURA // 2 - TAM_JOGADOR // 2,
        40,
        TAM_JOGADOR,
        TAM_JOGADOR
    )
    return jogador, False, False, False, False, False, False, None


(
    jogador,
    atravessando,
    venceu,
    perdeu,
    tentou_no_vermelho,
    animacao_atropelamento,
    esperando_atropelamento,
    caminhao
) = reiniciar()

# ===== SEMÁFORO =====
vermelho = True
tempo = 0


def desenhar_botao(rect, cor, texto):
    global clicado
    scale = 0.95 if clicado == rect else 1.0
    r = rect.copy()
    if scale != 1.0:
        r.inflate_ip(-20, -10)
    pygame.draw.rect(tela, cor, r, border_radius=10)
    txt = fonte.render(texto, True, PRETO)
    tela.blit(txt, txt.get_rect(center=r.center))


# ========================= LOOP =========================
rodando = True
while rodando:
    dt = clock.tick(60)
    mx, my = pygame.mouse.get_pos()

    if click_timer > 0:
        click_timer -= dt
        if click_timer <= 0:
            clicado = None

    # ================= MENU =================
    if estado == "MENU":
        tela.fill(PRETO)

        titulo = fonte_grande.render("Bem vindo ao humer", True, BRANCO)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA//2, 150)))

        desenhar_botao(btn_jogar, VERDE, "JOGAR")
        desenhar_botao(btn_credito, AZUL, "CRÉDITOS")

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                rodando = False
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn_jogar.collidepoint(e.pos):
                    clicado = btn_jogar
                    click_timer = 120
                    estado = "JOGO"
                    (
                        jogador, atravessando, venceu, perdeu,
                        tentou_no_vermelho, animacao_atropelamento,
                        esperando_atropelamento, caminhao
                    ) = reiniciar()
                    vermelho = True
                    tempo = 0
                elif btn_credito.collidepoint(e.pos):
                    clicado = btn_credito
                    click_timer = 120
                    estado = "CREDITO"

        pygame.display.update()
        continue

    # ================= CRÉDITOS =================
    if estado == "CREDITO":
        tela.fill(PRETO)

        titulo_cred = fonte_grande.render("CRÉDITOS", True, AMARELO)
        tela.blit(titulo_cred, titulo_cred.get_rect(center=(LARGURA//2, 120)))

        lista_creditos = [
            ("Carlos:", "software", AZUL),
            ("Nauan:", "líder do projeto", AMARELO),
            ("Marcos:", "ideia inicial", VERDE),
            ("Izaias:", "farmou aura", (180, 0, 255)),
            ("Adriano:", "atropelou Izaias", VERMELHO),
            ("Igor:", "estava lá", (0, 255, 255))
        ]

        y_inicial = ALTURA // 2 - 120
        espacamento = int(ALTURA * 0.05)

        for i, (nome, funcao, cor_funcao) in enumerate(lista_creditos):
            pos_y = y_inicial + (i * espacamento)

            txt_nome = fonte.render(nome, True, BRANCO)
            rect_nome = txt_nome.get_rect(
                right=LARGURA//2 - 20,
                centery=pos_y
            )
            tela.blit(txt_nome, rect_nome)

            txt_funcao = fonte.render(funcao, True, cor_funcao)
            rect_funcao = txt_funcao.get_rect(
                left=LARGURA//2 + 20,
                centery=pos_y
            )
            tela.blit(txt_funcao, rect_funcao)	

        pygame.draw.rect(tela, CINZA, btn_voltar, border_radius=8)
        vtxt = fonte.render("VOLTAR", True, BRANCO)
        tela.blit(vtxt, vtxt.get_rect(center=btn_voltar.center))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                rodando = False
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn_voltar.collidepoint(e.pos):
                    clicado = btn_voltar
                    click_timer = 120
                    estado = "MENU"

        pygame.display.update()
        continue

    # ================= JOGO =================
    if estado == "JOGO":

        if not atravessando and not venceu and not perdeu and not animacao_atropelamento:
            tempo += dt
            limite = 4500 if vermelho else 2800
            if tempo >= limite:
                vermelho = not vermelho
                tempo = 0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                rodando = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    estado = "MENU"
            if e.type == pygame.MOUSEBUTTONDOWN:
                if venceu or perdeu:
                    (
                        jogador, atravessando, venceu, perdeu,
                        tentou_no_vermelho, animacao_atropelamento,
                        esperando_atropelamento, caminhao
                    ) = reiniciar()
                    vermelho = True
                    tempo = 0
                elif not atravessando and not venceu and not perdeu:
                    atravessando = True
                    if vermelho:
                        tentou_no_vermelho = True

        meio = ALTURA_FAIXA + (ALTURA_FAIXA // 2)

        if atravessando and not perdeu:
            if not esperando_atropelamento:
                jogador.y += int(VEL_JOGADOR * dt / 1000)

            if tentou_no_vermelho and jogador.y >= meio and not animacao_atropelamento:
                jogador.y = meio
                atravessando = False
                esperando_atropelamento = True
                caminhao = pygame.Rect(
                    -LARG_CAMINHAO,
                    jogador.y - ALT_CAMINHAO // 4,
                    LARG_CAMINHAO,
                    ALT_CAMINHAO
                )
                animacao_atropelamento = True

            if jogador.y >= ALTURA_FAIXA * 2:
                venceu = True
                atravessando = False

        if animacao_atropelamento and caminhao:
            caminhao.x += int(VEL_CAMINHAO * dt / 1000)
            if caminhao.x + 120 > jogador.x and caminhao.colliderect(jogador):
                perdeu = True
                animacao_atropelamento = False

        if perdeu:
            tela.fill(PRETO)
            msg = fonte_grande.render("Adriano te atropelou", True, BRANCO)
            tela.blit(msg, msg.get_rect(center=(LARGURA//2, ALTURA//2)))
            pygame.display.update()
            continue

        if venceu:
            tela.fill(PRETO)
            m1 = fonte.render("Você atravessou com segurança!", True, BRANCO)
            m2 = fonte.render("Parabéns!", True, BRANCO)
            tela.blit(m1, (50, ALTURA//2 - 40))
            tela.blit(m2, (50, ALTURA//2))
            pygame.display.update()
            continue

        # ===== DESENHO =====
        if img_rua is not None:
            tela.blit(img_rua, (0, 0))
        else:
            tela.fill(BRANCO)
            pygame.draw.rect(tela, MARROM, (0, 0, LARGURA, ALTURA_FAIXA))
            pygame.draw.rect(tela, MARROM, (0, ALTURA_FAIXA*2, LARGURA, ALTURA_FAIXA))
            pygame.draw.rect(tela, CINZA, (0, ALTURA_FAIXA, LARGURA, ALTURA_FAIXA))
            for i in range(0, LARGURA, 90):
                pygame.draw.rect(tela, AMARELO, (i, ALTURA//2, 35, 6))

        cor = VERMELHO if vermelho else VERDE
        pygame.draw.circle(tela, cor, (LARGURA - 70, 70), 25)

        if img_jogador is not None:
            tela.blit(img_jogador, (jogador.x, jogador.y))
        else:
            pygame.draw.rect(tela, (0, 90, 255), jogador, border_radius=8)

        if caminhao:
            if img_caminhao is not None:
                tela.blit(img_caminhao, (caminhao.x, caminhao.y))
            else:
                pygame.draw.rect(tela, (200, 0, 0), caminhao, border_radius=6)

        pygame.display.update()

pygame.quit()
sys.exit()
