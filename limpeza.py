import os
import random
import sys
import time

# Habilita cores ANSI no console
os.system('')

class Cores:
    RESET = '\033[0m'
    NEGRITO = '\033[1m'
    VERMELHO = '\033[91m'
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CIANO = '\033[96m'
    BRANCO = '\033[97m'

PALETA_CORES = [
    Cores.AZUL,
    Cores.AMARELO,
    Cores.MAGENTA,
    Cores.VERDE,
    Cores.CIANO,
    Cores.BRANCO
]

ITENS_DISPONIVEIS = {
    "1": ("Overclock", "Aumenta o dano do proximo tiro em +1 (Acumulativo)"),
    "2": ("Expurgar", "Ejeta a celula atual e revela seu conteudo a todos"),
    "3": ("Trava EMP", "Escolha um oponente para perder o proximo turno"),
    "4": ("Bateria Reserva", "Recupera +1 de vida (maximo 5)"),
    "5": ("Inversor", "Inverte a polaridade da celula no cano (Viva <-> Neutra)"),
    "6": ("Scanner", "Verifica secretamente a PROXIMA carga (a que vem apos o tiro atual)"),
    "7": ("Escudo", "Bloqueia o proximo dano de tiro (Dura ate o inicio do seu proximo turno)"),
    "8": ("Injetor", "Adiciona 1 carga aleatoria (Viva/Neutra) no tambor")
}

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar(segundos=1.0):
    time.sleep(segundos)

class JogoDueloMultiplayer:
    def __init__(self, nomes, is_bot):
        self.nomes = nomes
        self.is_bot = is_bot
        self.total_jogadores = len(nomes)
        self.max_hp = 5
        self.max_inv = 6
        self.hp = [self.max_hp for _ in nomes]
        self.inventarios = [[] for _ in nomes]
        self.emp_ativo = [False for _ in nomes]
        self.escudo_ativo = [False for _ in nomes]
        self.escudo_criado_no_turno = [False for _ in nomes]
        self.turno_atual = 0
        self.camara = []
        self.dano_acumulado = 1
        self.bot_conhece_proxima = None

    def vivos(self):
        return [i for i, vida in enumerate(self.hp) if vida > 0]

    def eliminados(self):
        return [i for i, vida in enumerate(self.hp) if vida <= 0]

    def proximo_jogador(self):
        if len(self.vivos()) <= 1:
            return
        # Ao passar a vez, qualquer escudo criado neste turno perde a imunidade de recém-criado
        self.escudo_criado_no_turno[self.turno_atual] = False

        idx = self.turno_atual
        while True:
            idx = (idx + 1) % self.total_jogadores
            if self.hp[idx] > 0:
                self.turno_atual = idx
                break

    def cabecalho(self):
        limpar_tela()
        print(f"{Cores.CIANO}{Cores.NEGRITO}========================================================================{Cores.RESET}")
        print(f"{Cores.MAGENTA}{Cores.NEGRITO}                 TERMINAL OVERCHARGE: CYBER DUEL                        {Cores.RESET}")
        print(f"{Cores.CIANO}{Cores.NEGRITO}========================================================================{Cores.RESET}\n")

        for i, nome in enumerate(self.nomes):
            cor = PALETA_CORES[i % len(PALETA_CORES)]
            tipo = " [BOT]" if self.is_bot[i] else ""
            if self.hp[i] > 0:
                barra_hp = f"{Cores.VERDE}{'█' * self.hp[i]}{Cores.RESET}{'░' * (self.max_hp - self.hp[i])}"
                status_tags = []
                if self.emp_ativo[i]:
                    status_tags.append(f"{Cores.VERMELHO}[EMP BLOQUEADO]{Cores.RESET}")
                if self.escudo_ativo[i]:
                    status_tags.append(f"{Cores.CIANO}[🛡️ ESCUDO ATIVO]{Cores.RESET}")
                if not status_tags:
                    status_tags.append(f"{Cores.VERDE}[ATIVO]{Cores.RESET}")

                status_str = " ".join(status_tags)
                itens_str = ', '.join(self.inventarios[i]) if self.inventarios[i] else "Vazio"
                print(f" {cor}{Cores.NEGRITO}{nome + tipo:<14}{Cores.RESET} | HP: {barra_hp} ({self.hp[i]}/{self.max_hp}) | {status_str}")
                print(f"                 | Itens ({len(self.inventarios[i])}/{self.max_inv}): {itens_str}")
            else:
                print(f" {Cores.VERMELHO}{Cores.NEGRITO}{nome + tipo:<14}{Cores.RESET} | {Cores.VERMELHO}[ELIMINADO / MODO FANTASMA 👻]{Cores.RESET}")
            print("-" * 72)

        if self.dano_acumulado > 1:
            print(f"{Cores.VERMELHO}{Cores.NEGRITO}⚡ POTÊNCIA DE FOGO: {self.dano_acumulado} DE DANO ACUMULADO! ⚡{Cores.RESET}\n")
        else:
            print()

    def aplicar_sabotagem_espectral(self):
        mortos = self.eliminados()
        sobreviventes = self.vivos()

        if not mortos or not sobreviventes:
            return

        limpar_tela()
        print(f"{Cores.MAGENTA}{Cores.NEGRITO}========================================================================{Cores.RESET}")
        print(f"{Cores.MAGENTA}{Cores.NEGRITO}             👻 FASE ESPECTRAL: INTERVENÇÃO DOS ELIMINADOS 👻            {Cores.RESET}")
        print(f"{Cores.MAGENTA}{Cores.NEGRITO}========================================================================{Cores.RESET}")
        print("Cada jogador eliminado tem direito a sabotar 1 item de qualquer sobrevivente.\n")
        pausar(1.5)

        for m in mortos:
            alvos_com_itens = [s for s in sobreviventes if len(self.inventarios[s]) > 0]
            if not alvos_com_itens:
                print(f"{Cores.MAGENTA}Fantasma {self.nomes[m]}: Nenhum sobrevivente possui itens para sabotar.{Cores.RESET}")
                pausar(1.2)
                continue

            if self.is_bot[m]:
                alvo = max(alvos_com_itens, key=lambda s: (self.hp[s], len(self.inventarios[s])))
                item_escolhido = random.choice(self.inventarios[alvo])
                self.inventarios[alvo].remove(item_escolhido)
                print(f"{Cores.VERMELHO}👻 O fantasma {self.nomes[m]} invadiu o terminal de {self.nomes[alvo]} e destruiu: '{item_escolhido}'!{Cores.RESET}")
                pausar(2.0)
            else:
                limpar_tela()
                print(f"{Cores.MAGENTA}{Cores.NEGRITO}>>> TURNO DO FANTASMA: {self.nomes[m]} <<<{Cores.RESET}\n")
                print("Escolha a vítima da sua sabotagem:")
                for idx, s in enumerate(alvos_com_itens):
                    cor_s = PALETA_CORES[s % len(PALETA_CORES)]
                    print(f" [{idx + 1}] {cor_s}{self.nomes[s]}{Cores.RESET} (Possui {len(self.inventarios[s])} itens)")
                print(" [0] Não sabotar ninguém")

                escolha_alvo = input(f"\n{Cores.AMARELO}Vítima > {Cores.RESET}").strip()
                if not escolha_alvo.isdigit() or int(escolha_alvo) <= 0 or int(escolha_alvo) > len(alvos_com_itens):
                    print(f"{Cores.AMARELO}Sabotagem cancelada pelo fantasma.{Cores.RESET}")
                    pausar(1.2)
                    continue

                alvo_idx = alvos_com_itens[int(escolha_alvo) - 1]
                inv_alvo = self.inventarios[alvo_idx]

                print(f"\nEscolha qual item DESTRUIR de {self.nomes[alvo_idx]}:")
                for it_idx, item_nome in enumerate(inv_alvo):
                    print(f" [{it_idx + 1}] {item_nome}")

                escolha_item = input(f"\n{Cores.AMARELO}Item para apagar > {Cores.RESET}").strip()
                if escolha_item.isdigit() and 1 <= int(escolha_item) <= len(inv_alvo):
                    item_removido = inv_alvo.pop(int(escolha_item) - 1)
                    print(f"{Cores.VERMELHO}💥 SUCESSO! O item '{item_removido}' de {self.nomes[alvo_idx]} foi deletado!{Cores.RESET}")
                else:
                    print(f"{Cores.VERMELHO}Seleção inválida. Nenhuma sabotagem foi concluída.{Cores.RESET}")
                pausar(1.8)

    def carregar_arma(self):
        qtd_vivos = len(self.vivos())
        min_balas = max(2, qtd_vivos)
        max_balas = max(3, qtd_vivos + 1)
        vivas = random.randint(min_balas, max_balas)
        neutras = random.randint(min_balas, max_balas)

        self.camara = [True] * vivas + [False] * neutras
        random.shuffle(self.camara)
        self.bot_conhece_proxima = None

        # Fase de sabotagem dos fantasmas antes da distribuição de suprimentos
        self.aplicar_sabotagem_espectral()

        self.cabecalho()
        print(f"{Cores.NEGRITO}>>> RECARREGANDO NÚCLEO MAGNÉTICO <<<{Cores.RESET}")
        print(f"Cargas inseridas: {Cores.VERMELHO}{vivas} VIVAS ⚡{Cores.RESET} | {Cores.CIANO}{neutras} NEUTRAS 💨{Cores.RESET}")
        print(f"Total no tambor: {len(self.camara)} projéteis.\n")

        # Distribui até 2 itens por sobrevivente (respeitando o limite de 6)
        for i in self.vivos():
            for _ in range(2):
                if len(self.inventarios[i]) < self.max_inv:
                    novo_item = random.choice(list(ITENS_DISPONIVEIS.values()))[0]
                    self.inventarios[i].append(novo_item)

        print(f"{Cores.VERDE}Suprimentos entregues aos sobreviventes (Capacidade máxima: {self.max_inv} itens).{Cores.RESET}")
        input(f"\n{Cores.AMARELO}Pressione ENTER para destravar o terminal...{Cores.RESET}")

    def usar_item(self, jogador):
        if not self.inventarios[jogador]:
            print(f"{Cores.VERMELHO}Inventário vazio!{Cores.RESET}")
            pausar(1)
            return

        print(f"\n{Cores.NEGRITO}Selecione o módulo para executar:{Cores.RESET}")
        for idx, item in enumerate(self.inventarios[jogador]):
            desc = next(d for n, d in ITENS_DISPONIVEIS.values() if n == item)
            print(f" [{idx + 1}] {item}: {Cores.CIANO}{desc}{Cores.RESET}")
        print(" [0] Voltar")

        escolha = input(f"{Cores.AMARELO}Item > {Cores.RESET}").strip()
        if not escolha.isdigit() or int(escolha) < 0 or int(escolha) > len(self.inventarios[jogador]):
            print(f"{Cores.VERMELHO}Opção inválida.{Cores.RESET}")
            pausar(1)
            return

        idx = int(escolha)
        if idx == 0:
            return

        item_usado = self.inventarios[jogador].pop(idx - 1)
        self.executar_efeito_item(jogador, item_usado)

    def executar_efeito_item(self, jogador, item_usado, alvo_emp=None):
        cor_j = PALETA_CORES[jogador % len(PALETA_CORES)]
        print(f"\n{cor_j}>>> {self.nomes[jogador]} executou: {item_usado}! <<<{Cores.RESET}")
        pausar(1)

        if item_usado == "Overclock":
            self.dano_acumulado += 1
            print(f"{Cores.VERMELHO}OVERCLOCK ATIVADO! Dano do próximo tiro aumentado para {self.dano_acumulado}!{Cores.RESET}")

        elif item_usado == "Expurgar":
            if not self.camara:
                self.carregar_arma()
            celula = self.camara.pop(0)
            self.bot_conhece_proxima = None
            tipo = f"{Cores.VERMELHO}VIVA ⚡{Cores.RESET}" if celula else f"{Cores.CIANO}NEUTRA 💨{Cores.RESET}"
            print(f"Carga descartada no ar! Ela era: {tipo}!")

        elif item_usado == "Trava EMP":
            oponentes_vivos = [i for i in self.vivos() if i != jogador]
            if not oponentes_vivos:
                return

            if alvo_emp is None:
                print(f"\n{Cores.AMARELO}Selecione o oponente para bloquear com EMP:{Cores.RESET}")
                for n_op, op_idx in enumerate(oponentes_vivos):
                    cor_op = PALETA_CORES[op_idx % len(PALETA_CORES)]
                    print(f" [{n_op + 1}] {cor_op}{self.nomes[op_idx]}{Cores.RESET}")

                sel = input(f"{Cores.AMARELO}Alvo > {Cores.RESET}").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(oponentes_vivos):
                    alvo_emp = oponentes_vivos[int(sel) - 1]
                else:
                    print(f"{Cores.VERMELHO}Seleção inválida. EMP cancelado.{Cores.RESET}")
                    return

            self.emp_ativo[alvo_emp] = True
            print(f"{Cores.VERDE}Pulso EMP disparado! {self.nomes[alvo_emp]} perderá a próxima vez!{Cores.RESET}")

        elif item_usado == "Bateria Reserva":
            if self.hp[jogador] < self.max_hp:
                self.hp[jogador] += 1
                print(f"{Cores.VERDE}+1 de integridade restaurado! (HP: {self.hp[jogador]}){Cores.RESET}")
            else:
                print("HP já está na capacidade máxima.")

        elif item_usado == "Inversor":
            if not self.camara:
                self.carregar_arma()
            self.camara[0] = not self.camara[0]
            print(f"{Cores.CIANO}Polaridade da carga no cano invertida com sucesso!{Cores.RESET}")

        elif item_usado == "Scanner":
            if len(self.camara) < 2:
                print(f"{Cores.AMARELO}Resta apenas 1 carga no tambor! Não há próxima bala antes da recarga.{Cores.RESET}")
                print("O módulo Scanner retornou ao seu inventário.")
                self.inventarios[jogador].append("Scanner")
            else:
                proxima_carga = self.camara[1]
                if not self.is_bot[jogador]:
                    limpar_tela()
                    print(f"{Cores.VERMELHO}{Cores.NEGRITO}ATENÇÃO: Apenas {self.nomes[jogador]} deve olhar a tela agora!{Cores.RESET}")
                    input(f"{Cores.AMARELO}Pressione ENTER quando os outros jogadores não estiverem olhando...{Cores.RESET}")
                    tipo = f"{Cores.VERMELHO}VIVA ⚡{Cores.RESET}" if proxima_carga else f"{Cores.CIANO}NEUTRA 💨{Cores.RESET}"
                    print(f"\n[SCANNER DE TELEMETRIA]: A PRÓXIMA carga (após o tiro atual) é: {tipo}")
                    input(f"\n{Cores.AMARELO}Pressione ENTER para ocultar a telemetria e voltar...{Cores.RESET}")
                    limpar_tela()
                else:
                    self.bot_conhece_proxima = proxima_carga
                    print(f"{Cores.MAGENTA}O bot analisou os sensores da próxima carga em segredo.{Cores.RESET}")

        elif item_usado == "Escudo":
            self.escudo_ativo[jogador] = True
            self.escudo_criado_no_turno[jogador] = True
            print(f"{Cores.CIANO}🛡️ Escudo ativado! Ele protegerá você por 1 rodada (até sua próxima vez de jogar).{Cores.RESET}")

        elif item_usado == "Injetor":
            if not self.camara:
                self.carregar_arma()
            nova_carga = random.choice([True, False])
            pos = random.randint(0, len(self.camara))
            self.camara.insert(pos, nova_carga)
            self.bot_conhece_proxima = None
            print(f"{Cores.MAGENTA}💉 Uma carga desconhecida foi inserida no tambor! (Total atual: {len(self.camara)}){Cores.RESET}")

        pausar(1.8)

    def disparar(self, jogador, alvo_idx):
        if not self.camara:
            self.carregar_arma()

        celula_viva = self.camara.pop(0)
        dano = self.dano_acumulado
        self.dano_acumulado = 1
        self.bot_conhece_proxima = None

        nome_alvo = self.nomes[alvo_idx]
        cor_alvo = PALETA_CORES[alvo_idx % len(PALETA_CORES)]

        print(f"\n{Cores.NEGRITO}Mirando em {cor_alvo}{nome_alvo}{Cores.RESET}{Cores.NEGRITO} e puxando o gatilho...{Cores.RESET}")
        for _ in range(3):
            print(".", end="", flush=True)
            pausar(0.35)
        print()

        if celula_viva:
            print(f"\n{Cores.VERMELHO}{Cores.NEGRITO}💥💥💥 BANG! Carga VIVA disparada! 💥💥💥{Cores.RESET}")
            if self.escudo_ativo[alvo_idx]:
                print(f"{Cores.CIANO}{Cores.NEGRITO}🛡️ O ESCUDO DE {nome_alvo} ABSORVEU TODO O IMPACTO! Dano bloqueado!{Cores.RESET}")
                self.escudo_ativo[alvo_idx] = False
            else:
                print(f"{nome_alvo} recebeu {dano} ponto(s) de dano!")
                self.hp[alvo_idx] = max(0, self.hp[alvo_idx] - dano)

            pausar(1.8)

            if self.hp[alvo_idx] == 0:
                print(f"\n{Cores.VERMELHO}{Cores.NEGRITO}💀 {nome_alvo} FOI ELIMINADO DA PARTIDA! 💀{Cores.RESET}")
                pausar(2)

            return True
        else:
            print(f"\n{Cores.CIANO}{Cores.NEGRITO}💨 *CLICK*... Carga Neutra (Vazio).{Cores.RESET}")
            pausar(1.5)

            if alvo_idx == jogador:
                print(f"{Cores.VERDE}Sorte pura! Atirou em si mesmo e não tomou dano: JOGA NOVAMENTE!{Cores.RESET}")
                pausar(1.8)
                return False
            else:
                print(f"{Cores.AMARELO}Sem efeito no adversário. Vez encerrada.{Cores.RESET}")
                pausar(1.5)
                return True

    def turno_ia(self, bot_idx):
        print(f"{Cores.MAGENTA}🤖 {self.nomes[bot_idx]} está calculando probabilidades de disparo...{Cores.RESET}")
        pausar(1.5)

        itens = list(self.inventarios[bot_idx])

        if "Escudo" in itens and not self.escudo_ativo[bot_idx]:
            self.inventarios[bot_idx].remove("Escudo")
            self.executar_efeito_item(bot_idx, "Escudo")

        if "Bateria Reserva" in itens and self.hp[bot_idx] <= 3:
            self.inventarios[bot_idx].remove("Bateria Reserva")
            self.executar_efeito_item(bot_idx, "Bateria Reserva")

        if "Scanner" in itens and self.bot_conhece_proxima is None and len(self.camara) >= 2:
            self.inventarios[bot_idx].remove("Scanner")
            self.executar_efeito_item(bot_idx, "Scanner")

        if "Trava EMP" in itens:
            oponentes_vivos = [i for i in self.vivos() if i != bot_idx]
            if oponentes_vivos:
                alvo = min(oponentes_vivos, key=lambda x: self.hp[x])
                self.inventarios[bot_idx].remove("Trava EMP")
                self.executar_efeito_item(bot_idx, "Trava EMP", alvo_emp=alvo)

        vivas = sum(1 for c in self.camara if c)
        neutras = len(self.camara) - vivas

        if neutras > vivas and random.random() < 0.65:
            print(f"{Cores.MAGENTA}O bot assume o risco e atira em si mesmo!{Cores.RESET}")
            pausar(1)
            return self.disparar(bot_idx, alvo_idx=bot_idx)
        else:
            oponentes_vivos = [i for i in self.vivos() if i != bot_idx]
            alvo = random.choice(oponentes_vivos)
            print(f"{Cores.MAGENTA}O bot mira em {self.nomes[alvo]}!{Cores.RESET}")
            pausar(1)
            return self.disparar(bot_idx, alvo_idx=alvo)

    def loop(self):
        while len(self.vivos()) > 1:
            if not self.camara:
                self.carregar_arma()

            jogador = self.turno_atual

            if self.hp[jogador] <= 0:
                self.proximo_jogador()
                continue

            # Se o jogador já tinha um escudo ativo de rodadas anteriores, ele se dissipa no início do novo turno
            if self.escudo_ativo[jogador] and not self.escudo_criado_no_turno[jogador]:
                self.escudo_ativo[jogador] = False
                self.cabecalho()
                print(f"{Cores.AMARELO}🛡️ A barreira do seu Escudo se dissipou após completar 1 rodada sem sofrer disparos.{Cores.RESET}")
                pausar(1.8)

            if self.emp_ativo[jogador]:
                self.cabecalho()
                print(f"{Cores.VERMELHO}⚡ SISTEMA BLOQUEADO! {self.nomes[jogador]} está sob choque de EMP e perdeu a vez!{Cores.RESET}")
                self.emp_ativo[jogador] = False
                pausar(2.5)
                self.proximo_jogador()
                continue

            self.cabecalho()
            cor_atual = PALETA_CORES[jogador % len(PALETA_CORES)]
            nome_atual = self.nomes[jogador]

            print(f"Turno atual: {cor_atual}{Cores.NEGRITO}{nome_atual}{Cores.RESET}")
            print(f"Cargas restantes no núcleo: {len(self.camara)}\n")

            if self.is_bot[jogador]:
                passar_vez = self.turno_ia(jogador)
                if passar_vez:
                    self.proximo_jogador()
                continue

            print(" [1] Atirar em Si Mesmo (Tiro Neutro concede turno extra)")
            print(" [2] Escolher um Oponente para Atirar")
            print(" [3] Usar Item do Inventário")

            escolha = input(f"\n{Cores.AMARELO}Ação de {nome_atual} > {Cores.RESET}").strip()

            if escolha == "1":
                passar_vez = self.disparar(jogador, alvo_idx=jogador)
                if passar_vez:
                    self.proximo_jogador()

            elif escolha == "2":
                oponentes_vivos = [i for i in self.vivos() if i != jogador]
                print(f"\n{Cores.NEGRITO}Escolha o alvo do disparo:{Cores.RESET}")
                for idx_op, op in enumerate(oponentes_vivos):
                    cor_op = PALETA_CORES[op % len(PALETA_CORES)]
                    print(f" [{idx_op + 1}] {cor_op}{self.nomes[op]}{Cores.RESET} (HP: {self.hp[op]})")
                print(" [0] Cancelar e voltar")

                sel_alvo = input(f"{Cores.AMARELO}Alvo > {Cores.RESET}").strip()
                if sel_alvo.isdigit():
                    num = int(sel_alvo)
                    if num == 0:
                        continue
                    elif 1 <= num <= len(oponentes_vivos):
                        alvo_escolhido = oponentes_vivos[num - 1]
                        passar_vez = self.disparar(jogador, alvo_idx=alvo_escolhido)
                        if passar_vez:
                            self.proximo_jogador()
                    else:
                        print(f"{Cores.VERMELHO}Alvo inexistente.{Cores.RESET}")
                        pausar(1)
                else:
                    print(f"{Cores.VERMELHO}Entrada inválida.{Cores.RESET}")
                    pausar(1)

            elif escolha == "3":
                self.usar_item(jogador)
            else:
                print(f"{Cores.VERMELHO}Comando inválido.{Cores.RESET}")
                pausar(0.8)

        # Fim de partida
        self.cabecalho()
        vencedor_idx = self.vivos()[0]
        vencedor_nome = self.nomes[vencedor_idx]
        cor_venc = PALETA_CORES[vencedor_idx % len(PALETA_CORES)]

        print(f"{Cores.VERDE}{Cores.NEGRITO}========================================================================{Cores.RESET}")
        print(f"          VITÓRIA ABSOLUTA DE: {cor_venc}{vencedor_nome.upper()}{Cores.VERDE}! O ÚLTIMO SOBREVIVENTE!          {Cores.RESET}")
        print(f"{Cores.VERDE}{Cores.NEGRITO}========================================================================{Cores.RESET}\n")

def menu_inicial():
    limpar_tela()
    print(f"{Cores.CIANO}{Cores.NEGRITO}===================================================={Cores.RESET}")
    print(f"{Cores.MAGENTA}{Cores.NEGRITO}           CONFIGURAÇÃO DA SALA DE COMBATE          {Cores.RESET}")
    print(f"{Cores.CIANO}{Cores.NEGRITO}===================================================={Cores.RESET}\n")

    while True:
        qtd_str = input(f"{Cores.AMARELO}Quantos players irão jogar? (1 a 6) > {Cores.RESET}").strip()
        if qtd_str.isdigit() and 1 <= int(qtd_str) <= 6:
            qtd = int(qtd_str)
            break
        print(f"{Cores.VERMELHO}Escolha um número válido entre 1 e 6.{Cores.RESET}")

    nomes = []
    is_bot = []

    if qtd == 1:
        nome_p1 = input(f"\n{Cores.CIANO}Digite seu nome (Padrão: Claudio): {Cores.RESET}").strip()
        if not nome_p1:
            nome_p1 = "Claudio"
        nomes = [nome_p1, "CYBER-BOT"]
        is_bot = [False, True]
        print(f"\n{Cores.VERDE}Modo Solo ativado! Você enfrentará a IA CYBER-BOT.{Cores.RESET}")
        pausar(1.5)
    else:
        padroes = ["Claudio", "Major", "Augusto", "Player 4", "Player 5", "Player 6"]
        print(f"\n{Cores.CIANO}--- Digite o nome dos jogadores ---{Cores.RESET}")
        for i in range(qtd):
            padrao = padroes[i]
            nome = input(f"Jogador {i + 1} (Padrão '{padrao}'): ").strip()
            if not nome:
                nome = padrao
            nomes.append(nome)
            is_bot.append(False)

    return JogoDueloMultiplayer(nomes=nomes, is_bot=is_bot)

if __name__ == "__main__":
    jogo = menu_inicial()
    jogo.loop()