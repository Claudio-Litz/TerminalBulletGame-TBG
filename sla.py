import os
import random
import time

C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_RED = "\033[91m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_BLUE = "\033[94m"
C_MAGENTA = "\033[95m"
C_CYAN = "\033[96m"

# Tabela de Faces com Pesos Estatísticos
FACES_INFO = {
    "PONTO":   {"nome": "⭐ PONTO",   "cor": C_CYAN,    "peso": 5},  # Mais comum: acelera o objetivo de 20 PV
    "ESCUDO":  {"nome": "🛡️ ESCUDO",  "cor": C_BLUE,    "peso": 4},  # Reduz a letalidade rápida
    "CURA":    {"nome": "💚 CURA",    "cor": C_GREEN,   "peso": 4},
    "CREDITO": {"nome": "⚡ CRÉDITO", "cor": C_YELLOW,  "peso": 6},
    "DANO":    {"nome": "⚔️ DANO",    "cor": C_RED,     "peso": 4},  # Combate consistente, mas controlado
    "CRITICO": {"nome": "💥 CRÍTICO", "cor": C_MAGENTA, "peso": 1}   # Raro (~4,3% de chance por dado)
}

FACES_CHAVES = list(FACES_INFO.keys())
FACES_PESOS = [FACES_INFO[k]["peso"] for k in FACES_CHAVES]

LOJA = {
    "1": {"nome": "Bandagem Rápida", "custo": 2, "tipo": "consumivel", "desc": "Cura 3 de vida imediatamente."},
    "2": {"nome": "Bateria Reserva", "custo": 2, "tipo": "consumivel", "desc": "Ganha +1 PV e +2 de Escudo neste turno."},
    "3": {"nome": "Blindagem Pesada", "custo": 4, "tipo": "passiva", "desc": "Recebe +1🛡️ de Escudo grátis no início de todo turno."},
    "4": {"nome": "Espinhos Reativos", "custo": 4, "tipo": "passiva", "desc": "Quem te atacar toma 1 de dano de volta."},
    "5": {"nome": "Lâmina Reforçada", "custo": 5, "tipo": "passiva", "desc": "Seus dados de DANO causam +1 de dano extra cada."},
    "6": {"nome": "Nano-Regeneração", "custo": 5, "tipo": "passiva", "desc": "Permite usar dados de CURA mesmo dentro da Jaula."},
    "7": {"nome": "Míssil Teleguiado", "custo": 6, "tipo": "arma", "desc": "[Uso Único] Dispara 3 de dano perfurante em qualquer alvo."}
}

def limpar():
    os.system("cls" if os.name == "nt" else "clear")

def pausar(s=1.2):
    time.sleep(s)

def rolar_dado_ponderado():
    return random.choices(FACES_CHAVES, weights=FACES_PESOS, k=1)[0]

class Jogador:
    def __init__(self, nome):
        self.nome = nome
        self.vida = 16
        self.max_vida = 16
        self.pontos = 0
        self.creditos = 0
        self.escudo = 0
        self.upgrades = set()
        self.misseis = 0

    def vivo(self):
        return self.vida > 0

class Arena:
    def __init__(self, nomes):
        self.jogadores = [Jogador(n) for n in nomes]
        self.rei = None
        self.turno_idx = 0

    def jogadores_vivos(self):
        return [j for j in self.jogadores if j.vivo()]

    def desenhar_mesa(self, jogador_atual=None):
        limpar()
        rei_nome = f"{C_RED}{C_BOLD}[ {self.rei.nome} ]{C_RESET}" if self.rei else f"{C_YELLOW}[ VAZIA ]{C_RESET}"
        
        print(f"{C_BOLD}{C_MAGENTA}==================== ARENA: REI DA JAULA ===================={C_RESET}")
        print(f"  CONTROLE DA JAULA: {rei_nome} (+2 PV por rodada | Alvo de todos)")
        print("-------------------------------------------------------------")
        
        for j in self.jogadores:
            if not j.vivo():
                print(f"💀 {C_RED}{j.nome:<12} | ELIMINADO DA PARTIDA{C_RESET}")
                continue

            marcador = f"{C_YELLOW}▶{C_RESET}" if j == jogador_atual else " "
            local = f"{C_RED}[NA JAULA]{C_RESET}" if j == self.rei else f"{C_GREEN}[FORA]{C_RESET}"
            
            bar_hp = f"{C_RED}{'█' * j.vida}{C_RESET}{'░' * (j.max_vida - j.vida)}"
            status = f"{marcador} {C_BOLD}{j.nome:<12}{C_RESET} {local} | HP: [{bar_hp}] {j.vida}/{j.max_vida}"
            if j.escudo > 0:
                status += f" {C_BLUE}[🛡️+{j.escudo}]{C_RESET}"
            print(status)
            print(f"   Progresso: {C_CYAN}{j.pontos:02d}/20 PV{C_RESET} | Banco: {C_YELLOW}{j.creditos}⚡{C_RESET}")
            
            melhorias = [LOJA[u]["nome"] for u in j.upgrades]
            if j.misseis > 0:
                melhorias.append(f"Míssil x{j.misseis}")
            if melhorias:
                print(f"   Equipamentos: {C_MAGENTA}{', '.join(melhorias)}{C_RESET}")
        print(f"{C_BOLD}{C_MAGENTA}============================================================={C_RESET}\n")

    def rolar_dados(self, jogador):
        dados = [rolar_dado_ponderado() for _ in range(6)]
        rerolls_restantes = 2

        while rerolls_restantes > 0:
            self.desenhar_mesa(jogador)
            print(f"Turno de {C_BOLD}{C_YELLOW}{jogador.nome}{C_RESET} | Rerolagens restantes: {rerolls_restantes}")
            print("\nSeus Dados:")
            for idx, d in enumerate(dados, 1):
                info = FACES_INFO[d]
                print(f"  [{idx}] {info['cor']}{info['nome']}{C_RESET}")

            print("\nDigite os números dos dados para REROLAR (Ex: '1 2 5', 'todos', ou '0' para manter):")
            escolha = input("> ").strip().lower()

            if escolha in ["0", "", "travar", "manter", "nenhum"]:
                break
            
            if escolha in ["todos", "all"]:
                dados = [rolar_dado_ponderado() for _ in range(6)]
                rerolls_restantes -= 1
                continue

            indices = []
            for part in escolha.replace(",", " ").split():
                if part.isdigit() and 1 <= int(part) <= 6:
                    indices.append(int(part) - 1)

            if indices:
                for idx in set(indices):
                    dados[idx] = rolar_dado_ponderado()
                rerolls_restantes -= 1
            else:
                print("Entrada inválida.")
                pausar(0.8)

        return dados

    def aplicar_dano(self, alvo, atacante, dano, critico=False):
        if not alvo.vivo():
            return

        dano_real = dano
        if not critico and alvo.escudo > 0:
            bloqueado = min(alvo.escudo, dano_real)
            alvo.escudo -= bloqueado
            dano_real -= bloqueado
            print(f"🛡️ O escudo de {alvo.nome} absorveu {bloqueado} de dano!")

        if dano_real > 0:
            alvo.vida = max(0, alvo.vida - dano_real)
            tipo_txt = f"{C_MAGENTA}CRÍTICO PERFURANTE{C_RESET}" if critico else "dano"
            print(f"💥 {C_RED}{alvo.nome} sofreu {dano_real} de {tipo_txt}! (HP: {alvo.vida}/{alvo.max_vida}){C_RESET}")

            # Espinhos Reativos
            if "4" in alvo.upgrades and atacante != alvo and atacante.vivo():
                atacante.vida = max(0, atacante.vida - 1)
                print(f"🌵 Espinhos de {alvo.nome} devolveram 1 de dano a {atacante.nome}!")

        if not alvo.vivo():
            print(f"\n{C_RED}{C_BOLD}💀 {alvo.nome} FOI ELIMINADO DA ARENA!{C_RESET}")
            if self.rei == alvo:
                self.rei = None

    def fase_mercado(self, jogador):
        while True:
            self.desenhar_mesa(jogador)
            print(f"Mercado Tático - Vez de {C_BOLD}{C_YELLOW}{jogador.nome}{C_RESET} | Saldo: {C_YELLOW}{jogador.creditos}⚡{C_RESET}")
            print("Itens:")
            for k, item in LOJA.items():
                tem = " [Adquirido]" if (k in jogador.upgrades and item["tipo"] == "passiva") else ""
                print(f"  [{k}] {item['nome']} ({item['custo']}⚡){tem} -> {item['desc']}")
            print("  [0] Finalizar Turno")
            if jogador.misseis > 0:
                print("  [M] Disparar Míssil Teleguiado")

            esc = input("\nEscolha uma opção: ").strip().lower()
            if esc == "0":
                break

            if esc == "m" and jogador.misseis > 0:
                alvos = [j for j in self.jogadores_vivos() if j != jogador]
                print("\nDisparar contra qual alvo?")
                for idx, alv in enumerate(alvos, 1):
                    print(f"  [{idx}] {alv.nome} (HP: {alv.vida})")
                escolha_alvo = input("> ").strip()
                if escolha_alvo.isdigit() and 1 <= int(escolha_alvo) <= len(alvos):
                    vitima = alvos[int(escolha_alvo) - 1]
                    jogador.misseis -= 1
                    print(f"\n🚀 {C_RED}{jogador.nome} disparou um míssil teleguiado em {vitima.nome}!{C_RESET}")
                    self.aplicar_dano(vitima, jogador, 3, critico=True)
                    pausar(2.0)
                continue

            if esc in LOJA:
                item = LOJA[esc]
                if item["tipo"] == "passiva" and esc in jogador.upgrades:
                    print("Você já possui esta melhoria ativa.")
                    pausar(1.0)
                    continue

                if jogador.creditos >= item["custo"]:
                    jogador.creditos -= item["custo"]
                    if esc == "1":  # Bandagem
                        jogador.vida = min(jogador.max_vida, jogador.vida + 3)
                        print(f"{C_GREEN}+3 HP recuperados!{C_RESET}")
                    elif esc == "2":  # Bateria Reserva
                        jogador.pontos += 1
                        jogador.escudo += 2
                        print(f"{C_CYAN}+1 PV e +2 Escudos adicionados!{C_RESET}")
                    elif esc == "7":  # Míssil
                        jogador.misseis += 1
                        print(f"{C_MAGENTA}Míssil estocado no inventário!{C_RESET}")
                    else:
                        jogador.upgrades.add(esc)
                        print(f"{C_GREEN}Melhoria instalada com sucesso!{C_RESET}")
                    pausar(1.3)
                else:
                    print(f"{C_RED}Créditos insuficientes.{C_RESET}")
                    pausar(1.0)

    def executar_turno(self):
        jogador = self.jogadores[self.turno_idx]
        if not jogador.vivo():
            self.turno_idx = (self.turno_idx + 1) % len(self.jogadores)
            return

        # Reseta escudos temporários do turno anterior
        jogador.escudo = 0

        # Passiva: Blindagem Pesada
        if "3" in jogador.upgrades:
            jogador.escudo += 1
            print(f"🛡️ Blindagem Pesada concedeu +1 Escudo base a {jogador.nome}.")

        # Bônus por começar o turno na Jaula
        if self.rei == jogador:
            jogador.pontos += 2
            self.desenhar_mesa(jogador)
            print(f"{C_YELLOW}👑 {jogador.nome} manteve o domínio da Jaula Central! (+2 PV garantidos){C_RESET}")
            pausar(1.5)

        # 1. Rolagem e Rerolagem de Dados
        dados_finais = self.rolar_dados(jogador)
        self.desenhar_mesa(jogador)

        print(f"\nDados Consolidados de {C_BOLD}{jogador.nome}{C_RESET}:")
        contagem = {k: 0 for k in FACES_CHAVES}
        for d in dados_finais:
            contagem[d] += 1
            info = FACES_INFO[d]
            print(f"  {info['cor']}{info['nome']}{C_RESET}")
        pausar(1.5)

        # 2. Resolução de Recursos
        # Pontos de Vitória
        if contagem["PONTO"] > 0:
            ganho_pv = contagem["PONTO"]
            if contagem["PONTO"] >= 3:
                ganho_pv += 1
                print(f"{C_CYAN}⭐ Combo de Pontos! +{contagem['PONTO']} PV base + 1 PV BÔNUS!{C_RESET}")
            else:
                print(f"⭐ +{ganho_pv} Ponto(s) de Vitória!")
            jogador.pontos += ganho_pv

        # Créditos
        if contagem["CREDITO"] > 0:
            jogador.creditos += contagem["CREDITO"]
            print(f"⚡ +{contagem['CREDITO']} Crédito(s) adquiridos!")

        # Escudos
        if contagem["ESCUDO"] > 0:
            jogador.escudo += contagem["ESCUDO"]
            print(f"🛡️ +{contagem['ESCUDO']} de Escudo ativo!")

        # Cura
        if contagem["CURA"] > 0:
            if self.rei == jogador and "6" not in jogador.upgrades:
                print(f"{C_RED}🚫 A Jaula suprime a regeneração natural! (Requer Nano-Regeneração){C_RESET}")
            else:
                curado = min(jogador.max_vida - jogador.vida, contagem["CURA"])
                jogador.vida += curado
                print(f"💚 Recuperou {curado} de vida! (HP: {jogador.vida}/{jogador.max_vida})")

        pausar(1.5)

        # 3. Resolução de Ataques
        mult_dano = 2 if "5" in jogador.upgrades else 1
        dano_normal = contagem["DANO"] * mult_dano
        dano_critico = contagem["CRITICO"] * 2  # Crítico perfura escudo
        total_dano = dano_normal + dano_critico

        if total_dano > 0:
            print(f"\n{C_RED}{C_BOLD}⚔️ PODER OFENSIVO GERADO: {total_dano} (Normal: {dano_normal} | Perfurante: {dano_critico}){C_RESET}")
            pausar(1.2)

            if self.rei == jogador:
                # O ocupante da Jaula ataca TODOS que estão fora
                print(f"🌋 {jogador.nome} dispara uma onde de choque da Jaula em TODOS os oponentes!")
                for alvo in self.jogadores_vivos():
                    if alvo != jogador:
                        self.aplicar_dano(alvo, jogador, dano_normal, critico=False)
                        if dano_critico > 0 and alvo.vivo():
                            self.aplicar_dano(alvo, jogador, dano_critico, critico=True)
                pausar(2.0)
            else:
                # O atacante de fora golpeia quem estiver na Jaula
                if self.rei is not None and self.rei.vivo():
                    alvo = self.rei
                    print(f"🎯 Ataque direcionado a {alvo.nome} no interior da Jaula!")
                    self.aplicar_dano(alvo, jogador, dano_normal, critico=False)
                    if dano_critico > 0 and alvo.vivo():
                        self.aplicar_dano(alvo, jogador, dano_critico, critico=True)
                    pausar(1.5)

                    # Se sobreviveu, o Rei tem a opção de bater em retirada
                    if alvo.vivo():
                        self.desenhar_mesa()
                        print(f"{C_YELLOW}Atenção {alvo.nome}:{C_RESET} Você foi atingido na Jaula.")
                        print(f"Deseja FUGIR da Jaula para preservar seu HP e ceder o posto a {jogador.nome}? (s/N)")
                        fuga = input("> ").strip().lower()
                        if fuga == "s":
                            print(f"{C_GREEN}🏃 {alvo.nome} recuou para fora! {jogador.nome} reivindica o centro!{C_RESET}")
                            self.rei = jogador
                            jogador.pontos += 1
                            pausar(1.5)
                    else:
                        print(f"{C_YELLOW}A Jaula ficou desimpedida! {jogador.nome} assume a posição central!{C_RESET}")
                        self.rei = jogador
                        jogador.pontos += 1
                        pausar(1.5)
                else:
                    # Jaula vazia ocupada pelo atacante
                    print(f"{C_YELLOW}A Jaula estava vazia! {jogador.nome} assumiu o trono central (+1 PV)!{C_RESET}")
                    self.rei = jogador
                    jogador.pontos += 1
                    pausar(1.5)

        # Entrada voluntária se a jaula estiver vazia e não houve ataque
        if self.rei is None and jogador.vivo():
            self.desenhar_mesa(jogador)
            print("A Jaula Central encontra-se vazia.")
            print("Deseja OCUPAR a Jaula agora para acelerar seus PV? (s/N)")
            entrar = input("> ").strip().lower()
            if entrar == "s":
                self.rei = jogador
                jogador.pontos += 1
                print(f"{C_GREEN}{jogador.nome} ocupou a Jaula (+1 PV)!{C_RESET}")
                pausar(1.2)

        # 4. Mercado
        if jogador.vivo() and len(self.jogadores_vivos()) > 1:
            self.fase_mercado(jogador)

        self.turno_idx = (self.turno_idx + 1) % len(self.jogadores)

    def checar_vencedor(self):
        vivos = self.jogadores_vivos()
        if len(vivos) == 1:
            return vivos[0], "eliminou todos os adversários e permaneceu de pé"

        # Vitória por PV
        concorrentes_pv = [j for j in vivos if j.pontos >= 20]
        if concorrentes_pv:
            # Caso mais de um atinja na mesma rodada, vence quem acumulou mais
            melhor = max(concorrentes_pv, key=lambda x: x.pontos)
            return melhor, f"atingiu a marca de {melhor.pontos} Pontos de Vitória"

        return None, None

    def iniciar(self):
        while True:
            vencedor, motivo = self.checar_vencedor()
            if vencedor:
                limpar()
                print(f"{C_GREEN}{C_BOLD}" + "=" * 60)
                print(f"       🏆 VITÓRIA CONSAGRADA: {vencedor.nome.upper()}! 🏆")
                print(f"       Motivo: {vencedor.nome} {motivo}!")
                print("=" * 60 + f"{C_RESET}\n")
                break

            self.executar_turno()

def configurar_partida():
    limpar()
    print(f"{C_BOLD}{C_MAGENTA}=== ARENA: REI DA JAULA [EDIÇÃO EQUILIBRADA] ==={C_RESET}\n")
    
    # Seleção de quantidade de jogadores
    while True:
        qtd_str = input("Quantos jogadores vão participar? (2 a 6) [Padrão: 3]: ").strip()
        if not qtd_str:
            qtd = 3
            break
        if qtd_str.isdigit() and 2 <= int(qtd_str) <= 6:
            qtd = int(qtd_str)
            break
        print(f"{C_RED}Por favor, informe um número válido entre 2 e 6.{C_RESET}")

    nomes_sugeridos = ["Major", "Gabriel", "Claudio", "Jogador 4", "Jogador 5", "Jogador 6"]
    nomes = []
    print("\nDefinição dos Nomes (Pressione ENTER para aceitar o nome sugerido):")
    for i in range(qtd):
        sugestao = nomes_sugeridos[i]
        nome = input(f"Nome do Jogador {i + 1} [{sugestao}]: ").strip()
        nomes.append(nome if nome else sugestao)

    return nomes

if __name__ == "__main__":
    nomes_jogadores = configurar_partida()
    arena = Arena(nomes_jogadores)
    arena.iniciar()